import yaml

class YamlKnowledgeBuilder:
    def gerar_base_conhecimento(self, pokemons, caminho="conhecimento.yaml"):
        perguntas = {}
        regras = []
        
        for p in pokemons:
            f_tipo = f"tipo_{p['tipo']}"
            f_cor = f"cor_{p['cor']}"
            f_formato = f"formato_{p['formato'].replace(' ', '_')}"
            f_habitat = f"habitat_{p['habitat']}"
            f_lendario = f"lendario_{p['lendario']}"
            
            perguntas[f_tipo] = f"O seu Pokémon é do tipo {p['tipo'].upper()}?"
            perguntas[f_cor] = f"O seu Pokémon é da cor {p['cor'].upper()}?"
            perguntas[f_formato] = f"O seu Pokémon tem o formato {p['formato'].upper()}?"
            perguntas[f_habitat] = f"O seu Pokémon vive no habitat: {p['habitat'].upper()}?"
            
            status_lendario = "LENDÁRIO" if p['lendario'] == 'sim' else "COMUM (Não Lendário)"
            perguntas[f_lendario] = f"O seu Pokémon é classificado como {status_lendario}?"
            
            regras.append({
                "se": [f_tipo, f_cor, f_formato, f_habitat, f_lendario],
                "entao": f"Diagnóstico: {p['nome']}"
            })
            
        conhecimento = {"perguntas": perguntas, "regras": regras}
        with open(caminho, 'w', encoding='utf-8') as f:
            yaml.dump(conhecimento, f, allow_unicode=True, sort_keys=False)
        return caminho