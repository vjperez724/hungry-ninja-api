def test_app_runs(client):
    response = client.get("/docs")
    assert response.status_code == 200
