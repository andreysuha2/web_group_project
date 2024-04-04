def test_create_photo(client, photo):
    response = client.post(
        "/api/photos",
        data=photo,
        files = {"file": ("filename.jpg", "fakeimagecontent", "image/jpeg")},
    )
    assert response.status_code == 200, response.text
    # data = response.json()
    # assert data["first_name"] == photo.get("first_name")
    # assert "id" in data
