class TestUsers:
    def test_create_user(self, client):
        response = client.post("/v2/user", json={
            "email": "test@example.com",
            "password": "secret123",
        })
        assert response.status_code == 201
        assert response.json()["email"] == "test@example.com"
        assert response.json()["tokens"] == 10  # new users always start with 10

    def test_duplicate_user(self, client):
        client.post("/v2/user", json={
            "email": "dupe@test.com", "password": "secret123",
        })
        response = client.post("/v2/user", json={  # same email again, should fail
            "email": "dupe@test.com", "password": "other456",
        })
        assert response.status_code == 409

    def test_get_user(self, client):
        create_response = client.post("/v2/user", json={
            "email": "find@test.com", "password": "secret123",
        })
        user_id = create_response.json()["id"]  # need the id to fetch the user
        response = client.get(f"/v2/user/{user_id}")
        assert response.status_code == 200
        assert response.json()["email"] == "find@test.com"

    def test_delete_user(self, client):
        create_response = client.post("/v2/user", json={
            "email": "delete@test.com", "password": "secret123",
        })
        user_id = create_response.json()["id"]
        response = client.delete(f"/v2/user/{user_id}")
        assert response.status_code == 204


class TestTokens:
    # this worked in assignment 1, endpoint changed in assignment 2 to use token shop
    # so it needs a running container
    #
    # def test_add_tokens(self, client):
    #     create_response = client.post("/v2/user", json={
    #         "email": "token@test.com", "password": "secret123",
    #     })
    #     user_id = create_response.json()["id"]
    #     response = client.post("/v2/tokens", json={
    #         "user_id": user_id, "amount": 5,
    #     })
    #     assert response.json()["tokens"] == 15

    def test_token_consumption(self, client):
        create_response = client.post("/v2/user", json={
            "email": "consume@test.com", "password": "secret123",
        })
        user_id = create_response.json()["id"]

        client.get("/v2/country/JAM", headers={"X-User-Id": user_id})  # costs 1 token

        response = client.get(f"/v2/user/{user_id}")
        assert response.json()["tokens"] == 9

    def test_no_tokens_returns_403(self, client):
        create_response = client.post("/v2/user", json={
            "email": "broke@test.com", "password": "secret123",
        })
        user_id = create_response.json()["id"]

        for _ in range(10):  # use all 10 tokens
            client.get("/v2/country/JAM", headers={"X-User-Id": user_id})

        response = client.get("/v2/country/JAM", headers={"X-User-Id": user_id})  # 11th call, no tokens left
        assert response.status_code == 403


class TestDataEndpoints:
    def test_get_athlete_returns_data(self, client):
        create_response = client.post("/v2/user", json={  # data endpoints need a user with tokens
            "email": "data@test.com",
            "password": "secret123",
        })
        user_id = create_response.json()["id"]

        response = client.get(  # 2 usain bolt records seeded in conftest
            "/v2/athlete/Usain-Bolt",
            headers={"X-User-Id": user_id},
        )

        assert response.status_code == 200
        assert response.json()["count"] == 2
        assert response.json()["results"][0]["noc"] == "JAM"

    def test_get_country_returns_data(self, client):
        create_response = client.post("/v2/user", json={
            "email": "country@test.com",
            "password": "secret123",
        })
        user_id = create_response.json()["id"]

        response = client.get(  # petter northug is NOR, seeded in conftest
            "/v2/country/NOR",
            headers={"X-User-Id": user_id},
        )

        response_body = response.json()

        assert response.status_code == 200
        assert "Skiing" in response_body["sports"]

    def test_get_sport_returns_data(self, client):
        create_response = client.post("/v2/user", json={
            "email": "sport@test.com",
            "password": "secret123",
        })
        user_id = create_response.json()["id"]

        response = client.get(  # 2 athletics records seeded in conftest
            "/v2/sport/Athletics",
            headers={"X-User-Id": user_id},
        )

        assert response.status_code == 200
        assert response.json()["count"] == 2

    def test_athlete_not_found_does_not_deduct_token(self, client):
        create_response = client.post("/v2/user", json={
            "email": "nodeduce@test.com",
            "password": "secret123",
        })
        user_id = create_response.json()["id"]

        client.get(  # this athlete doesnt exist, should return 404
            "/v2/athlete/nobody-ever",
            headers={"X-User-Id": user_id},
        )

        user_response = client.get(f"/v2/user/{user_id}")
        token_count = user_response.json()["tokens"]

        assert token_count == 10  # should still be 10, failed requests dont cost tokens
