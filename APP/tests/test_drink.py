import pytest
import sys
import os
test_directory = os.path.dirname(os.path.abspath(__file__))
app_directory = os.path.join(test_directory, '..')  
sys.path.append(app_directory)
from server import app

@pytest.fixture
def client():
    client = app.test_client()
    yield client

def test_get_keyword(client):
    response = client.get('/api/v1/hot_drink')

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    data = response.get_json()
    assert 'data' in data
    assert isinstance(data['data'], list)
    assert len(data['data']) >= 1



def test_get_keyword(client):
    response = client.get('/api/v1/hot_drink')

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    data = response.get_json()
    assert 'data' in data
    assert isinstance(data['data'], list)
    assert len(data['data']) >= 1


def test_search_bar(client):
    response = client.post('/search', data={'search': 'coco'})

    assert response.status_code == 200

    response_data = response.get_data(as_text=True)
    assert 'CoCo都可 ' in response_data