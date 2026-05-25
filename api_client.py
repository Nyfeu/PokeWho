import requests
import random

class PokeApiClient:
    def __init__(self, limite_id=151, quantidade=12):
        self.limite_id = limite_id
        self.quantidade = quantidade

    def buscar_pokemons(self):
        pokemons = []
        assinaturas_vistas = set()
        tentativas = 0

        while len(pokemons) < self.quantidade and tentativas < 60:
            poke_id = random.randint(1, self.limite_id)
            tentativas += 1
            try:
                resp_pk = requests.get(f"https://pokeapi.co/api/v2/pokemon/{poke_id}").json()
                resp_sp = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{poke_id}").json()
                
                nome = resp_pk['name'].capitalize()
                tipo = resp_pk['types'][0]['type']['name']
                cor = resp_sp['color']['name'] if resp_sp['color'] else "desconhecido"
                formato = resp_sp['shape']['name'] if resp_sp['shape'] else "desconhecido"
                habitat = resp_sp['habitat']['name'] if resp_sp['habitat'] else "desconhecido"
                is_legendary = "sim" if resp_sp['is_legendary'] or resp_sp['is_mythical'] else "nao"
                url_img = resp_pk['sprites']['other']['official-artwork']['front_default']
                
                # Garante que os 12 Pokémons sejam distinguíveis pela IA
                # Cria uma assinatura única baseada em atributos que a IA pode usar para diferenciação
                assinatura = (tipo, cor, formato, habitat, is_legendary)
                
                # Verifica se essa combinação de atributos já foi vista
                # Apenas Pokémons com assinaturas únicas são adicionados
                if assinatura not in assinaturas_vistas:
                    # Adiciona a assinatura ao conjunto para evitar duplicatas
                    assinaturas_vistas.add(assinatura)
                    # Apenas persiste Pokémons com características distintas
                    pokemons.append({
                        "id": poke_id, "nome": nome, "tipo": tipo,
                        "cor": cor, "formato": formato.replace("-", " "),
                        "habitat": habitat, "lendario": is_legendary,
                        "url_img": url_img
                    })
            except Exception as e:
                print(f"Erro ID {poke_id}: {e}")
                
        return pokemons