import ast
import random

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.schemas import CompanionType, CompanionEvents


def get_schema_attrs(schema):
    return [a.value for a in schema]


client = TestClient(app)


def inBulk(d, items):
    for item in items:
        assert item in d


class TestApi:
    companion_ids = []
    event_ids = []
    auth_header = None

    def get_header(self):
        return self.__class__.auth_header

    def test_users(self):
        response = client.get("/users/")
        assert response.status_code == 200
        for user in response.json():  # loop through list of dicts of user and test for keys
            inBulk(user, ["username", "first_name", "last_name", "is_active", "user_id", "Companions"])

    @pytest.mark.depends(on=['test_users'])
    def test_login(self):
        msg = {"username": "test@email.com", "password": "password"}
        response = client.post(url="/token/", data=msg)
        content = ast.literal_eval(response.content.decode("UTF-8"))  # decodes the response byte string into the dict
        self.__class__.auth_header = {'Authorization': f'Bearer {content["access_token"]}'}
        assert response.status_code == 200

    @pytest.mark.depends(on=['test_login'])
    def test_get_companions(self):
        response = client.get("/companions/", headers=self.get_header())
        assert response.status_code == 200
        for companion in response.json():  # check all returned companions include correct fields
            inBulk(companion, ["name", "companion_type", "notes", "user_id", "companion"])

    @pytest.mark.depends(on=['test_get_companions'])
    def test_create_companion(self):
        companion_types = get_schema_attrs(CompanionType)
        msgs = [{"name": "test_cc", "companion_type": companion, "notes": "none"} for companion in companion_types]
        for msg, companion_type in zip(msgs, companion_types):
            response = client.post("/users/companions/", json=msg, headers=self.__class__.auth_header)
            # decodes the response byte string into the dict
            content = ast.literal_eval(response.content.decode("UTF-8"))
            assert "companion" in content
            self.__class__.companion_ids.append(content["companion"])
            assert response.status_code == 200
            assert content["companion_type"] == companion_type

    @pytest.mark.depends(on=['test_create_companion'])
    def test_modify_companion(self):
        msg = {"name": "Changed", "companion_type": "plant", "notes": "string", "image": "string"}
        response = client.put(f"/users/companions/?companion_id={self.__class__.companion_ids[0]}", json=msg,
                              headers=self.get_header())
        content = ast.literal_eval(response.content.decode("UTF-8"))
        assert int(content["row_id"]) > 0
        assert content["operation"] == "update"
        assert content["rows_modified"] == 1
        assert content["table"] == "Companion"

    @pytest.mark.depends(on=['test_modify_companion'])
    def test_get_all_companions(self):
        response = client.get(f"/companions/", headers=self.get_header()).json()
        response_companion_ids = [companion["companion"] for companion in response]
        for companion_id in self.__class__.companion_ids:
            assert companion_id in response_companion_ids

    @pytest.mark.depends(on=['test_get_all_companions'])
    def test_create_event(self):
        companion_events = random.sample(get_schema_attrs(CompanionEvents), 3)
        opts = [("l", 20, companion_events[0]), ("m", 15, companion_events[1]), ("h", 5, companion_events[2])]
        msgs = [{"name": "test_event", "notes": "testing", "priority": opt[0], "frequency": opt[1], "action": opt[2]}
                for opt in opts]

        for i, msg in enumerate(msgs):
            response = client.post(f"/companions/event/?companion_id={self.__class__.companion_ids[i]}", json=msg,
                                   headers=self.get_header()).json()
            self.__class__.event_ids.append(response["event_id"])
            assert response["name"] == msg["name"]
            assert response["notes"] == msg["notes"]
            assert response["priority"] == msg["priority"]
            assert response["frequency"] == msg["frequency"]
            assert response["action"] == msg["action"]

    @pytest.mark.depends(on=['test_create_event'])
    def test_get_all_events(self):
        response = client.get("/companions/event/", headers=self.get_header()).json()
        for event in response:
            pass

    @pytest.mark.depends(on=['test_get_all_events'])
    def test_modify_event(self):
        pass

    @pytest.mark.depends(on=['test_modify_event'])
    def test_event_trigger(self):
        pass

    @pytest.mark.depends(on=['test_get_all_companions'])
    def test_delete_companion(self):
        for companion_id in self.__class__.companion_ids:
            response = client.delete(f"/users/companions/{companion_id}/", headers=self.get_header()).json()
            assert int(response["row_id"]) == companion_id
            assert response["operation"] == "delete"
            assert response["rows_modified"] == 1
            assert response["table"] == "Companion"
