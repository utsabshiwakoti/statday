def test_any_website_can_call_the_public_api(client):
    r = client.get("/v1/regions", headers={"Origin": "https://example.com"})
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "*"
