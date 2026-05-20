from typing import NoReturn

from fastapi import HTTPException, status

from app.services.exceptions import (
    ConflitoError,
    ErroServico,
    NaoAutorizadoError,
    NaoEncontradoError,
    ValidacaoNegocioError,
)


def converter_erro_servico(exc: ErroServico) -> NoReturn:
    if isinstance(exc, NaoEncontradoError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, NaoAutorizadoError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    if isinstance(exc, ConflitoError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if isinstance(exc, ValidacaoNegocioError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
