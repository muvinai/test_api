from datetime import datetime
import mailchimp_transactional
from mailchimp_transactional.api_client import ApiClientError
import urllib.parse
import posixpath

from config.constants import MAILCHIMP_KEY, FRONTEND_URL, BACKEND_URL
from utils.security import encode
from exceptions.mail_exceptions import InvalidMail, RejectedMail, ErrorMail

mailchimp = mailchimp_transactional.Client(MAILCHIMP_KEY)


def send_mail_login(receiver_mail, spice):
    print('sending email')
    url = posixpath.join(BACKEND_URL, f'authenticate?email={urllib.parse.quote(receiver_mail)}&spice={spice}')
    token_url = encode({'url': url})
    params = {
        'the_url': f'{FRONTEND_URL}/#/login?token_url={token_url}'
    }
    template = 'auth-backoffice'
    return send_mail(receiver_mail, template, params)


def send_mail(receiver_mail: str, template: str, params: dict, send_at: datetime = None):
    global_merge_vars = [{'name': k, 'content': v} for k, v in params.items()]

    msg = {
        'from_email': 'no-responder@muvinai.com',
        'from_name': 'Envision Backoffice',
        'to': [{'email': receiver_mail}],
        'global_merge_vars': global_merge_vars
    }

    body = {'template_name': template, 'template_content': [], 'message': msg}
    if send_at:
        body['send_at'] = send_at.strftime('%Y-%m-%d %H:%M:%S')

    try:
        response = mailchimp.messages.send_template(body)
    except ApiClientError as error:
        raise ErrorMail(detail=error.text)

    if response[0]['status'] == 'invalid':
        raise InvalidMail()
    elif response[0]['status'] == 'rejected':
        raise RejectedMail(reason=response[0]['reject_reason'])

    return response[0]
