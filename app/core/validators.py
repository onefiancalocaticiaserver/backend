import re

from pydantic import EmailStr, TypeAdapter

UFS = {
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
}

EMAIL_ADAPTER = TypeAdapter(EmailStr)


def somente_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor)


def normalizar_email(valor: str) -> str:
    return str(EMAIL_ADAPTER.validate_python(valor.strip().lower()))


def normalizar_whatsapp(valor: str) -> str:
    digitos = somente_digitos(valor)
    if len(digitos) < 10 or len(digitos) > 13:
        raise ValueError("whatsapp deve ter entre 10 e 13 digitos")
    return digitos


def validar_uf(valor: str) -> str:
    uf = valor.strip().upper()
    if uf not in UFS:
        raise ValueError("UF invalida")
    return uf


def validar_creci(valor: str) -> str:
    creci = valor.strip().upper()
    if len(creci) < 3 or len(creci) > 40:
        raise ValueError("CRECI invalido")
    return creci


def validar_cpf(valor: str) -> str:
    cpf = somente_digitos(valor)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValueError("CPF invalido")

    for tamanho in (9, 10):
        soma = sum(int(cpf[i]) * (tamanho + 1 - i) for i in range(tamanho))
        digito = (soma * 10) % 11
        if digito == 10:
            digito = 0
        if digito != int(cpf[tamanho]):
            raise ValueError("CPF invalido")
    return cpf


def validar_cnpj(valor: str) -> str:
    cnpj = somente_digitos(valor)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        raise ValueError("CNPJ invalido")

    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos_2 = [6, *pesos_1]

    def calcula_digito(base: str, pesos: list[int]) -> int:
        soma = sum(int(digito) * peso for digito, peso in zip(base, pesos, strict=True))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    if calcula_digito(cnpj[:12], pesos_1) != int(cnpj[12]):
        raise ValueError("CNPJ invalido")
    if calcula_digito(cnpj[:13], pesos_2) != int(cnpj[13]):
        raise ValueError("CNPJ invalido")
    return cnpj
