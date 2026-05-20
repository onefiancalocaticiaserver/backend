from fastapi.testclient import TestClient

from tests.factories import payload_corretor, payload_imobiliaria


def test_crud_publico_imobiliaria_exige_token_de_cadastro(client: TestClient) -> None:
    criar_response = client.post("/v1/publico/imobiliarias", json=payload_imobiliaria())
    assert criar_response.status_code == 201
    body = criar_response.json()
    imobiliaria_id = body["id"]
    token = body["token_cadastro"]
    assert token

    sem_token = client.get(f"/v1/publico/imobiliarias/{imobiliaria_id}")
    assert sem_token.status_code == 422

    token_errado = client.get(
        f"/v1/publico/imobiliarias/{imobiliaria_id}",
        headers={"X-Cadastro-Token": "errado"},
    )
    assert token_errado.status_code == 403

    obter_response = client.get(
        f"/v1/publico/imobiliarias/{imobiliaria_id}",
        headers={"X-Cadastro-Token": token},
    )
    assert obter_response.status_code == 200
    assert obter_response.json()["nome_fantasia"] == "Imobiliaria Teste"

    atualizar_response = client.patch(
        f"/v1/publico/imobiliarias/{imobiliaria_id}",
        headers={"X-Cadastro-Token": token},
        json={"nome_fantasia": "Imobiliaria Atualizada"},
    )
    assert atualizar_response.status_code == 200
    assert atualizar_response.json()["nome_fantasia"] == "Imobiliaria Atualizada"


def test_criacao_publica_corretor_autonomo_remove_imobiliaria_vinculada(
    client: TestClient,
) -> None:
    imobiliaria_response = client.post("/v1/publico/imobiliarias", json=payload_imobiliaria())
    assert imobiliaria_response.status_code == 201
    imobiliaria_id = imobiliaria_response.json()["id"]

    criar_response = client.post(
        "/v1/publico/corretores",
        json=payload_corretor(imobiliaria_vinculada_id=imobiliaria_id),
    )
    assert criar_response.status_code == 201
    body = criar_response.json()

    obter_response = client.get(
        f"/v1/publico/corretores/{body['id']}",
        headers={"X-Cadastro-Token": body["token_cadastro"]},
    )
    assert obter_response.status_code == 200
    assert obter_response.json()["tipo_corretor"] == "autonomo"
    assert obter_response.json()["imobiliaria_vinculada_id"] is None
