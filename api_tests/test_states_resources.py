def test_classrooms_post(client):
    classroom_id = 10
    class_id = 15

    endpoint = f"/classrooms/{classroom_id}/classes/{class_id}"
    response = client.post(endpoint)

    assert response.status_code == 200
