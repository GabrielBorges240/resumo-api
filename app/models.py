from pydantic import BaseModel, Field


class ResumoRequest(BaseModel):
    texto: str = Field(..., min_length=50, description="Texto a ser resumido")
    tamanho_maximo: int = Field(
        150, gt=0, le=1000, description="Tamanho aproximado do resumo em palavras"
    )


class ResumoResponse(BaseModel):
    resumo: str
    tamanho_original: int
    tamanho_resumo: int


class ErrorResponse(BaseModel):
    detail: str
