# API de Resumo de Textos

API REST assíncrona construída com **FastAPI** que usa a API da **Anthropic (Claude)** para gerar resumos de textos.

## Stack

- **FastAPI** — framework web assíncrono
- **Pydantic v2** — validação de dados e configurações
- **Anthropic SDK (async)** — chamadas ao LLM
- **slowapi** — rate limiting
- **pytest + httpx** — testes automatizados
- **Docker** — containerização

## Funcionalidades

- Endpoint para resumir textos com tamanho configurável
- Validação de entrada (tamanho mínimo do texto, limites do resumo)
- Rate limiting (10 requisições/minuto por IP)
- Tratamento de erros específico (rate limit do LLM, falhas de conexão, erros de validação)
- Healthcheck para orquestração (Docker/Kubernetes)
- Documentação automática via Swagger (`/docs`)

## Rodando localmente

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edite o .env e coloque sua ANTHROPIC_API_KEY

uvicorn app.main:app --reload
```

Acesse a documentação interativa em `http://localhost:8000/docs`.

## Rodando com Docker

```bash
docker compose up --build
```

## Testes

```bash
pytest tests/ -v
```

Os testes usam mocks para a chamada ao LLM, então não é necessário ter uma API key válida nem gastar créditos para rodá-los.

## Exemplo de uso

```bash
curl -X POST http://localhost:8000/resumir \
  -H "Content-Type: application/json" \
  -d '{
    "texto": "Seu texto longo aqui...",
    "tamanho_maximo": 100
  }'
```

Resposta:

```json
{
  "resumo": "Resumo gerado pelo modelo...",
  "tamanho_original": 320,
  "tamanho_resumo": 98
}
```

## Estrutura do projeto

```
resumo-api/
├── app/
│   ├── main.py         # rotas e configuração da aplicação
│   ├── models.py       # schemas Pydantic
│   ├── llm_client.py   # cliente assíncrono para o LLM
│   └── config.py       # configurações via variáveis de ambiente
├── tests/
│   └── test_main.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Próximos passos (roadmap)

- [ ] Cache de resumos (Redis) para textos repetidos
- [ ] Suporte a streaming da resposta
- [ ] Autenticação via API key própria
- [ ] Observabilidade (logs estruturados + métricas)
