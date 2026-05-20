from fastapi.testclient import TestClient

from tests.factories import payload_corretor, payload_imobiliaria


def test_crud_admin_exige_jwt_e_soft_delete_remove_da_listagem(
    client: TestClient,
    admin_token: str,
) -> None:
    sem_jwt = client.get("/v1/admin/imobiliarias")
    assert sem_jwt.status_code == 401

    criar_response = client.post("/v1/publico/imobiliarias", json=payload_imobiliaria())
    assert criar_response.status_code == 201
    imobiliaria_id = criar_response.json()["id"]

    headers = {"Authorization": f"Bearer {admin_token}"}
    listar_response = client.get("/v1/admin/imobiliarias", headers=headers)
    assert listar_response.status_code == 200
    assert [item["id"] for item in listar_response.json()] == [imobiliaria_id]

    atualizar_response = client.patch(
        f"/v1/admin/imobiliarias/{imobiliaria_id}",
        headers=headers,
        json={"status": "ativo", "observacoes_internas": "validada"},
    )
    assert atualizar_response.status_code == 200
    assert atualizar_response.json()["status"] == "ativo"

    remover_response = client.delete(f"/v1/admin/imobiliarias/{imobiliaria_id}", headers=headers)
    assert remover_response.status_code == 200

    listar_apos_delete = client.get("/v1/admin/imobiliarias", headers=headers)
    assert listar_apos_delete.status_code == 200
    assert listar_apos_delete.json() == []


def test_admin_vincula_corretor_a_imobiliaria(client: TestClient, admin_token: str) -> None:
    imobiliaria_response = client.post("/v1/publico/imobiliarias", json=payload_imobiliaria())
    assert imobiliaria_response.status_code == 201
    imobiliaria_id = imobiliaria_response.json()["id"]

    corretor_response = client.post("/v1/publico/corretores", json=payload_corretor())
    assert corretor_response.status_code == 201
    corretor_id = corretor_response.json()["id"]

    headers = {"Authorization": f"Bearer {admin_token}"}
    vincular_response = client.post(
        f"/v1/admin/imobiliarias/{imobiliaria_id}/corretores/{corretor_id}",
        headers=headers,
    )
    assert vincular_response.status_code == 200
    assert vincular_response.json() == {"mensagem": "corretor_vinculado"}

    obter_response = client.get(f"/v1/admin/corretores/{corretor_id}", headers=headers)
    assert obter_response.status_code == 200
    assert obter_response.json()["tipo_corretor"] == "vinculado_imobiliaria"
    assert obter_response.json()["imobiliaria_vinculada_id"] == imobiliaria_id
