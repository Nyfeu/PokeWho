import sys
from PyQt6.QtWidgets import QApplication
from api_client import PokeApiClient
from knowledge_builder import YamlKnowledgeBuilder
from expert_engine import MotorInferenciaEventDriven
from gui_view import CaraACaraGUI

def iniciar_app():
    # Cria a instância raiz do Qt
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    print("Sincronizando com a PokeAPI (Buscando 12 espécies)...")
    cliente = PokeApiClient(quantidade=12)
    pokemons = cliente.buscar_pokemons()
    
    print("Gerando YAML de Regras...")
    construtor = YamlKnowledgeBuilder()
    caminho_yaml = construtor.gerar_base_conhecimento(pokemons)
    
    print("Instanciando Sistema Especialista...")
    motor = MotorInferenciaEventDriven(caminho_yaml)
    
    # Inicia a Interface PyQt. Passamos `iniciar_app` como callback de Restart
    gui = CaraACaraGUI(pokemons, motor, callback_restart=iniciar_app)
    
    # Inicia o loop de eventos
    app.exec()

if __name__ == "__main__":
    iniciar_app()