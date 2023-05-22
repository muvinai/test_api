from fastapi.testclient import TestClient
from datetime import datetime
import json

from .conftest import verify_environment, DummyAdmins
from config.db import conn
from main import app

client = TestClient(app)


@verify_environment
def test_find_talents(mongo_empty, mongo_insert_dummy_talents):
    filters = json.dumps({'q': 'name'})
    response = client.get('/talents/', params=f'filter={filters}', headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 200
    assert len(response.json()['results']) == 1

    filters = json.dumps({'q': 'not found'})
    response = client.get('/talents/', params=f'filter={filters}', headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 200
    assert len(response.json()['results']) == 0

    response = client.get('/talents/', headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 200
    assert len(response.json()['results']) == 2


@verify_environment
def test_insert_and_get_talent(mongo_empty, mock_cms):
    talent = {
        'name': 'Test name',
        'envision_festival': False,
        'slug': 'slug-1'
    }
    response = client.post('/talents/', json=talent, headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 201
    assert response.json()['name'] == talent['name']
    assert response.json()['envision_festival'] == talent['envision_festival']
    assert response.json()['slug'] == talent['slug']

    talent_id = response.json()['id']
    response = client.get(f'/talents/{talent_id}', headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 200
    assert response.json()['name'] == talent['name']
    assert response.json()['envision_festival'] == talent['envision_festival']
    assert response.json()['slug'] == talent['slug']


@verify_environment
def test_create_talent_stage_not_found(mongo_empty, mongo_insert_dummy_talents, mock_thinkific):
    talent = {
        'name': 'Test name',
        'envision_festival': False,
        'slug': 'slug-1',
        'main_stage': '63e3c3546a45ecc5d5698d36'
    }
    response = client.post('/talents/', json=talent, headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 404


@verify_environment
def test_get_talent_not_found(mongo_empty):
    talent_id = '63f1937484c3af471a5f044c'
    response = client.get(f'/talents/{talent_id}', headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 404


@verify_environment
def test_update_talent_not_found(mongo_empty):
    talent_id = '63f1937484c3af471a5f044c'
    response = client.put(f'/talents/{talent_id}', json={'name': 'new name'},
                          headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 404


@verify_environment
def test_update_talent(mongo_empty, mongo_insert_dummy_talents):
    talent = conn.talents.find_one({'deleted': False})
    talent_id = str(talent['_id'])
    new_name = 'new name'
    last_modified = datetime.utcnow()
    response = client.put(f'/talents/{talent_id}', json={'name': new_name},
                          headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 200
    assert response.json()['name'] == new_name
    assert response.json()['envision_festival'] == talent['envision_festival']
    assert response.json()['slug'] == talent['slug']

    response = client.get('/talents/', params=f'last_modified={last_modified}',
                          headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 200
    assert len(response.json()['results']) == 1
    assert response.json()['results'][0]['name'] == new_name
    assert response.json()['results'][0]['envision_festival'] == talent['envision_festival']
    assert response.json()['results'][0]['slug'] == talent['slug']


@verify_environment
def test_find_talent_filters(mongo_empty, mongo_insert_dummy_talents):
    talent = conn.talents.find_one({'deleted': False})
    value = talent['slug']
    response = client.get('/talents/', params=f'slug={value}', headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 200
    assert len(response.json()['results']) > 0

    value = talent['email']
    response = client.get('/talents/', params=f'email={value}', headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 200
    assert len(response.json()['results']) > 0

    value = talent['envision_festival']
    response = client.get('/talents/', params=f'envision_festival={value}',
                          headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 200
    assert len(response.json()['results']) > 0


@verify_environment
def test_update_talent_stage_not_found(mongo_empty, mongo_insert_dummy_talents):
    talent = conn.talents.find_one({'deleted': False})
    talent_id = str(talent['_id'])
    response = client.put(f'/talents/{talent_id}', json={'main_stage': '63e3c3546a45ecc5d5698d36'},
                          headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 404


@verify_environment
def test_delete_talent_not_found(mongo_empty):
    talent_id = '63f1937484c3af471a5f044c'
    response = client.delete(f'/talents/{talent_id}', headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 404


@verify_environment
def test_delete_talent(mongo_empty, mongo_insert_dummy_talents):
    talent = conn.talents.find_one({'deleted': False})
    talent_id = str(talent['_id'])
    response = client.delete(f'/talents/{talent_id}', headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 204


@verify_environment
def test_delete_talent_with_event(mongo_empty, mongo_insert_dummy_talents, mongo_insert_dummy_events):
    talent = conn.talents.find_one({'deleted': False})
    event_id = conn.events.find_one({'deleted': False}, {'_id': 1})['_id']
    r = conn.events.update_one({'_id': event_id}, {'$set': {'talents_ids': [talent['_id']]}})
    assert r.modified_count == 1
    talent_id = str(talent['_id'])
    response = client.delete(f'/talents/{talent_id}', headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 400

    r = conn.events.update_one({'_id': event_id}, {'$set': {'deleted': True}})
    assert r.modified_count == 1
    talent_id = str(talent['_id'])
    response = client.delete(f'/talents/{talent_id}', headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 204


@verify_environment
def test_get_talent_categories(mongo_empty, mongo_insert_dummy_talents):
    response = client.get(f'/talents/categories', headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 200
    results = response.json()['results']
    assert isinstance(results, list)
    for c in results:
        assert isinstance(c, str)


@verify_environment
def test_create_ethos_instructor(mongo_empty, mongo_insert_dummy_talents, mock_thinkific):
    talent = conn.talents.find_one({'deleted': False, 'ethos_id': None})
    assert talent['ethos_id'] is None
    talent_id = str(talent['_id'])
    response = client.put(f'/talents/{talent_id}/create_ethos', headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 200
    assert response.json()['name'] == talent['name']
    assert response.json()['ethos_id'] is not None


@verify_environment
def test_create_ethos_instructor_already_in_ethos(mongo_empty, mongo_insert_dummy_talents, mock_thinkific):
    talent = conn.talents.find_one({'deleted': False, 'ethos_id': {'$exists': True, '$ne': None}})
    assert isinstance(talent['ethos_id'], int)
    talent_id = str(talent['_id'])
    response = client.put(f'/talents/{talent_id}/create_ethos', headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 200
    assert response.json()['name'] == talent['name']
    assert response.json()['ethos_id'] == talent['ethos_id']


@verify_environment
def test_create_ethos_instructor_not_found(mongo_empty, mongo_insert_dummy_talents, mock_thinkific):
    talent_id = '63f1937484c3af471a5f044c'
    response = client.put(f'/talents/{talent_id}/create_ethos', headers={'Authorization': DummyAdmins.admin_token})
    assert response.status_code == 404
