from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.llm_client import LLMRateLimitError, LLMServiceError, gerar_resumo
from app.models import ResumoRequest, ResumoResponse

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="API de Resumo de Textos",
    description="API para gerar resumos de textos usando LLM (Claude)",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/resumir", response_model=ResumoResponse)
@limiter.limit("10/minute")
async def resumir(request: Request, req: ResumoRequest):
    try:
        resumo = await gerar_resumo(req.texto, req.tamanho_maximo)

    except LLMRateLimitError:
        raise HTTPException(
            status_code=429,
            detail="Limite de requisições ao serviço de LLM excedido. Tente novamente em instantes.",
        )
    except LLMServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {e}")

    return ResumoResponse(
        resumo=resumo,
        tamanho_original=len(req.texto.split()),
        tamanho_resumo=len(resumo.split()),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
