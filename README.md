# PokeAPI demo: JSON + MongoDB

Este pequeno projeto demonstra como buscar dados da PokeAPI, manipular JSON e persistir em MongoDB.

Requisitos
- Python 3.8+
- MongoDB rodando localmente ou um URI MongoDB Atlas

Instalação
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Executando
```bash
# (Opcional) defina MONGODB_URI se não for usar mongodb://localhost:27017
python3 poke_app.py
```

Arquivos
- `poke_app.py`: script principal que faz as requisições, imprime resultados, salva `poke_data.json` e grava no MongoDB.
- `requirements.txt`: dependências.

Conceitos usados
- **JSON**: formato de intercâmbio de dados. A API retorna JSON, que o script percorre como dicionários/ listas em Python e grava em `poke_data.json`.
- **MongoDB**: banco de documentos NoSQL. O script conecta usando `pymongo` e grava documentos com estrutura parecida ao JSON retornado. Utilizamos `update_one(..., upsert=True)` para criar/atualizar registros.

Notas
- A execução do script requer acesso à internet para acessar `https://pokeapi.co`.
- Se o MongoDB não estiver disponível, o script ainda salvará o arquivo JSON e exibirá mensagens de erro de conexão.
