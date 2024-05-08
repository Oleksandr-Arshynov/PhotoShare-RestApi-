
def test_get_me_info(client, token_admin):
    response = client.get(
            f"/api/user",
            headers={"Authorization": f"Bearer {token_admin}"}
        )
    
    assert response.status_code == 200, "OK"
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "Admin"
    assert data["email"] == "Admin@gmail.com"
    assert data["role_id"] == 1

def test_user_info(client, token_admin):
    username = "Admin"
    response = client.post(
            f"/api/user/{username}",
            headers={"Authorization": f"Bearer {token_admin}"}
        )
    
    assert response.status_code == 200, "OK"
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "Admin"
    assert data["email"] == "Admin@gmail.com"
    assert data["role_id"] == 1


