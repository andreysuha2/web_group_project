def test_create_photo(client, photo):
    response = client.post(
        "/api/photos",
        data=photo,
        files = {"file": ("filename.jpg", "fakeimagecontent", "image/jpeg")},
    )
    assert response.status_code == 200, response.text


def test_create_photo_wrong_tag(client, photo_wrong_tag):
    response = client.post(
        "/api/photos",
        data=photo_wrong_tag,
        files = {"file": ("filename.jpg", "fakeimagecontent", "image/jpeg")},
    )
    assert response.status_code == 422


def test_get_photo(client):
    response = client.get(
        "/api/photos/1"
    )
    assert response.status_code == 200


def test_get_absent_photo(client):
    response = client.get(
        "/api/photos/9999"
    )
    assert response.status_code == 404


def test_update_photo(client):
    response = client.put(
        "/api/photos/1",
        data={"photo_update": "test new description"}
    )
    assert response.status_code == 200


def test_update_absent_photo(client):
    response = client.put(
        "/api/photos/9999",
        data={"photo_update": "test new description"}
    )
    assert response.status_code == 404


def test_delete_absent_photo(client):
    response = client.delete(
        "/api/photos/9999",

    )
    assert response.status_code == 404


def test_get_photo_qr_code(client):

    response = client.post(
        "/api/photos/qr/1"
    )

    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/png'


def test_delete_photo(client):
    response = client.delete(
        "/api/photos/1",

    )
    assert response.status_code == 204
