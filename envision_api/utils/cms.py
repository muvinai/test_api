import requests
from datetime import datetime
from bson import ObjectId

from config.constants import CMS_API_KEY, CMS_SITE_ID
from utils.logger import log_error

headers = {
    'Authorization': f'Bearer {CMS_API_KEY}',
    'accept-version': '1.0.0',
    'Content-Type': 'application/json',
    'Accept': '*/*',
    'Cache-Control': 'no-cache',
    'Host': 'api.webflow.com',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

url = 'https://api.webflow.com/'


def get_collections():
    r = requests.get(url + f'sites/{CMS_SITE_ID}/collections?live=true', headers=headers)
    return r.json()


def get_schema(collection_id):
    r = requests.get(url + f'collections/{collection_id}?live=true', headers=headers)
    return r.json()


def get_sites():
    r = requests.get(url + 'sites?live=true', headers=headers)
    return r.text


def get_items(collection_id):
    r = requests.get(url + f'collections/{collection_id}/items?live=true', headers=headers)
    response = r.json()
    items = response['items']
    missing_items = response['total'] - response['count']
    reached_items = response['count']
    while missing_items > 0:
        offset = reached_items
        r = requests.get(url + f'collections/{collection_id}/items?live=true&offset={offset}', headers=headers)
        response = r.json()
        missing_items = missing_items - response['count']
        reached_items = reached_items + response['count']
        items.extend(response['items'])
    return items


def get_item(collection_id, item_id):
    r = requests.get(url + f'collections/{collection_id}/items/{item_id}?live=true', headers=headers)
    response = r.json()
    return response


def create_item(collection_id, item):
    for k, v in item.items():
        if isinstance(v, (ObjectId, datetime)):
            item[k] = str(v)
    payload = {
        'fields': item
    }
    r = requests.post(url + f'collections/{collection_id}/items?live=true', json=payload, headers=headers)
    response = {'status': r.status_code}
    if r.status_code >= 400:
        error_name = r.json()['name']
        response['error'] = error_name
        log_error(f'CMS ERROR trying to create item: {error_name}. Response: {r.json()}')
    else:
        response['response'] = r.json()
    return response


def update_item(collection_id, item_id, item):
    for k, v in item.items():
        if isinstance(v, (ObjectId, datetime)):
            item[k] = str(v)
    payload = {
        'fields': item
    }
    r = requests.patch(url + f'collections/{collection_id}/items/{item_id}?live=true', json=payload, headers=headers)
    response = {'status': r.status_code}
    if r.status_code >= 400:
        error_name = r.json()['name']
        response['error'] = error_name
        log_error(f'CMS ERROR trying to update item: {error_name}')
        log_error(r.text)
    else:
        response['response'] = r.json()
    return response


def delete_item(collection_id, item_id):
    r = requests.delete(url + f'collections/{collection_id}/items/{item_id}', headers=headers)
    response = {'status': r.status_code}
    if r.status_code >= 400:
        error_name = r.json()['name']
        response['error'] = error_name
        log_error(f'CMS ERROR trying to delete item: {error_name}')
        log_error(r.text)
    else:
        response['response'] = r.json()
    return response
