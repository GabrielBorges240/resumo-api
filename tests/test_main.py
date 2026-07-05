import os
from unittest.mock import AsyncMock, patch

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-fake")

import pytest
from httpx import ASGITransport, AsyncClient

from app.llm_client import LLMRateLimitError, LLMServiceError
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_resumir_sucesso(client):
    texto_longo = "Este é um texto de teste bem grande. " * 5  # >50 chars

    with patch("app.main.gerar_resumo", new=AsyncMock(return_value="Resumo gerado pelo mock.")):
        response = await client.post(
            "/resumir",
            json={"texto": texto_longo, "tamanho_maximo": 50},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["resumo"] == "Resumo gerado pelo mock."
    assert data["tamanho_original"] == len(texto_longo.split())
    assert data["tamanho_resumo"] == 4


@pytest.mark.asyncio
async def test_resumir_texto_muito_curto(client):
    response = await client.post("/resumir", json={"texto": "curto", "tamanho_maximo": 50})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_resumir_rate_limit_do_llm(client):
    texto_longo = "Texto suficientemente longo para passar na validação. " * 3

    with patch(
        "app.main.gerar_resumo",
        new=AsyncMock(side_effect=LLMRateLimitError("limite excedido")),
    ):
        response = await client.post("/resumir", json={"texto": texto_longo})

    assert response.status_code == 429


@pytest.mark.asyncio
async def test_resumir_erro_de_servico(client):
    texto_longo = "Texto suficientemente longo para passar na validação. " * 3

    with patch(
        "app.main.gerar_resumo",
        new=AsyncMock(side_effect=LLMServiceError("erro 503")),
    ):
        response = await client.post("/resumir", json={"texto": texto_longo})

    assert response.status_code == 502
