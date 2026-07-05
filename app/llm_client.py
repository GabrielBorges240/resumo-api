import anthropic
from anthropic import AsyncAnthropic

from app.config import settings

client = AsyncAnthropic(api_key=settings.anthropic_api_key)


class LLMRateLimitError(Exception):
    """Levantado quando a API do LLM retorna 429 (rate limit)."""


class LLMServiceError(Exception):
    """Levantado para outros erros da API do LLM (5xx, timeout, etc.)."""


async def gerar_resumo(texto: str, tamanho_maximo: int) -> str:
    try:
        response = await client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Resuma o texto abaixo em até {tamanho_maximo} palavras, "
                        f"mantendo as ideias centrais e sem adicionar comentários extras:\n\n{texto}"
                    ),
                }
            ],
        )
        return response.content[0].text

    except anthropic.RateLimitError as e:
        raise LLMRateLimitError("Limite de requisições ao LLM excedido") from e

    except anthropic.APIStatusError as e:
        raise LLMServiceError(f"Erro na API do LLM: {e.status_code}") from e

    except anthropic.APIConnectionError as e:
        raise LLMServiceError("Falha de conexão com a API do LLM") from e
