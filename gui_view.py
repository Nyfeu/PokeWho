import sys
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                             QTextEdit, QFrame, QDialog, QComboBox, QGraphicsOpacityEffect,
                             QGraphicsDropShadowEffect)
from PyQt6.QtGui import QPixmap, QFont, QColor, QTextCursor
from PyQt6.QtCore import Qt, QTimer

# --- ESTILOS GERAIS (TEMA POKÉDEX VERMELHA) ---
STYLESHEET = """
    QMainWindow { 
        background-color: #DC0A2D; /* Vermelho Clássico da Pokédex */
    }
    
    /* Decorações do Topo (LEDs) */
    QFrame#LenteAzul {
        background-color: qradialgradient(cx:0.3, cy:0.3, radius: 1, fx:0.3, fy:0.3, stop:0 #93C5FD, stop:1 #1E3A8A);
        border-radius: 30px;
        border: 4px solid #E2E8F0;
    }
    QFrame#LedVermelho { 
        background-color: qradialgradient(cx:0.3, cy:0.3, radius: 1, fx:0.3, fy:0.3, stop:0 #FCA5A5, stop:1 #991B1B); 
        border-radius: 8px; border: 1px solid #7F1D1D; 
    }
    QFrame#LedAmarelo { 
        background-color: qradialgradient(cx:0.3, cy:0.3, radius: 1, fx:0.3, fy:0.3, stop:0 #FDE047, stop:1 #B45309); 
        border-radius: 8px; border: 1px solid #78350F; 
    }
    QFrame#LedVerde { 
        background-color: qradialgradient(cx:0.3, cy:0.3, radius: 1, fx:0.3, fy:0.3, stop:0 #6EE7B7, stop:1 #065F46); 
        border-radius: 8px; border: 1px solid #064E3B; 
    }
    
    /* Tela Esquerda (Grid) */
    QFrame#GridScreen {
        background-color: #111827;
        border-radius: 10px;
        border: 15px solid #E5E7EB; /* Borda cinza/branca da tela */
        border-bottom: 30px solid #E5E7EB;
    }
    
    /* Cartas no Grid */
    QFrame#Card {
        background-color: #1F2937;
        border-radius: 8px;
        border: 2px solid #374151;
    }
    QFrame#Card:hover {
        border: 2px solid #FBBF24;
        background-color: #374151;
    }
    QLabel { color: #F8FAFC; } /* Texto branco nas cartas */

    /* Painel Direito (Controles) */
    QFrame#Panel {
        background-color: #DC0A2D; /* Fundo vermelho */
        border-left: 4px solid #991B1B; /* Vinco da dobradiça */
    }
    
    QFrame#Panel QLabel.LabelEscura { color: #111827; } /* Títulos escuros */
    
    /* HUD do Alvo */
    QFrame#HudAlvo {
        background-color: #111827;
        border-radius: 8px;
        border: 4px solid #E5E7EB;
    }
    QFrame#HudAlvo QLabel { color: #4ADE80; font-family: Consolas; } /* Letra verde terminal */

    /* Terminal de Inferência */
    QTextEdit {
        background-color: #064E3B; /* Fundo verde escuro tipo GameBoy/Retro */
        color: #A7F3D0; /* Letra verde clara */
        border: 4px solid #E5E7EB;
        border-radius: 5px;
        padding: 5px;
        font-family: Consolas;
        font-size: 13px;
    }
    
    /* Botões */
    QPushButton {
        border-radius: 8px;
        font-weight: bold;
        font-size: 16px;
        color: white;
        border: 2px solid #111827;
    }
    QPushButton#BtnSim { background-color: #10B981; }
    QPushButton#BtnSim:hover { background-color: #059669; }
    
    QPushButton#BtnNao { background-color: #EF4444; }
    QPushButton#BtnNao:hover { background-color: #DC2626; }
    
    QPushButton#BtnReiniciar { background-color: #3B82F6; }
    QPushButton#BtnReiniciar:hover { background-color: #2563EB; }
    
    /* ESTILIZAÇÃO DA BARRA DE ROLAGEM DO TERMINAL */
    QScrollBar:vertical {
        border: none;
        background: #064E3B; /* Fundo verde escuro igual ao terminal */
        width: 14px;
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:vertical {
        background: #10B981; /* Verde neon */
        min-height: 30px;
        border-radius: 7px;
    }
    QScrollBar::handle:vertical:hover {
        background: #34D399; /* Brilha ao passar o mouse */
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
        height: 0px; /* Esconde as setinhas feias de cima e de baixo */
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
"""

class DialogoAlvo(QDialog):
    def __init__(self, parent, pokemons):
        super().__init__(parent)
        self.setWindowTitle("Definir Alvo")
        self.setFixedSize(350, 180)
        self.setStyleSheet("background-color: #111827; color: white;")
        
        layout = QVBoxLayout(self)
        lbl = QLabel("Selecione o Pokémon a ser diagnosticado:")
        lbl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.combo = QComboBox()
        self.combo.setStyleSheet("background-color: #1F2937; padding: 5px; border-radius: 5px;")
        self.combo.addItems([p['nome'] for p in pokemons])
        layout.addWidget(self.combo)
        
        btn_confirmar = QPushButton("Iniciar Diagnóstico")
        btn_confirmar.setFixedSize(150, 40)
        btn_confirmar.setStyleSheet("background-color: #10B981; border-radius: 5px; font-weight: bold; color: white;")
        btn_confirmar.clicked.connect(self.accept)
        
        layout.addWidget(btn_confirmar, alignment=Qt.AlignmentFlag.AlignCenter)
        
    def get_escolha(self):
        return self.combo.currentText()

class CaraACaraGUI(QMainWindow):
    def __init__(self, pokemons, motor, callback_restart=None):
        super().__init__()
        self.pokemons = pokemons
        self.motor = motor
        self.callback_restart = callback_restart
        
        self.fato_atual = None
        self.cards_ui = []
        self.cartas_baixadas = [False] * len(pokemons)
        
        self.led_state = True
        self.timer_led = QTimer(self)
        self.timer_led.timeout.connect(self.animar_led)
        self.timer_led.start(800)
        
        self.setWindowTitle("Pokédex - Diagnóstico de IA Simbólica")
        self.setFixedSize(1300, 850)
        self.setStyleSheet(STYLESHEET)
        
        self.setup_ui()
        self.show()
        self.escolher_secreto_jogador()
        
    def animar_led(self):
        # Alterna o estado visual da Lente Azul para simular um "breathing" effect
        lente = self.findChild(QFrame, "LenteAzul")
        if lente:
            if self.led_state:
                lente.setStyleSheet("background-color: qradialgradient(cx:0.3, cy:0.3, radius: 1, fx:0.3, fy:0.3, stop:0 #BFDBFE, stop:1 #3B82F6); border-radius: 30px; border: 4px solid #FFFFFF; box-shadow: 0 0 15px #3B82F6;")
            else:
                lente.setStyleSheet("background-color: qradialgradient(cx:0.3, cy:0.3, radius: 1, fx:0.3, fy:0.3, stop:0 #93C5FD, stop:1 #1E3A8A); border-radius: 30px; border: 4px solid #E2E8F0;")
        self.led_state = not self.led_state

    def setup_ui(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        main_layout = QVBoxLayout(widget_central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # --- CABEÇALHO: LENTES DA POKÉDEX ---
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        lente_azul = QFrame()
        lente_azul.setObjectName("LenteAzul")
        lente_azul.setFixedSize(60, 60)
        header_layout.addWidget(lente_azul)
        
        led1 = QFrame(); led1.setObjectName("LedVermelho"); led1.setFixedSize(16, 16)
        led2 = QFrame(); led2.setObjectName("LedAmarelo"); led2.setFixedSize(16, 16)
        led3 = QFrame(); led3.setObjectName("LedVerde"); led3.setFixedSize(16, 16)
        
        header_layout.addWidget(led1, alignment=Qt.AlignmentFlag.AlignTop)
        header_layout.addWidget(led2, alignment=Qt.AlignmentFlag.AlignTop)
        header_layout.addWidget(led3, alignment=Qt.AlignmentFlag.AlignTop)
        
        main_layout.addWidget(header_frame)
        
        # --- CORPO PRINCIPAL (DIVIDIDO EM DOIS) ---
        body_layout = QHBoxLayout()
        
        # LADO ESQUERDO: TELA GRID
        self.grid_container = QFrame()
        self.grid_container.setObjectName("GridScreen")
        grid_layout = QGridLayout(self.grid_container)
        grid_layout.setSpacing(10)
        
        for i, p in enumerate(self.pokemons):
            card = QFrame()
            card.setObjectName("Card")
            card.setFixedSize(180, 215)
            
            sombra = QGraphicsDropShadowEffect()
            sombra.setBlurRadius(15)
            sombra.setXOffset(0)
            sombra.setYOffset(5)
            sombra.setColor(QColor(0, 0, 0, 150))
            card.setGraphicsEffect(sombra)
            
            card_layout = QVBoxLayout(card)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            lbl_img = QLabel()
            pixmap = self.baixar_imagem(p['url_img'])
            lbl_img.setPixmap(pixmap.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(lbl_img)
            
            lbl_nome = QLabel(p['nome'].upper())
            lbl_nome.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
            lbl_nome.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(lbl_nome)
            
            tags_html = f"""
            <div style='color: #9CA3AF; font-size: 10px; text-align: center;'>
                <b>Tipo:</b> {p['tipo'].upper()} | <b>Cor:</b> {p['cor'].upper()}<br>
                <b>Form:</b> {p['formato'].title()}<br>
                <b>Hab:</b> {p['habitat'].title()} | <b>Lend:</b> {p['lendario'].title()}
            </div>
            """
            lbl_tags = QLabel(tags_html)
            card_layout.addWidget(lbl_tags)
            
            grid_layout.addWidget(card, i // 4, i % 4)
            self.cards_ui.append({"frame": card, "dados": p})
            
        body_layout.addWidget(self.grid_container, stretch=2)
        
        # LADO DIREITO: PAINEL DE CONTROLE
        panel_container = QFrame()
        panel_container.setObjectName("Panel")
        panel_container.setFixedWidth(450)
        panel_layout = QVBoxLayout(panel_container)
        panel_layout.setContentsMargins(20, 0, 20, 20)
        
        lbl_titulo = QLabel("DIAGNÓSTICO POKÉMON")
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Weight.Black))
        lbl_titulo.setStyleSheet("color: white;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(lbl_titulo)
        
        # HUD DO ALVO (AGORA COM IMAGEM E DADOS)
        self.hud_alvo = QFrame()
        self.hud_alvo.setObjectName("HudAlvo")
        self.hud_alvo.setFixedHeight(140)
        hud_layout = QHBoxLayout(self.hud_alvo)
        
        self.lbl_img_alvo = QLabel()
        self.lbl_img_alvo.setFixedSize(100, 100)
        self.lbl_img_alvo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hud_layout.addWidget(self.lbl_img_alvo)
        
        self.lbl_info_alvo = QLabel("Aguardando seleção...")
        self.lbl_info_alvo.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        hud_layout.addWidget(self.lbl_info_alvo)
        
        panel_layout.addWidget(self.hud_alvo)
        
        # TERMINAL
        lbl_term = QLabel("PROCESSADOR DE INFERÊNCIA")
        lbl_term.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        lbl_term.setStyleSheet("color: white; margin-top: 15px;")
        panel_layout.addWidget(lbl_term)
        
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        panel_layout.addWidget(self.terminal, stretch=1)
        
        # BOTÕES
        btn_layout = QHBoxLayout()
        self.btn_sim = QPushButton("SIM")
        self.btn_sim.setObjectName("BtnSim")
        self.btn_sim.setFixedHeight(60)
        self.btn_sim.clicked.connect(lambda: self.processar_resposta(True))
        
        self.btn_nao = QPushButton("NÃO")
        self.btn_nao.setObjectName("BtnNao")
        self.btn_nao.setFixedHeight(60)
        self.btn_nao.clicked.connect(lambda: self.processar_resposta(False))
        
        self.btn_reiniciar = QPushButton("JOGAR NOVAMENTE")
        self.btn_reiniciar.setObjectName("BtnReiniciar")
        self.btn_reiniciar.setFixedHeight(60)
        self.btn_reiniciar.clicked.connect(self.reiniciar_jogo)
        self.btn_reiniciar.hide()
        
        btn_layout.addWidget(self.btn_sim)
        btn_layout.addWidget(self.btn_nao)
        panel_layout.addLayout(btn_layout)
        panel_layout.addWidget(self.btn_reiniciar)
        
        body_layout.addWidget(panel_container, stretch=1)
        main_layout.addLayout(body_layout)

    def baixar_imagem(self, url):
        try:
            req = requests.get(url)
            pixmap = QPixmap()
            pixmap.loadFromData(req.content)
            return pixmap
        except:
            return QPixmap()

    def escrever_log(self, texto, cor="#A7F3D0"):
        self.terminal.append(f"<span style='color: {cor};'>> {texto}</span>")
        self.terminal.moveCursor(QTextCursor.MoveOperation.End)

    def escolher_secreto_jogador(self):
        dialog = DialogoAlvo(self, self.pokemons)
        if dialog.exec():
            escolha = dialog.get_escolha()
            self.secreto_jogador = next(p for p in self.pokemons if p['nome'] == escolha)
            
            # ATUALIZA A IMAGEM NO HUD
            pixmap = self.baixar_imagem(self.secreto_jogador['url_img'])
            self.lbl_img_alvo.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            
            # ATUALIZA TODOS OS DADOS NO HUD
            info = f"NOME: {self.secreto_jogador['nome']}\n" \
                   f"TIPO: {self.secreto_jogador['tipo'].upper()}\n" \
                   f"COR : {self.secreto_jogador['cor'].upper()}\n" \
                   f"FORM: {self.secreto_jogador['formato'].title()}\n" \
                   f"HAB : {self.secreto_jogador['habitat'].title()}\n" \
                   f"LEND: {self.secreto_jogador['lendario'].upper()}"
            self.lbl_info_alvo.setText(info)
            
            self.escrever_log("Sistema Especialista Carregado.", "#FCD34D")
            self.escrever_log("Iniciando Encadeamento Progressivo...", "#FCD34D")
            self.escrever_log("-----------------------------", "#A7F3D0")
            self.avancar_motor()
        else:
            sys.exit()

    def processar_resposta(self, afirmativa):
        if not self.fato_atual: return
        
        resp_str = "SIM" if afirmativa else "NÃO"
        self.escrever_log(f"Sinal do Usuário: {resp_str}", "#FFFFFF")
        self.escrever_log("-----------------------------", "#059669")
        
        self.motor.registrar_resposta(self.fato_atual, afirmativa)
        
        atributo, valor = self.fato_atual.split("_", 1)
        valor = valor.replace("_", " ")
        
        for i, card in enumerate(self.cards_ui):
            if not self.cartas_baixadas[i]:
                val_carta = str(card['dados'][atributo]).replace("-", " ")
                match = (val_carta == str(valor))
                
                if match != afirmativa:
                    self.cartas_baixadas[i] = True
                    efeito = QGraphicsOpacityEffect()
                    efeito.setOpacity(0.15) # Fica quase invisível
                    card["frame"].setGraphicsEffect(efeito)
                    card["frame"].setStyleSheet("border: 2px solid #111827;")
                    
        self.avancar_motor()

    def avancar_motor(self):
        if self.motor.diagnosticos:
            diag = self.motor.diagnosticos[0]
            self.escrever_log(f"DIAGNÓSTICO CONCLUÍDO!", "#FBBF24")
            self.escrever_log(f">> {diag} <<", "#FFFFFF")
            self.btn_sim.hide()
            self.btn_nao.hide()
            self.btn_reiniciar.show()
            return

        self.fato_atual, texto = self.motor.obter_proxima_pergunta()
        if self.fato_atual:
            self.escrever_log(texto, "#A7F3D0") # Pergunta em verde claro
        else:
            self.escrever_log("ERRO: Base esgotada sem conclusão.", "#EF4444")
            self.btn_sim.hide()
            self.btn_nao.hide()
            self.btn_reiniciar.show()

    def reiniciar_jogo(self):
        if self.callback_restart:
            self.close()
            self.callback_restart()