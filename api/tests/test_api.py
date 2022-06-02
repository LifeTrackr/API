import ast

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.schemas import CompanionType


def get_schema_attrs(schema):
    return [a.name for a in schema]


client = TestClient(app)


def inBulk(d, items):
    for item in items:
        assert item in d


class TestApi:
    token = None
    companion_id = []

    def test_users(self):
        response = client.get("/users/")
        assert response.status_code == 200
        for user in response.json():  # loop through list of dicts of user and test for keys
            inBulk(user, ["username", "is_active", "user_id", "Companions"])

    def test_login(self):
        msg = {"username": "test4@email.com", "password": "password"}
        response = client.post(url="/token/", data=msg)
        assert response.status_code == 200
        content = ast.literal_eval(response.content.decode("UTF-8"))  # decodes the response byte string into the dict
        self.__class__.token = content["access_token"]

    @pytest.mark.depends(on=['test_login'])  # if test_login fails, this test will be skipped
    def test_token(self):
        assert len(self.__class__.token) > 0

    def test_get_companions(self):
        auth_header = {'Authorization': f'Bearer {self.__class__.token}'}
        response = client.get("/companions/", headers=auth_header)
        assert response.status_code == 200
        for companion in response.json():  # check all returned companions include correct fields
            inBulk(companion, ["name", "companion_type", "notes", "user_id", "companion"])

    def test_create_companion(self):
        auth_header = {'Authorization': f'Bearer {self.__class__.token}'}
        companion_types = get_schema_attrs(CompanionType)
        msgs = [{"name": "test_cc", "companion_type": companion, "notes": "none"} for companion in companion_types]

        for msg, companion_type in zip(msgs, companion_types):
            response = client.post("/users/companions/", json=msg, headers=auth_header)
            # decodes the response byte string into the dict
            content = ast.literal_eval(response.content.decode("UTF-8"))
            self.__class__.companion_id.append(content["companion"])
            assert response.status_code == 200
            assert content["companion_type"] == companion_type

    @pytest.mark.depends(on=['test_create_companion'])  # if test_login fails, this test will be skipped
    def test_modify_companion(self):
        auth_header = {'Authorization': f'Bearer {self.__class__.token}'}
        msg = {"name": "Changed", "companion_type": "plant", "notes": "string", "image": "string"}
        response = client.put(f"/users/companions/?companion_id={self.__class__.companion_id[0]}", json=msg,
                              headers=auth_header)
        content = ast.literal_eval(response.content.decode("UTF-8"))  # decodes the response byte string into the dict
        assert int(content["row_id"]) > 0
        assert content["operation"] == "update"
        assert content["rows_modified"] == 1
        assert content["table"] == "Companion"

    @pytest.mark.depends(on=['test_modify_companion'])
    def test_get_all_companions(self):
        auth_header = {'Authorization': f'Bearer {self.__class__.token}'}
        response = client.get(f"/companions/", headers=auth_header).json()
        response_companion_ids = [companion["companion"] for companion in response]
        for companion_id in self.__class__.companion_id:
            assert companion_id in response_companion_ids

    @pytest.mark.depends(on=['test_get_all_companions'])
    def test_delete_companion(self):
        auth_header = {'Authorization': f'Bearer {self.__class__.token}'}
        for companion_id in self.__class__.companion_id:
            response = client.delete(f"/users/companions/{companion_id}/", headers=auth_header).json()
            assert int(response["row_id"]) == companion_id
            assert response["operation"] == "delete"
            assert response["rows_modified"] == 1
            assert response["table"] == "Companion"
