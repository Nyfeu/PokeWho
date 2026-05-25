import yaml
import random

# MOTOR DE INFERÊNCIA - SISTEMA ESPECIALISTA EVENT-DRIVEN
# Funcionamento:
# 1. Carrega base de conhecimento (perguntas e regras de inferência)
# 2. Formula perguntas ao usuário 
# 3. Registra respostas e deduz novos fatos
# 4. Utiliza exclusão mútua entre atributos da mesma categoria
# 5. Realiza encadeamento progressivo de regras até atingir diagnóstico
# 6. Aplica dedução por eliminação quando apenas uma hipótese resta viável

class MotorInferenciaEventDriven:
    def __init__(self, caminho_yaml):
        # INICIALIZAÇÃO: Carrega conhecimento do arquivo YAML
        with open(caminho_yaml, 'r', encoding='utf-8') as f:
            conhecimento = yaml.safe_load(f)
            
        # Armazena perguntas (fato -> texto da pergunta)
        self.perguntas = conhecimento['perguntas']
        # Armazena regras de inferência (se [premissas] entao [conclusão])
        self.regras = conhecimento['regras']
        
        # MEMÓRIA DE FATOS: Armazena fatos confirmados (respostas afirmativas)
        self.fatos = set()
        # MEMÓRIA NEGATIVA: Armazena fatos refutados (respostas negativas)
        self.fatos_negados = set() 
        # Armazena diagnósticos alcançados pela inferência
        self.diagnosticos = []
        
        # AGENDA: Cria fila de perguntas embaralhada
        # Embaralhamento evita viés posicional dos cartões do tabuleiro
        self.fila_perguntas = list(self.perguntas.items())
        random.shuffle(self.fila_perguntas)

    def _regras_viaveis(self):
        # FILTRAGEM DE REGRAS: Retorna apenas regras ainda aplicáveis
        # Uma regra é INVIÁVEL se uma de suas premissas foi refutada
        viaveis = []
        for regra in self.regras:
            premissas = set(regra['se'])
            # Verifica se alguma premissa está em fatos_negados
            # Se não há intersecção = regra ainda pode ser ativada
            if not premissas.intersection(self.fatos_negados):
                viaveis.append(regra)
        return viaveis

    def obter_proxima_pergunta(self):
        # SELEÇÃO INTELIGENTE DE PERGUNTAS
        # Estratégia: Fazer perguntas que afetam regras ativas
        
        # 1. Identifica quais regras ainda podem ser aplicadas
        regras_ativas = self._regras_viaveis()
        
        # 2. Extrai todas as premissas das regras ativas
        # Essas premissas são "úteis" - responder sobre elas pode inferir conclusões
        premissas_uteis = set()
        for r in regras_ativas:
            premissas_uteis.update(r['se'])

        # 3. Busca próxima pergunta sobre um fato útil que ainda não foi respondido
        while self.fila_perguntas and not self.diagnosticos:
            fato, texto = self.fila_perguntas.pop(0)
            
            # Pula se já foi respondido (positiva ou negativamente)
            if fato in self.fatos or fato in self.fatos_negados:
                continue
            
            # Prioriza perguntas sobre premissas de regras ativas
            if fato in premissas_uteis:
                return fato, texto
        
        # Se nenhuma pergunta útil restante, retorna None
        return None, None

    def registrar_resposta(self, fato, resposta_afirmativa):
        # PROCESSAMENTO DE RESPOSTA DO USUÁRIO
        
        if resposta_afirmativa:
            # Usuário confirmou o fato: Adiciona aos fatos conhecidos
            self.fatos.add(fato)
            
            # EXCLUSÃO MÚTUA: Implementa constraint que atributos da mesma categoria
            # são mutuamente exclusivos (ex: cor_verde + cor_vermelho não podem coexistir)
            categoria = fato.split("_")[0]
            for regra in self.regras:
                for premissa in regra['se']:
                    # Identifica outras premissas da mesma categoria
                    if premissa.startswith(categoria + "_") and premissa != fato:
                        # Marca como refutadas (exclusão mútua)
                        self.fatos_negados.add(premissa)
        else:
            # Usuário negou o fato: Adiciona aos fatos negados
            self.fatos_negados.add(fato)
        
        # Após registrar resposta, tenta inferir novas conclusões
        self._inferir()

    def _inferir(self):
        # MECANISMO DE ENCADEAMENTO PROGRESSIVO (Forward Chaining)
        # Aplica regras repetidamente até não haver mais fatos a inferir
        
        novos_fatos = True
        while novos_fatos:
            novos_fatos = False
            # Itera sobre todas as regras ainda viáveis
            for regra in self._regras_viaveis():
                premissas = set(regra['se'])
                conseq = regra['entao']
                
                # Verifica se TODAS as premissas da regra foram confirmadas
                # E se a conclusão ainda não foi derivada
                if premissas.issubset(self.fatos) and conseq not in self.fatos and conseq not in self.diagnosticos:
                    # Diferencia entre conclusões intermediárias e diagnósticos finais
                    if str(conseq).lower().startswith("diagnóstico"):
                        # Diagnóstico foi alcançado: Termina o processo
                        self.diagnosticos.append(conseq)
                    else:
                        # Fato intermediário: Adiciona à base de conhecimento
                        self.fatos.add(conseq)
                        novos_fatos = True  # Pode disparar novas regras
        
        # DEDUÇÃO POR ELIMINAÇÃO: Aplicada após encadeamento completo
        # Se apenas uma regra permanece viável e não há diagnóstico,
        # conclui-se que sua conclusão é inevitável
        regras_ativas = self._regras_viaveis()
        if len(regras_ativas) == 1 and not self.diagnosticos:
            conseq = regras_ativas[0]['entao']
            # Marca como dedução lógica para rastreabilidade
            self.diagnosticos.append(f"{conseq} (Dedução Lógica por Eliminação)")