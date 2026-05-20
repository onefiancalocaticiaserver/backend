class ErroServico(Exception):
    """Erro esperado da camada de servico."""


class NaoEncontradoError(ErroServico):
    pass


class NaoAutorizadoError(ErroServico):
    pass


class ConflitoError(ErroServico):
    pass


class ValidacaoNegocioError(ErroServico):
    pass
