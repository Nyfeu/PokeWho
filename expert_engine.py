import yaml
import random

class MotorInferenciaEventDriven:
    def __init__(self, caminho_yaml):
        with open(caminho_yaml, 'r', encoding='utf-8') as f:
            conhecimento = yaml.safe_load(f)
            
        self.perguntas = conhecimento['perguntas']
        self.regras = conhecimento['regras']
        
        # Base de Dados Lógica
        self.fatos = set()
        self.fatos_negados = set() 
        
        self.diagnosticos = []
        
        self.fila_perguntas = list(self.perguntas.items())
        random.shuffle(self.fila_perguntas)

    def _regras_viaveis(self):
        """ Retorna apenas regras que matematicamente ainda podem ser verdadeiras. """
        viaveis = []
        for regra in self.regras:
            premissas = set(regra['se'])
            if not premissas.intersection(self.fatos_negados):
                viaveis.append(regra)
        return viaveis

    def obter_proxima_pergunta(self):
        # Transforma-se apenas em um "getter" (Busca apenas perguntas, não tira conclusões)
        regras_ativas = self._regras_viaveis()
        premissas_uteis = set()
        for r in regras_ativas:
            premissas_uteis.update(r['se'])

        while self.fila_perguntas and not self.diagnosticos:
            fato, texto = self.fila_perguntas.pop(0)
            
            # Pula a pergunta se a Lógica de Exclusão já definiu a resposta
            if fato in self.fatos or fato in self.fatos_negados:
                continue
                
            # Só pergunta se for útil para as regras ativas
            if fato in premissas_uteis:
                return fato, texto
                
        return None, None

    def registrar_resposta(self, fato, resposta_afirmativa):
        if resposta_afirmativa:
            self.fatos.add(fato)
            
            # --- EXCLUSÃO MÚTUA (Atributos Monovalorados) ---
            categoria = fato.split("_")[0]
            
            for regra in self.regras:
                for premissa in regra['se']:
                    if premissa.startswith(categoria + "_") and premissa != fato:
                        self.fatos_negados.add(premissa)
        else:
            self.fatos_negados.add(fato)
            
        self._inferir()

    def _inferir(self):
        # 1. Encadeamento Progressivo Clássico
        novos_fatos = True
        while novos_fatos:
            novos_fatos = False
            
            for regra in self._regras_viaveis():
                premissas = set(regra['se'])
                conseq = regra['entao']
                
                if premissas.issubset(self.fatos) and conseq not in self.fatos and conseq not in self.diagnosticos:
                    if str(conseq).lower().startswith("diagnóstico"):
                        self.diagnosticos.append(conseq)
                    else:
                        self.fatos.add(conseq)
                        novos_fatos = True
                        
        # 2. Avalia a Dedução Lógica por Exclusão AGORA!
        regras_ativas = self._regras_viaveis()
        if len(regras_ativas) == 1 and not self.diagnosticos:
            conseq = regras_ativas[0]['entao']
            self.diagnosticos.append(f"{conseq} (Dedução Lógica por Eliminação)")