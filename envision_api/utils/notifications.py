import requests
from utils.logger import logger


def send_notification(title: str, body: str, url: str, expo_tokens: list):
    if not expo_tokens:
        return []
    response = []
    c = 100  # Expo has a maximum of 100 notifications per request
    for _expo_tokens in [expo_tokens[x:x + c] for x in range(0, len(expo_tokens), c)]:
        r = requests.post('https://exp.host/--/api/v2/push/send', data={
            'to': _expo_tokens,
            'title': title,
            'body': body,
            'data.url': url
        })
        expo_response = r.json()
        logger.info(expo_response)
        if 'data' in expo_response:
            data = expo_response['data'] if isinstance(expo_response['data'], list) else [expo_response['data']]
            response.extend([{'token': token, 'status': data[i]['status']} for i, token in enumerate(_expo_tokens)])
        elif errors := expo_response.get('errors'):
            for error in errors:
                if error.get('code') == 'PUSH_TOO_MANY_EXPERIENCE_IDS':
                    for project, tokens in error.get('details', {}).items():
                        response.extend(send_notification(title, body, url, tokens))
        else:  # Most common error is PUSH_TOO_MANY_EXPERIENCE_IDS
            result = send_notifications_individually(title, body, url, _expo_tokens)
            response.extend(result)
    return response


def send_notifications_individually(title: str, body: str, url: str, expo_tokens: list):
    if not expo_tokens:
        return []
    response = []
    for _expo_token in expo_tokens:
        r = requests.post('https://exp.host/--/api/v2/push/send', data={
            'to': _expo_token,
            'title': title,
            'body': body,
            'data.url': url
        })
        expo_response = r.json()
        logger.info(expo_response)
        response.append({'token': _expo_token, 'status': expo_response['data']['status']})
    return response
