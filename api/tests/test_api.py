import ast
import random

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def inBulk(d, items):
    for item in items:
        assert item in d


class TestApi:
    token = None

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
        self.__class__.token = content["access_token"]  # pytest is ... and accessing class vars must be done like this

    @pytest.mark.depends(on=['test_login'])  # if test_login fails, this test will be skipped
    def test_token(self):
        assert len(self.__class__.token) > 0

    def test_get_companions(self):
        response = client.get("/companions/?skip=0&limit=100", headers={
            'Authorization': f'Bearer {self.__class__.token}'})
        assert response.status_code == 200
        for companion in response.json():
            inBulk(companion, ["name", "companion_type", "notes", "image", "user_id", "companion"])

    def test_create_companion(self):
        testName = 'test'
        testName += str(random.randint(0, 255))
        msg = {"name": testName,
               "companion_type": random.choice(['cat', 'dog', 'plant', 'reptile']),
               "notes": "none", "image": "none"}
        response = client.post("/users/companions/", headers={
            'Authorization': f'Bearer {self.__class__.token}'}, json=msg)
        companionId = response.content[6]
        print("Content is: ", companionId, response.content[5])
        assert response.status_code == 200

    def test_modify_companion(self):
        response = client.get("/companions/?skip=0&limit=100", headers={
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0MkBlbWFpbC5jb20iLCJleHAiOjE2ODExNzA0NDZ9.LICm3_Tvuu6mB4sxLK-VgX370Y1zSOwmGi5BLh3Mb6A'})
        maxId = max(response.json()["companion"])
        print(maxId)