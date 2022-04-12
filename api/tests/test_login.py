import ast

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestLogin:
    token = None

    def test_users(self):
        response = client.get("/users/")
        assert response.status_code == 200
        for user in response.json():  # loop through list of dicts of user and test for keys
            assert ("username" in user and "is_active" in user and "user_id" in user and "Companions" in user)

    def test_login(self):
        msg = {"username": "test4@email.com", "password": "password"}
        response = client.post(url="/token/", data=msg)
        assert response.status_code == 200
        content = ast.literal_eval(response.content.decode("UTF-8"))  # decodes the response byte string into the dict
        self.__class__.token = content["access_token"]  # pytest is ... and accessing class vars must be done like this

    @pytest.mark.depends(on=['test_login'])  # if test_login fails, this test will be skipped
    def test_token(self):
        assert len(self.__class__.token) > 0
