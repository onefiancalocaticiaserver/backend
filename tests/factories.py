from typing import Any


def payload_imobiliaria(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "razao_social": "Imobiliaria Teste Ltda",
        "nome_fantasia": "Imobiliaria Teste",
        "cnpj": "11.222.333/0001-81",
        "whatsapp": "+55 11 99999-9999",
        "email": "Contato@Teste.com",
        "endereco": "Rua Teste, 100",
        "cidades_ufs_atuacao": [{"cidade": "Sao Paulo", "uf": "SP"}],
        "responsavel_principal": "Maria Silva",
        "cargo_responsavel": "Diretora",
    }
    payload.update(overrides)
    return payload


def payload_corretor(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "nome_completo": "Joao Corretor",
        "cpf": "529.982.247-25",
        "creci": "CRECI-SP 12345",
        "whatsapp": "+55 11 98888-7777",
        "email": "joao.corretor@example.com",
        "cidade": "Sao Paulo",
        "uf": "SP",
        "tipo_corretor": "autonomo",
    }
    payload.update(overrides)
    return payload
