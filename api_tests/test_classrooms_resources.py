CLASSROOMS_ENDPOINT = "/classrooms"
NUM_CLASSROOMS = 3


def test_get_all_classrooms(client):
    response = client.get(CLASSROOMS_ENDPOINT)

    assert response.status_code == 200
    assert len(response.json) == NUM_CLASSROOMS


def test_get_classroom_by_id(client):
    classroom_id = 2

    response = client.get(CLASSROOMS_ENDPOINT + f"/{classroom_id}")

    assert response.status_code == 200
    assert response.json["building"] == "ULK"
    assert response.json["floor"] == 5
    assert response.json["number"] == "511л"


def test_classrooms_post(client):
    new_classroom = {"building": "ENERGO", "floor": 2, "number": "203э"}

    response = client.post(CLASSROOMS_ENDPOINT, json=new_classroom)

    assert response.status_code == 200
    assert response.json["classroom_id"] == 4


def test_delete_all_classrooms(client):
    response = client.delete(CLASSROOMS_ENDPOINT)

    assert response.status_code == 200
    assert response.json == NUM_CLASSROOMS
