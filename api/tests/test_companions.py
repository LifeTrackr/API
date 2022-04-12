import random

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestCompanions:
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0MkBlbWFpbC5jb20iLCJleHAiOjE2ODExNzA0NDZ9.LICm3_Tvuu6mB4sxLK-VgX370Y1zSOwmGi5BLh3Mb6A'

    def test_get_companions(self):
        response = client.get("/companions/?skip=0&limit=100", headers={'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0MkBlbWFpbC5jb20iLCJleHAiOjE2ODExNzA0NDZ9.LICm3_Tvuu6mB4sxLK-VgX370Y1zSOwmGi5BLh3Mb6A'})
        assert response.status_code == 200
        for companion in response.json():
            assert (
                        "name" in companion and "companion_type" in companion and "notes" in companion and "image" in companion and "user_id" in companion and "companion" in companion)

    def test_create_companion(self):
        testName = 'test'
        testName += str(random.randint(0, 255))
        msg = {"name": testName,
               "companion_type": random.choice(['cat', 'dog', 'plant', 'reptile']),
               "notes": "none", "image": "none"}
        response = client.post("/users/companions/", headers={
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0MkBlbWFpbC5jb20iLCJleHAiOjE2ODExNzA0NDZ9.LICm3_Tvuu6mB4sxLK-VgX370Y1zSOwmGi5BLh3Mb6A'},
                               json=msg)
        assert response.status_code == 200
