import requests

from config.constants import THINKIFIC_API_KEY, THINKIFIC_SUBDOMAIN
from utils.logger import logger

headers = {
    'X-Auth-API-Key': THINKIFIC_API_KEY,
    'X-Auth-Subdomain': THINKIFIC_SUBDOMAIN,
    'Content-Type': 'application/json'
}

url = 'https://api.thinkific.com/api/public/v1'


def get_items(collection: str, query: dict = None):
    params = {'limit': 50}
    if query:
        for k, v in query.items():
            params[f'query[{k}]'] = v
    r = requests.get(f'{url}/{collection}', headers=headers, params=params)
    if r.status_code >= 400:
        return []
    response = r.json()
    items = response['items']
    pagination_info = response['meta']['pagination']
    while pagination_info['current_page'] < pagination_info['total_pages']:
        params['page'] = params['page'] + 1 if 'page' in params else 2
        r = requests.get(f'{url}/{collection}', headers=headers, params=params)
        if r.status_code >= 400:
            return items
        response = r.json()
        pagination_info = response['meta']['pagination']
        items.extend(response['items'])
    return items


def get_item(collection, item_id):
    r = requests.get(f'{url}/{collection}/{item_id}', headers=headers)
    response = r.json()
    return response


def create_item(collection, item):
    r = requests.post(f'{url}/{collection}', json=item, headers=headers)
    response = {'status': r.status_code}
    if r.status_code >= 400:
        r_json = r.json()
        response['error'] = None
        response['error'] = r_json['error'] if 'error' in r_json else response['error']
        response['error'] = r_json['errors'] if 'errors' in r_json else response['error']
    else:
        response['response'] = r.json()
    logger.info(f'Thinkific: Create item at {collection} collection. status_code={r.status_code}')
    return response


def update_item(collection, item_id, item):
    r = requests.put(f'{url}/{collection}/{item_id}', json=item, headers=headers)
    response = {'status': r.status_code}
    if r.status_code >= 400:
        response['error'] = r.json()['error']
    logger.info(f'Thinkific: Update item {item_id} from {collection} collection. status_code={r.status_code}')
    return response


def delete_item(collection, item_id):
    r = requests.delete(f'{url}/{collection}/{item_id}', headers=headers)
    response = {'status': r.status_code}
    if r.status_code >= 400:
        response['error'] = r.json()['error'] if 'error' in r.json() else r.json()['errors']
    logger.info(f'Thinkific: Delete item {item_id} from {collection} collection. status_code={r.status_code}')
    return response
