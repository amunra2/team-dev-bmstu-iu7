CLASSES_ENDPOINT = "/classes"
NUM_CLASSES = 3


def test_get_all_classes(client):
    response = client.get(CLASSES_ENDPOINT)

    assert response.status_code == 200
    assert len(response.json) == NUM_CLASSES


def test_get_class_by_id(client):
    class_id = 1

    response = client.get(CLASSES_ENDPOINT + f"/{class_id}")

    assert response.status_code == 200
    assert response.json["week"] == 0
    assert response.json["day"] == 0
    assert response.json["time"] == 0


def test_classes_post(client):
    new_class = {"week": 0, "day": 0, "time": 3}

    response = client.post(CLASSES_ENDPOINT, json=new_class)

    assert response.status_code == 200
    assert response.json["class_id"] == 4


def test_delete_all_classes(client):
    response = client.delete(CLASSES_ENDPOINT)

    assert response.status_code == 200
    assert response.json == NUM_CLASSES
