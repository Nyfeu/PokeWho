import sys
import requests
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QLabel, QPushButton, QTextEdit, 
                             QFrame, QGraphicsOpacityEffect, QGraphicsDropShadowEffect)
from PyQt6.QtGui import QPixmap, QFont, QColor, QTextCursor
from PyQt6.QtCore import Qt, QTimer

STYLESHEET = """
    QMainWindow { background-color: #DC0A2D; }
    
    QFrame#LenteAzul { border-radius: 30px; border: 4px solid #E2E8F0; }
    QFrame#LedVermelho { background-color: qradialgradient(cx:0.3, cy:0.3, radius: 1, fx:0.3, fy:0.3, stop:0 #FCA5A5, stop:1 #991B1B); border-radius: 8px; border: 1px solid #7F1D1D; }
    QFrame#LedAmarelo { background-color: qradialgradient(cx:0.3, cy:0.3, radius: 1, fx:0.3, fy:0.3, stop:0 #FDE047, stop:1 #B45309); border-radius: 8px; border: 1px solid #78350F; }
    QFrame#LedVerde { background-color: qradialgradient(cx:0.3, cy:0.3, radius: 1, fx:0.3, fy:0.3, stop:0 #6EE7B7, stop:1 #065F46); border-radius: 8px; border: 1px solid #064E3B; }

    QFrame#GridScreen { background-color: #111827; border-radius: 10px; border: 15px solid #E5E7EB; border-bottom: 30px solid #E5E7EB; }
    
    QFrame#Card { background-color: #1F2937; border-radius: 8px; border: 2px solid #374151; }
    QFrame#Card:hover { border: 2px solid #9CA3AF; background-color: #374151; }
    QFrame#Card[selecionado="true"] { border: 3px solid #FBBF24; background-color: #2D3748; }
    
    QLabel { color: #F8FAFC; } 
    
    QFrame#Panel { background-color: #DC0A2D; border-left: 4px solid #991B1B; }
    QFrame#HudAlvo { background-color: #111827; border-radius: 8px; border: 4px solid #E5E7EB; }
    QFrame#HudAlvo QLabel { color: #4ADE80; font-family: Consolas; } 

    QTextEdit { background-color: #064E3B; color: #A7F3D0; border: 4px solid #E5E7EB; border-radius: 5px; padding: 5px; font-family: Consolas; font-size: 13px; }
    
    QScrollBar:vertical { border: none; background: #064E3B; width: 14px; margin: 0px; }
    QScrollBar::handle:vertical { background: #10B981; min-height: 30px; border-radius: 7px; }
    QScrollBar::handle:vertical:hover { background: #34D399; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; height: 0px; }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

    QPushButton { border-radius: 8px; font-weight: bold; font-size: 16px; color: white; border: 2px solid #111827; }
    QPushButton#BtnSim { background-color: #10B981; border-bottom: 4px solid #047857; }
    QPushButton#BtnSim:pressed { background-color: #059669; border-bottom: 0px; margin-top: 4px; }
    QPushButton#BtnNao { background-color: #EF4444; border-bottom: 4px solid #B91C1C; }
    QPushButton#BtnNao:pressed { background-color: #DC2626; border-bottom: 0px; margin-top: 4px; }
    
    QPushButton#BtnSubmit { background-color: #FBBF24; color: #111827; border-bottom: 4px solid #D97706; }
    QPushButton#BtnSubmit:hover { background-color: #FCD34D; }
    QPushButton#BtnSubmit:pressed { background-color: #FBBF24; border-bottom: 0px; margin-top: 4px; }
    QPushButton#BtnSubmit:disabled { background-color: #4B5563; color: #9CA3AF; border-bottom: 2px solid #374151; }
    
    QPushButton#BtnReiniciar { background-color: #3B82F6; border-bottom: 4px solid #1D4ED8; }
    QPushButton#BtnReiniciar:pressed { background-color: #2563EB; border-bottom: 0px; margin-top: 4px; }
"""

class PokemonCard(QFrame):
    def __init__(self, pokemon, parent_gui, pixmap):
        super().__init__()
        self.pokemon = pokemon
        self.parent_gui = parent_gui
        self.pixmap = pixmap
        self.setObjectName("Card")
        self.setFixedSize(180, 215)
        self.setProperty("selecionado", "false")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_img = QLabel()
        self.lbl_img.setPixmap(self.pixmap.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_img)
        
        self.lbl_nome = QLabel(self.pokemon['nome'].upper())
        self.lbl_nome.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.lbl_nome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_nome)
        
        tags_html = f"<div style='color: #9CA3AF; font-size: 10px; text-align: center;'><b>Tipo:</b> {self.pokemon['tipo'].upper()} | <b>Cor:</b> {self.pokemon['cor'].upper()}<br><b>Form:</b> {self.pokemon['formato'].title()}<br><b>Hab:</b> {self.pokemon['habitat'].title()} | <b>Lend:</b> {self.pokemon['lendario'].title()}</div>"
        lbl_tags = QLabel(tags_html)
        layout.addWidget(lbl_tags)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent_gui.controlar_clique_card(self)

class CaraACaraGUI(QMainWindow):
    def __init__(self, pokemons, motor, callback_restart=None):
        super().__init__()
        self.pokemons = pokemons
        self.motor = motor
        self.callback_restart = callback_restart
        
        self.fato_atual = None
        self.cards_ui = []
        self.cartas_baixadas = [False] * len(pokemons)
        
        self.estado_interface = "SELECAO"
        self.card_selecionado_temp = None
        self.secreto_jogador = None

        self.setWindowTitle("Pokédex - Diagnóstico de IA Simbólica")
        self.setFixedSize(1300, 850)
        self.setStyleSheet(STYLESHEET)
        
        self.led_state = True
        self.timer_led = QTimer(self)
        self.timer_led.timeout.connect(self.animar_led)
        self.timer_led.start(800)
        
        self.setup_ui()
        self.show()
        
        self.escrever_log("MODO DE SELEÇÃO ATIVO.", "#FCD34D")
        self.escrever_log("Clique no seu Pokémon secreto diretamente no tabuleiro à esquerda e clique em 'CONFIRMAR SELEÇÃO'.", "#FCD34D")

    def animar_led(self):
        lente = self.findChild(QFrame, "LenteAzul")
        if lente:
            if self.led_state:
                lente.setStyleSheet("background-color: qradialgradient(cx:0.3, cy:0.3, radius: 1, fx:0.3, fy:0.3, stop:0 #BFDBFE, stop:1 #3B82F6); border-radius: 30px; border: 4px solid #FFFFFF;")
            else:
                lente.setStyleSheet("background-color: qradialgradient(cx:0.3, cy:0.3, radius: 1, fx:0.3, fy:0.3, stop:0 #93C5FD, stop:1 #1E3A8A); border-radius: 30px; border: 4px solid #E2E8F0;")
        self.led_state = not self.led_state

    def setup_ui(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        main_layout = QVBoxLayout(widget_central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        lente_azul = QFrame(); lente_azul.setObjectName("LenteAzul"); lente_azul.setFixedSize(60, 60)
        led1 = QFrame(); led1.setObjectName("LedVermelho"); led1.setFixedSize(16, 16)
        led2 = QFrame(); led2.setObjectName("LedAmarelo"); led2.setFixedSize(16, 16)
        led3 = QFrame(); led3.setObjectName("LedVerde"); led3.setFixedSize(16, 16)
        
        header_layout.addWidget(lente_azul)
        header_layout.addWidget(led1, alignment=Qt.AlignmentFlag.AlignTop)
        header_layout.addWidget(led2, alignment=Qt.AlignmentFlag.AlignTop)
        header_layout.addWidget(led3, alignment=Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(header_frame)
        
        body_layout = QHBoxLayout()
        self.grid_container = QFrame()
        self.grid_container.setObjectName("GridScreen")
        grid_layout = QGridLayout(self.grid_container)
        grid_layout.setSpacing(10)
        
        for i, p in enumerate(self.pokemons):
            pixmap = self.baixar_imagem(p['url_img'])
            card = PokemonCard(p, self, pixmap)
            
            sombra = QGraphicsDropShadowEffect()
            sombra.setBlurRadius(15)
            sombra.setXOffset(0)
            sombra.setYOffset(5)
            sombra.setColor(QColor(0, 0, 0, 150))
            card.setGraphicsEffect(sombra)
            
            grid_layout.addWidget(card, i // 4, i % 4)
            self.cards_ui.append(card)
            
        body_layout.addWidget(self.grid_container, stretch=2)
        
        panel_container = QFrame()
        panel_container.setObjectName("Panel")
        panel_container.setFixedWidth(450)
        panel_layout = QVBoxLayout(panel_container)
        panel_layout.setContentsMargins(20, 0, 20, 20)
        
        lbl_titulo = QLabel("DIAGNÓSTICO POKÉMON")
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Weight.Black))
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(lbl_titulo)
        
        self.hud_alvo = QFrame()
        self.hud_alvo.setObjectName("HudAlvo")
        # AUMENTADO PARA 180px PARA CABER TODO O TEXTO SEM CORTAR
        self.hud_alvo.setFixedHeight(180) 
        hud_layout = QHBoxLayout(self.hud_alvo)
        
        self.lbl_img_alvo = QLabel()
        self.lbl_img_alvo.setFixedSize(90, 90) # Imagem levemente reduzida para abrir espaço
        self.lbl_img_alvo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hud_layout.addWidget(self.lbl_img_alvo)
        
        self.lbl_info_alvo = QLabel("Selecione um card...")
        self.lbl_info_alvo.setFont(QFont("Consolas", 10, QFont.Weight.Bold)) # Fonte levemente reduzida (10pt)
        hud_layout.addWidget(self.lbl_info_alvo)
        panel_layout.addWidget(self.hud_alvo)
        
        lbl_term = QLabel("PROCESSADOR DE INFERÊNCIA")
        lbl_term.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        lbl_term.setStyleSheet("margin-top: 10px;")
        panel_layout.addWidget(lbl_term)
        
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        panel_layout.addWidget(self.terminal, stretch=1)
        
        self.btn_layout = QHBoxLayout()
        self.btn_sim = QPushButton("SIM")
        self.btn_sim.setObjectName("BtnSim")
        self.btn_sim.setFixedHeight(60)
        self.btn_sim.clicked.connect(lambda: self.processar_resposta(True))
        self.btn_sim.hide() 
        
        self.btn_nao = QPushButton("NÃO")
        self.btn_nao.setObjectName("BtnNao")
        self.btn_nao.setFixedHeight(60)
        self.btn_nao.clicked.connect(lambda: self.processar_resposta(False))
        self.btn_nao.hide() 
        
        self.btn_submit = QPushButton("CONFIRMAR SELEÇÃO")
        self.btn_submit.setObjectName("BtnSubmit")
        self.btn_submit.setFixedHeight(60)
        self.btn_submit.setEnabled(False)
        self.btn_submit.clicked.connect(self.confirmar_alvo_tabuleiro)
        
        self.btn_reiniciar = QPushButton("JOGAR NOVAMENTE")
        self.btn_reiniciar.setObjectName("BtnReiniciar")
        self.btn_reiniciar.setFixedHeight(60)
        self.btn_reiniciar.clicked.connect(self.reiniciar_jogo)
        self.btn_reiniciar.hide()
        
        self.btn_layout.addWidget(self.btn_sim)
        self.btn_layout.addWidget(self.btn_nao)
        panel_layout.addLayout(self.btn_layout)
        panel_layout.addWidget(self.btn_submit)
        panel_layout.addWidget(self.btn_reiniciar)
        
        body_layout.addWidget(panel_container, stretch=1)
        main_layout.addLayout(body_layout)

    def baixar_imagem(self, url):
        try:
            req = requests.get(url)
            pixmap = QPixmap()
            pixmap.loadFromData(req.content)
            return pixmap
        except: return QPixmap()

    def escrever_log(self, texto, cor="#A7F3D0"):
        self.terminal.append(f"<span style='color: {cor};'>> {texto}</span>")
        self.terminal.moveCursor(QTextCursor.MoveOperation.End)

    def controlar_clique_card(self, card_component):
        if self.estado_interface == "SELECAO":
            if self.card_selecionado_temp:
                self.card_selecionado_temp.setProperty("selecionado", "false")
                self.card_selecionado_temp.style().unpolish(self.card_selecionado_temp)
                self.card_selecionado_temp.style().polish(self.card_selecionado_temp)
            
            self.card_selecionado_temp = card_component
            card_component.setProperty("selecionado", "true")
            card_component.style().unpolish(card_component)
            card_component.style().polish(card_component)
            
            self.lbl_img_alvo.setPixmap(card_component.pixmap.scaled(85, 85, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            p = card_component.pokemon
            info = f"PREVIEW:\nNOME: {p['nome']}\nTIPO: {p['tipo'].upper()}\nCOR : {p['cor'].upper()}"
            self.lbl_info_alvo.setText(info)
            
            self.btn_submit.setEnabled(True)

    def confirmar_alvo_tabuleiro(self):
        if not self.card_selecionado_temp: return
        
        self.secreto_jogador = self.card_selecionado_temp.pokemon
        self.estado_interface = "INFERENCIA"
        
        self.card_selecionado_temp.setProperty("selecionado", "false")
        self.card_selecionado_temp.style().unpolish(self.card_selecionado_temp)
        self.card_selecionado_temp.style().polish(self.card_selecionado_temp)
        
        p = self.secreto_jogador
        info = f"ALVO CONFIRMADO:\nNOME: {p['nome']}\nTIPO: {p['tipo'].upper()}\nCOR : {p['cor'].upper()}\nFORM: {p['formato'].title()}\nHAB : {p['habitat'].title()}\nLEND: {p['lendario'].upper()}"
        self.lbl_info_alvo.setText(info)
        
        self.btn_submit.hide()
        self.btn_sim.show()
        self.btn_nao.show()
        
        self.escrever_log("Alvo definido com sucesso direto do tabuleiro.", "#4ADE80")
        self.escrever_log("Sistema Especialista Carregado (Encadeamento Progressivo).", "#FCD34D")
        self.escrever_log("-----------------------------", "#A7F3D0")
        
        self.avancar_motor()

    def processar_resposta(self, afirmativa):
        if not self.fato_atual: return
        
        resp_str = "SIM" if afirmativa else "NÃO"
        self.escrever_log(f"Sinal do Usuário: {resp_str}", "#FFFFFF")
        self.escrever_log("-----------------------------", "#059669")
        
        self.motor.registrar_resposta(self.fato_atual, afirmativa)
        
        atributo, valor = self.fato_atual.split("_", 1)
        
        for i, card in enumerate(self.cards_ui):
            if not self.cartas_baixadas[i]:
                # NORMALIZAÇÃO AGRESSIVA PARA EVITAR BUGS DE HÍFEN/ESPAÇO
                val_carta = str(card.pokemon[atributo]).replace("-", "").replace("_", "").replace(" ", "").lower()
                val_pergunta = valor.replace("-", "").replace("_", "").replace(" ", "").lower()
                
                match = (val_carta == val_pergunta)
                
                if match != afirmativa:
                    self.cartas_baixadas[i] = True
                    efeito = QGraphicsOpacityEffect()
                    efeito.setOpacity(0.15)
                    card.setGraphicsEffect(efeito)
                    card.setStyleSheet("border: 2px solid #111827;")
                    
        self.avancar_motor()

    def avancar_motor(self):
        if self.motor.diagnosticos:
            diag = self.motor.diagnosticos[0]
            self.escrever_log(f"DIAGNÓSTICO CONCLUÍDO!", "#FBBF24")
            self.escrever_log(f">> {diag} <<", "#FFFFFF")
            self.btn_sim.hide()
            self.btn_nao.hide()
            self.btn_reiniciar.show()
            self.timer_led.stop()
            return

        self.fato_atual, texto = self.motor.obter_proxima_pergunta()
        if self.fato_atual:
            self.escrever_log(texto, "#A7F3D0")
        else:
            self.escrever_log("ERRO: Base esgotada sem conclusão.", "#EF4444")
            self.btn_sim.hide()
            self.btn_nao.hide()
            self.btn_reiniciar.show()

    def reiniciar_jogo(self):
        if self.callback_restart:
            self.close()
            self.callback_restart()