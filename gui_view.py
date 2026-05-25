import sys
import random
import requests
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QGridLayout, QLabel, QPushButton, QTextEdit, 
                             QFrame, QGraphicsOpacityEffect, QSplitter)
from PyQt6.QtGui import QPixmap, QFont, QTextCursor
from PyQt6.QtCore import Qt, QTimer

TYPE_COLORS = {
    'normal': '#6B7280', 'fire': '#EF4444', 'water': '#3B82F6', 'electric': '#EAB308',
    'grass': '#22C55E', 'ice': '#06B6D4', 'fighting': '#DC2626', 'poison': '#9333EA',
    'ground': '#D97706', 'flying': '#8B5CF6', 'psychic': '#D946EF', 'bug': '#84CC16',
    'rock': '#B45309', 'ghost': '#4C1D95', 'dragon': '#1D4ED8', 'dark': '#111827',
    'steel': '#475569', 'fairy': '#EC4899'
}

STYLESHEET = """
    QMainWindow { background-color: #0B1120; }
    
    /* Barra Lateral Esquerda */
    QFrame#Sidebar { background-color: #DC0A2D; border-right: 4px solid #991B1B; }
    
    QFrame#LenteAzul { 
        background-color: qradialgradient(cx:0.3, cy:0.3, radius:0.8, fx:0.2, fy:0.2, stop:0 #FFFFFF, stop:0.1 #93C5FD, stop:0.5 #2563EB, stop:1 #1E3A8A);
        border-radius: 35px; border: 4px solid #E2E8F0; border-bottom: 6px solid #94A3B8;
    }
    
    QFrame#LedVermelho { background-color: qradialgradient(cx:0.3, cy:0.3, radius: 1, fx:0.3, fy:0.3, stop:0 #FCA5A5, stop:1 #991B1B); border-radius: 8px; border: 1px solid #7F1D1D; }
    QFrame#LedAmarelo { background-color: qradialgradient(cx:0.3, cy:0.3, radius: 1, fx:0.3, fy:0.3, stop:0 #FDE047, stop:1 #B45309); border-radius: 8px; border: 1px solid #78350F; }
    QFrame#LedVerde { background-color: qradialgradient(cx:0.3, cy:0.3, radius: 1, fx:0.3, fy:0.3, stop:0 #6EE7B7, stop:1 #065F46); border-radius: 8px; border: 1px solid #064E3B; }

    QLabel#VerticalText { color: #FCA5A5; font-family: Consolas; font-weight: bold; font-size: 14px; letter-spacing: 5px; }

    /* Área do Tabuleiro */
    QFrame#GridWrapper { background-color: #0B1120; }
    QFrame#GridScreen { background-color: transparent; }
    
    QFrame#Card { background-color: #111827; border-radius: 12px; border: 2px solid #1E293B; }
    QFrame#Card:hover { border: 2px solid #3B82F6; background-color: #1E293B; }
    QFrame#Card[selecionado="true"] { border: 2px solid #4ADE80; background-color: #064E3B; }
    
    QLabel { color: #F8FAFC; font-family: Consolas, "Courier New", monospace; } 
    
    /* Painel Direito */
    QFrame#Panel { background-color: #DC0A2D; border-left: 4px solid #991B1B; }
    
    QLabel#TituloPanel { color: #FFFFFF; font-family: Arial; font-weight: bold; font-size: 18px; }
    QLabel#SubTituloPanel { color: #FCA5A5; font-family: Arial; font-size: 11px; font-weight: bold; }
    QLabel#LblTerm { color: #FFFFFF; font-family: Arial; font-weight: bold; font-size: 12px; }
    
    /* HUD Alvo */
    QFrame#HudAlvo { background-color: #F8FAFC; border-radius: 12px; border: 4px solid #CBD5E1; }
    
    /* Terminal */
    QTextEdit { 
        background-color: #111827; color: #E2E8F0; border: 4px solid #0F172A; 
        border-radius: 12px; padding: 15px; font-size: 13px; line-height: 1.5;
    }
    
    /* Splitter */
    QSplitter::handle:horizontal { background-color: #0B1120; width: 6px; }
    QSplitter::handle:horizontal:hover { background-color: #3B82F6; }

    QScrollBar:vertical { border: none; background: transparent; width: 8px; margin: 0px; }
    QScrollBar::handle:vertical { background: #334155; border-radius: 4px; }
    QScrollBar::handle:vertical:hover { background: #475569; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; height: 0px; }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

    /* Botões Padrões */
    QPushButton { border-radius: 25px; font-weight: bold; font-size: 16px; color: white; border: none; }
    QPushButton#BtnSim { background-color: #10B981; }
    QPushButton#BtnSim:hover { background-color: #059669; }
    QPushButton#BtnNao { background-color: #EF4444; }
    QPushButton#BtnNao:hover { background-color: #DC2626; }
    
    QPushButton#BtnSubmit { background-color: #FBBF24; color: #111827; border-radius: 12px; }
    QPushButton#BtnSubmit:hover { background-color: #FCD34D; }
    QPushButton#BtnSubmit:disabled { background-color: #1E293B; color: #475569; }
    
    QPushButton#BtnReiniciar { background-color: #3B82F6; border-radius: 12px; }
    QPushButton#BtnReiniciar:hover { background-color: #2563EB; }
    
    /* Botão Toggle Dificuldade */
    QPushButton#BtnDificuldade { background-color: #64748B; color: #FFFFFF; border-radius: 12px; font-weight: bold; font-size: 14px; }
    QPushButton#BtnDificuldade:hover { opacity: 0.8; }

    /* Painel Embutido de Valores Dinâmicos */
    QFrame#ContainerValores {
        background-color: #0B1120; 
        border-radius: 12px;
        border: 2px solid #1E293B;
    }

    /* Tags Interativas (Botões de Pergunta do Jogador) */
    QPushButton.TagBtn {
        background-color: #1E293B;
        color: #94A3B8;
        border: 2px solid #0F172A;
        border-radius: 8px;
        padding: 8px 5px; 
        font-size: 11px;
        font-family: Consolas;
        font-weight: bold;
    }
    QPushButton.TagBtn:hover {
        border: 2px solid #3B82F6;
        color: #E2E8F0;
    }
    QPushButton.TagBtn:checked {
        background-color: #3B82F6;
        color: #FFFFFF;
        border: 2px solid #93C5FD;
    }
    QPushButton.TagBtn:disabled {
        background-color: #0F172A;
        color: #334155;
        border: 2px solid #0F172A;
    }
"""

class PokemonCard(QFrame):
    def __init__(self, pokemon, parent_gui, pixmap):
        super().__init__()
        self.pokemon = pokemon
        self.parent_gui = parent_gui
        self.pixmap = pixmap
        self.setObjectName("Card")
        self.setFixedSize(175, 230)
        self.setProperty("selecionado", "false")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(5)
        
        self.lbl_img = QLabel()
        self.lbl_img.setPixmap(self.pixmap.scaled(85, 85, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.lbl_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_img)
        
        self.lbl_nome = QLabel(self.pokemon['nome'].upper())
        self.lbl_nome.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        self.lbl_nome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_nome)
        
        type_str = self.pokemon['tipo'].lower()
        cor_badge = TYPE_COLORS.get(type_str, '#475569')
        self.lbl_badge = QLabel(type_str.upper())
        self.lbl_badge.setStyleSheet(f"background-color: {cor_badge}; color: white; border-radius: 10px; padding: 2px 10px; font-size: 10px; font-weight: bold;")
        self.lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_badge.setFixedHeight(20)
        layout.addWidget(self.lbl_badge, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        tags_html = f"""
        <div style='color: #64748B; font-size: 10px; text-align: center; line-height: 1.4;'>
            <span style='color:#94A3B8;'>COR</span> {self.pokemon['cor'].upper()}<br>
            <span style='color:#94A3B8;'>FORM</span> {self.pokemon['formato'].title()}<br>
            <span style='color:#94A3B8;'>HAB</span> {self.pokemon['habitat'].title()}<br>
            <span style='color:#94A3B8;'>LEND</span> {self.pokemon['lendario'].title()}
        </div>
        """
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
        self.secreto_ia = None

        self.setWindowTitle("Pokédex - Sistema de Diagnóstico Simbólico")
        self.setFixedSize(1300, 850)
        self.setStyleSheet(STYLESHEET)
        
        self.led_lente_state = True
        self.timer_lente = QTimer(self)
        self.timer_lente.timeout.connect(self.animar_lente)
        self.timer_lente.start(1000)
        
        self.led_red_state = True
        self.timer_red = QTimer(self)
        self.timer_red.timeout.connect(self.animar_led_vermelho)
        self.timer_red.start(400)
        
        self.led_yellow_state = True
        self.timer_yellow = QTimer(self)
        self.timer_yellow.timeout.connect(self.animar_led_amarelo)
        self.timer_yellow.start(750)
        
        self.led_green_state = True
        self.timer_green = QTimer(self)
        self.timer_green.timeout.connect(self.animar_led_verde)
        self.timer_green.start(1200)
        
        self.setup_ui()
        self.show()
        
        self.escrever_log("Pokédex iniciada e pronta para uso.", "sistema")
        self.escrever_log("Selecione a Dificuldade e o seu Pokémon secreto.", "alerta")

    def animar_lente(self):
        lente = self.findChild(QFrame, "LenteAzul")
        if lente:
            if self.led_lente_state:
                lente.setStyleSheet("background-color: qradialgradient(cx:0.3, cy:0.3, radius:0.8, fx:0.2, fy:0.2, stop:0 #BFDBFE, stop:1 #3B82F6); border-radius: 35px; border: 4px solid #FFFFFF; border-bottom: 6px solid #94A3B8;")
            else:
                lente.setStyleSheet("background-color: qradialgradient(cx:0.3, cy:0.3, radius:0.8, fx:0.2, fy:0.2, stop:0 #FFFFFF, stop:0.1 #93C5FD, stop:0.5 #2563EB, stop:1 #1E3A8A); border-radius: 35px; border: 4px solid #E2E8F0; border-bottom: 6px solid #94A3B8;")
        self.led_lente_state = not self.led_lente_state

    def animar_led_vermelho(self):
        led = self.findChild(QFrame, "LedVermelho")
        if led:
            if self.led_red_state:
                led.setStyleSheet("background-color: qradialgradient(cx:0.3, cy:0.3, radius: 1, fx:0.3, fy:0.3, stop:0 #FCA5A5, stop:1 #991B1B); border-radius: 8px; border: 1px solid #7F1D1D;")
            else:
                led.setStyleSheet("background-color: #450a0a; border-radius: 8px; border: 1px solid #220505;")
        self.led_red_state = not self.led_red_state

    def animar_led_amarelo(self):
        led = self.findChild(QFrame, "LedAmarelo")
        if led:
            if self.led_yellow_state:
                led.setStyleSheet("background-color: qradialgradient(cx:0.3, cy:0.3, radius: 1, fx:0.3, fy:0.3, stop:0 #FDE047, stop:1 #B45309); border-radius: 8px; border: 1px solid #78350F;")
            else:
                led.setStyleSheet("background-color: #422006; border-radius: 8px; border: 1px solid #281304;")
        self.led_yellow_state = not self.led_yellow_state

    def animar_led_verde(self):
        led = self.findChild(QFrame, "LedVerde")
        if led:
            if self.led_green_state:
                led.setStyleSheet("background-color: qradialgradient(cx:0.3, cy:0.3, radius: 1, fx:0.3, fy:0.3, stop:0 #6EE7B7, stop:1 #065F46); border-radius: 8px; border: 1px solid #064E3B;")
            else:
                led.setStyleSheet("background-color: #022c22; border-radius: 8px; border: 1px solid #011611;")
        self.led_green_state = not self.led_green_state

    def setup_ui(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        main_layout = QHBoxLayout(widget_central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- BARRA LATERAL VERMELHA ---
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(100)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        side_layout.setContentsMargins(10, 30, 10, 30)
        
        lente_azul = QFrame(); lente_azul.setObjectName("LenteAzul"); lente_azul.setFixedSize(70, 70)
        side_layout.addWidget(lente_azul, alignment=Qt.AlignmentFlag.AlignHCenter)
        side_layout.addSpacing(20)
        
        leds_layout = QVBoxLayout()
        leds_layout.setSpacing(8)
        leds_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        led1 = QFrame(); led1.setObjectName("LedVermelho"); led1.setFixedSize(16, 16)
        led2 = QFrame(); led2.setObjectName("LedAmarelo"); led2.setFixedSize(16, 16)
        led3 = QFrame(); led3.setObjectName("LedVerde"); led3.setFixedSize(16, 16)
        leds_layout.addWidget(led1); leds_layout.addWidget(led2); leds_layout.addWidget(led3)
        side_layout.addLayout(leds_layout)
        
        side_layout.addSpacing(50)
        lbl_vert = QLabel("P\nO\nK\nÉ\nD\nE\nX")
        lbl_vert.setObjectName("VerticalText")
        lbl_vert.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_layout.addWidget(lbl_vert)
        
        main_layout.addWidget(sidebar)
        
        # --- SPLITTER (REDIMENSIONAMENTO HORIZONTAL) ---
        body_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 1. Container do Grid (Lado Esquerdo do Splitter)
        grid_wrapper = QFrame()
        grid_wrapper.setObjectName("GridWrapper")
        grid_wrapper.setMinimumWidth(500)
        wrapper_layout = QVBoxLayout(grid_wrapper)
        wrapper_layout.setContentsMargins(30, 30, 30, 30)
        
        self.grid_container = QFrame()
        self.grid_container.setObjectName("GridScreen")
        grid_layout = QGridLayout(self.grid_container)
        grid_layout.setSpacing(8)
        
        for i, p in enumerate(self.pokemons):
            pixmap = self.baixar_imagem(p['url_img'])
            card = PokemonCard(p, self, pixmap)
            grid_layout.addWidget(card, i // 4, i % 4)
            self.cards_ui.append(card)
            
        wrapper_layout.addWidget(self.grid_container)
        body_splitter.addWidget(grid_wrapper)
        
        # 2. Container do Painel Direito
        panel_container = QFrame()
        panel_container.setObjectName("Panel")
        panel_container.setMinimumWidth(350)
        panel_layout = QVBoxLayout(panel_container)
        panel_layout.setContentsMargins(25, 25, 25, 25)
        
        lbl_titulo = QLabel("SISTEMA ESPECIALISTA")
        lbl_titulo.setObjectName("TituloPanel")
        panel_layout.addWidget(lbl_titulo)
        
        lbl_sub = QLabel("DIAGNÓSTICO POR INFERÊNCIA PROGRESSIVA")
        lbl_sub.setObjectName("SubTituloPanel")
        panel_layout.addWidget(lbl_sub)
        panel_layout.addSpacing(15)
        
        # HUD DO ALVO (BRANCO)
        self.hud_alvo = QFrame()
        self.hud_alvo.setObjectName("HudAlvo")
        self.hud_alvo.setFixedHeight(170)
        hud_layout = QHBoxLayout(self.hud_alvo)
        
        self.lbl_img_alvo = QLabel()
        self.lbl_img_alvo.setFixedSize(90, 90) 
        self.lbl_img_alvo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hud_layout.addWidget(self.lbl_img_alvo)
        
        self.lbl_info_alvo = QLabel("<span style='color:#64748B;'>Aguardando Alvo...</span>")
        hud_layout.addWidget(self.lbl_info_alvo)
        panel_layout.addWidget(self.hud_alvo)
        
        panel_layout.addSpacing(15)
        lbl_term = QLabel("ANÁLISE LOG")
        lbl_term.setObjectName("LblTerm")
        panel_layout.addWidget(lbl_term)
        
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        panel_layout.addWidget(self.terminal, stretch=1)
        panel_layout.addSpacing(15)
        
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(15)
        
        self.btn_sim = QPushButton("SIM")
        self.btn_sim.setObjectName("BtnSim")
        self.btn_sim.setFixedHeight(50)
        self.btn_sim.clicked.connect(lambda: self.processar_resposta(True))
        self.btn_sim.hide() 
        
        self.btn_nao = QPushButton("NÃO")
        self.btn_nao.setObjectName("BtnNao")
        self.btn_nao.setFixedHeight(50)
        self.btn_nao.clicked.connect(lambda: self.processar_resposta(False))
        self.btn_nao.hide() 
        
        # NOVO: Botão de Alternar Dificuldade
        self.btn_dificuldade = QPushButton("DIFICULDADE: NORMAL")
        self.btn_dificuldade.setObjectName("BtnDificuldade")
        self.btn_dificuldade.setFixedHeight(40)
        self.btn_dificuldade.clicked.connect(self.alternar_dificuldade)
        panel_layout.addWidget(self.btn_dificuldade)
        
        self.btn_submit = QPushButton("CONFIRMAR ALVO")
        self.btn_submit.setObjectName("BtnSubmit")
        self.btn_submit.setFixedHeight(50)
        self.btn_submit.setEnabled(False)
        self.btn_submit.clicked.connect(self.confirmar_alvo_tabuleiro)
        
        self.btn_reiniciar = QPushButton("JOGAR NOVAMENTE")
        self.btn_reiniciar.setObjectName("BtnReiniciar")
        self.btn_reiniciar.setFixedHeight(50)
        self.btn_reiniciar.clicked.connect(self.reiniciar_jogo)
        self.btn_reiniciar.hide()
        
        self.btn_layout.addWidget(self.btn_sim)
        self.btn_layout.addWidget(self.btn_nao)
        panel_layout.addLayout(self.btn_layout)
        panel_layout.addWidget(self.btn_submit)
        panel_layout.addWidget(self.btn_reiniciar)
        
        # --- PAINEL DO TURNO DO JOGADOR ---
        self.painel_jogador = QFrame()
        self.painel_jogador.hide()
        layout_jog = QVBoxLayout(self.painel_jogador)
        layout_jog.setSpacing(10)
        
        # Título ajustado com cor branca
        lbl_sua_vez = QLabel("SUA VEZ: MONTE SUA PERGUNTA")
        lbl_sua_vez.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 13px; margin-bottom: 5px;")
        layout_jog.addWidget(lbl_sua_vez)
        
        self.categoria_selecionada = None
        self.valor_selecionado = None
        self.botoes_categorias = []
        self.botoes_valores = []
        
        # 1. Linha de Categorias
        row_categorias = QHBoxLayout()
        row_categorias.setSpacing(8)
        for cat in ["tipo", "cor", "formato", "habitat", "lendario"]:
            btn = QPushButton(cat.upper())
            btn.setProperty("class", "TagBtn")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, c=cat, b=btn: self.selecionar_categoria(c, b))
            row_categorias.addWidget(btn)
            self.botoes_categorias.append(btn)
        layout_jog.addLayout(row_categorias)
        
        # 2. Grid de Valores Dinâmicos (Painel Embutido Escuro)
        self.container_valores = QFrame()
        self.container_valores.setObjectName("ContainerValores")
        self.layout_valores = QGridLayout(self.container_valores)
        self.layout_valores.setContentsMargins(15, 15, 15, 15)
        self.layout_valores.setSpacing(10)
        layout_jog.addWidget(self.container_valores)
        
        # Botões de Ação
        self.btn_perguntar = QPushButton("PERGUNTAR À IA")
        self.btn_perguntar.setStyleSheet("background-color: #3B82F6; border-radius: 12px; height: 40px; font-size: 13px; margin-top: 5px;")
        self.btn_perguntar.setEnabled(False) 
        self.btn_perguntar.clicked.connect(self.jogador_pergunta_ia)
        layout_jog.addWidget(self.btn_perguntar)
        
        self.btn_chutar = QPushButton("TENTAR ADIVINHAR (Selecione no Grid)")
        self.btn_chutar.setStyleSheet("background-color: #8B5CF6; border-radius: 12px; height: 40px; font-size: 13px;")
        self.btn_chutar.clicked.connect(self.jogador_tenta_adivinhar)
        layout_jog.addWidget(self.btn_chutar)
        
        panel_layout.addWidget(self.painel_jogador)
        
        body_splitter.addWidget(panel_container)
        body_splitter.setSizes([850, 450])
        
        main_layout.addWidget(body_splitter, stretch=1)

    def alternar_dificuldade(self):
        if self.motor.dificuldade == "normal":
            self.motor.set_dificuldade("hard")
            self.btn_dificuldade.setText("DIFICULDADE: DIFÍCIL (Hard)")
            self.btn_dificuldade.setStyleSheet("background-color: #991B1B;")
        else:
            self.motor.set_dificuldade("normal")
            self.btn_dificuldade.setText("DIFICULDADE: NORMAL")
            self.btn_dificuldade.setStyleSheet("background-color: #64748B;")

    def baixar_imagem(self, url):
        try:
            req = requests.get(url)
            pixmap = QPixmap()
            pixmap.loadFromData(req.content)
            return pixmap
        except: return QPixmap()

    def escrever_log(self, texto, tipo="info"):
        cores = {
            "sistema": "#38BDF8",  
            "pergunta": "#F87171", 
            "usuario": "#94A3B8",  
            "alerta": "#FBBF24",   
            "sucesso": "#4ADE80",  
            "erro": "#EF4444",     
            "info": "#475569",
            "ia": "#3B82F6"      
        }
        
        prefixos = {
            "sistema": "[SYS]", "pergunta": "[S.E.]", "usuario": "[I/O]", 
            "alerta": "[WARN]", "sucesso": "[OK]", "erro": "[ERR]", "info": ">>>",
            "ia": "[IA]"         
        }
        
        negrito = "font-weight: bold;" if tipo in ["sucesso", "erro", "alerta", "ia"] else "font-weight: normal;"
        
        cor = cores.get(tipo, "#FFFFFF")
        prefixo = prefixos.get(tipo, ">>>")
        
        self.terminal.append(f"<span style='color: {cor}; {negrito}'>{prefixo} {texto}</span>")
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
            
            info = f"<span style='color:#DC2626; font-size:11px; font-weight:bold;'>ALVO SELECIONADO</span><br><br>" \
                   f"<b style='color:#0F172A; font-size:15px;'>{p['nome'].upper()}</b><br>" \
                   f"<span style='color:#334155; font-size:12px;'>Tipo: {p['tipo'].title()}<br>" \
                   f"Cor: {p['cor'].title()}</span>"
            self.lbl_info_alvo.setText(info)
            self.btn_submit.setEnabled(True)
            
        elif self.estado_interface == "INFERENCIA":
            idx = self.cards_ui.index(card_component)
            if self.cartas_baixadas[idx]:
                return
                
            if self.card_selecionado_temp:
                self.card_selecionado_temp.setProperty("selecionado", "false")
                self.card_selecionado_temp.style().unpolish(self.card_selecionado_temp)
                self.card_selecionado_temp.style().polish(self.card_selecionado_temp)
            
            self.card_selecionado_temp = card_component
            card_component.setProperty("selecionado", "true")
            card_component.style().unpolish(card_component)
            card_component.style().polish(card_component)
            
            p = card_component.pokemon
            self.escrever_log(f"Selecionado no tabuleiro: {p['nome'].upper()} (Pronto para chutar)", "info")

    def confirmar_alvo_tabuleiro(self):
        if not self.card_selecionado_temp: return
        
        self.secreto_jogador = self.card_selecionado_temp.pokemon
        self.secreto_ia = random.choice(self.pokemons)
        self.estado_interface = "INFERENCIA"
        
        self.card_selecionado_temp.setProperty("selecionado", "false")
        self.card_selecionado_temp.style().unpolish(self.card_selecionado_temp)
        self.card_selecionado_temp.style().polish(self.card_selecionado_temp)
        
        p = self.secreto_jogador
        
        info = f"<span style='color:#059669; font-size:11px; font-weight:bold;'>SEU POKÉMON</span><br><br>" \
               f"<b style='color:#0F172A; font-size:15px;'>{p['nome'].upper()}</b><br>" \
               f"<span style='color:#334155; font-size:12px;'>" \
               f"Tipo: {p['tipo'].title()}<br>" \
               f"Cor: {p['cor'].title()}<br>" \
               f"Formato: {p['formato'].title()}<br>" \
               f"Habitat: {p['habitat'].title()}<br>" \
               f"Lendário: {p['lendario'].title()}</span>"
        self.lbl_info_alvo.setText(info)
        
        # Oculta o botão de confirmar e de trocar dificuldade
        self.btn_submit.hide()
        self.btn_dificuldade.hide()
        
        self.escrever_log(f"Seu Pokémon confirmado: {p['nome'].upper()}", "sucesso")
        self.escrever_log(f"Modo Selecionado: {self.motor.dificuldade.upper()}", "info")
        self.escrever_log("A IA escolheu o Pokémon secreto dela! Que vença o melhor.", "alerta")
        
        self.iniciar_turno_ia()

    def selecionar_categoria(self, categoria, btn_clicado):
        for btn in self.botoes_categorias:
            if btn != btn_clicado:
                btn.setChecked(False)
        
        self.categoria_selecionada = categoria
        self.valor_selecionado = None
        self.btn_perguntar.setEnabled(False)
        self.atualizar_grid_valores(categoria)

    def atualizar_grid_valores(self, categoria):
        for i in reversed(range(self.layout_valores.count())): 
            widget = self.layout_valores.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        self.botoes_valores = []
        if not categoria: return
        
        valores = sorted(list(set(str(p[categoria]) for p in self.pokemons)))
        
        for i, val in enumerate(valores):
            btn = QPushButton(val.upper())
            btn.setProperty("class", "TagBtn")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, v=val, b=btn: self.selecionar_valor(v, b))
            
            linha = i // 3
            coluna = i % 3
            self.layout_valores.addWidget(btn, linha, coluna)
            self.botoes_valores.append(btn)

    def selecionar_valor(self, valor, btn_clicado):
        for btn in self.botoes_valores:
            if btn != btn_clicado:
                btn.setChecked(False)
                
        self.valor_selecionado = valor
        self.btn_perguntar.setEnabled(True)

    def iniciar_turno_ia(self):
        self.painel_jogador.hide()
        
        # VERIFICAÇÃO DE VITÓRIA DA IA POSTERGADA
        # A IA só anuncia que sabe a resposta na VEZ DELA, e não enquanto processa sua resposta.
        if self.motor.diagnosticos:
            diag = self.motor.diagnosticos[0]
            self.escrever_log("Já sei qual é o seu Pokémon!", "ia")
            self.escrever_log(f"A IA VENCEU O JOGO! {diag}", "ia")
            self.finalizar_jogo()
            return
            
        self.btn_sim.show()
        self.btn_nao.show()
        
        self.fato_atual, texto = self.motor.obter_proxima_pergunta()
        if self.fato_atual:
            self.escrever_log(texto, "pergunta")
        else:
            self.escrever_log("A IA não possui mais perguntas na base de conhecimento.", "info")
            self.iniciar_turno_jogador()

    def processar_resposta(self, afirmativa):
        if not self.fato_atual: return
        
        resp_str = "SIM" if afirmativa else "NÃO"
        self.escrever_log(f"Sua resposta para a IA: {resp_str}", "usuario")
        
        self.motor.registrar_resposta(self.fato_atual, afirmativa)
        
        # A IA não analisa a vitória aqui. Ela sempre devolve o turno pro jogador.
        # Mesmo que já saiba a resposta por eliminação, ela aguarda o turno dela para falar!
        self.iniciar_turno_jogador()

    def iniciar_turno_jogador(self):
        self.escrever_log("SUA VEZ! Faça uma pergunta ou tente adivinhar.", "alerta")
        self.btn_sim.hide()
        self.btn_nao.hide()
        self.painel_jogador.show()

    def jogador_pergunta_ia(self):
        cat = self.categoria_selecionada
        val = self.valor_selecionado
        
        if not cat or not val: return
        
        self.escrever_log(f"Você: O Pokémon da IA tem {cat} = {val}?", "usuario")
        
        valor_real = str(self.secreto_ia[cat])
        afirmativa = (valor_real.lower() == val.lower())
        
        resp_ia = "SIM!" if afirmativa else "NÃO!"
        self.escrever_log(f"IA: {resp_ia}", "ia")
        
        for i, card in enumerate(self.cards_ui):
            if not self.cartas_baixadas[i]:
                val_carta = str(card.pokemon[cat]).lower()
                match = (val_carta == val.lower())
                
                if match != afirmativa:
                    self.cartas_baixadas[i] = True
                    efeito = QGraphicsOpacityEffect()
                    efeito.setOpacity(0.15)
                    card.setGraphicsEffect(efeito)
                    card.setStyleSheet("border: 2px solid #0B1120;")
                    
        for btn in self.botoes_categorias: btn.setChecked(False)
        self.atualizar_grid_valores(None) 
        self.btn_perguntar.setEnabled(False)
        
        self.iniciar_turno_ia()

    def jogador_tenta_adivinhar(self):
        if not self.card_selecionado_temp or self.estado_interface != "INFERENCIA":
            self.escrever_log("Selecione uma carta ativa no tabuleiro para dar o palpite!", "alerta")
            return
            
        chute = self.card_selecionado_temp.pokemon
        self.escrever_log(f"Você: O seu Pokémon secreto é o {chute['nome'].upper()}?", "usuario")
        
        if chute['id'] == self.secreto_ia['id']:
            self.escrever_log("INCRÍVEL! VOCÊ ACERTOU! PARABÉNS, VOCÊ VENCEU!", "ia")
        else:
            self.escrever_log(f"ERRADO! O meu Pokémon secreto era o {self.secreto_ia['nome'].upper()}. EU VENCI!", "ia")
            
        self.finalizar_jogo()

    def finalizar_jogo(self):
        self.btn_sim.hide()
        self.btn_nao.hide()
        self.painel_jogador.hide()
        self.btn_reiniciar.show()
        self.parar_leds()

    def parar_leds(self):
        self.timer_lente.stop()
        self.timer_red.stop()
        self.timer_yellow.stop()
        self.timer_green.stop()

    def reiniciar_jogo(self):
        if self.callback_restart:
            self.close()
            self.callback_restart()