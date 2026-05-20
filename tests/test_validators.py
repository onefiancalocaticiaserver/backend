import pytest

from app.core.validators import (
    normalizar_email,
    normalizar_whatsapp,
    validar_cnpj,
    validar_cpf,
    validar_creci,
    validar_uf,
)


def test_validadores_normalizam_documentos_contato_e_uf() -> None:
    assert validar_cnpj("11.222.333/0001-81") == "11222333000181"
    assert validar_cpf("529.982.247-25") == "52998224725"
    assert validar_creci(" creci-sp 12345 ") == "CRECI-SP 12345"
    assert normalizar_email("Contato@Example.COM ") == "contato@example.com"
    assert normalizar_whatsapp("+55 11 99999-9999") == "5511999999999"
    assert validar_uf("sp") == "SP"


@pytest.mark.parametrize(
    ("funcao", "valor"),
    [
        (validar_cnpj, "11.111.111/1111-11"),
        (validar_cpf, "111.111.111-11"),
        (validar_creci, "x"),
        (normalizar_email, "email-invalido"),
        (normalizar_whatsapp, "123"),
        (validar_uf, "XX"),
    ],
)
def test_validadores_rejeitam_valores_invalidos(funcao, valor: str) -> None:
    with pytest.raises(ValueError):
        funcao(valor)
