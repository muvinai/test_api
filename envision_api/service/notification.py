from typing import Optional
from datetime import datetime
from bson import ObjectId
from pymongo import ReturnDocument

from exceptions.notification_exceptions import CancelNotificationException, UpdateNotificationException

from config.db import conn
from utils.notifications import send_notification
from utils.format import create_response_paginated

from models.notification import NotificationStatusEnum, UsersFilterModel, NotificationModel
from models.response import ListModel

import service.user


def find(limit: int = None, offset: int = None) -> ListModel[NotificationModel]:
    return create_response_paginated(conn.notifications, query={}, limit=limit, offset=offset)


def get(notification_id: ObjectId) -> Optional[dict]:
    return conn.notifications.find_one({'_id': notification_id})


def create(title: str, body: str, url: str, test: bool = False, users_filter: UsersFilterModel = None,
           send_at: datetime = None) -> dict:
    q = {}
    if users_filter:
        if expo_token := users_filter.expo_token:
            q['expo_token'] = expo_token
        if favourite_talents := users_filter.favourite_talents:
            q['favourite_talents'] = favourite_talents
        if favourite_events := users_filter.favourite_events:
            q['favourite_events'] = favourite_events
    if test:
        q['test'] = True

    tokens = [user['expo_token'] for user in conn.users.find(q, {'expo_token': 1})]
    if not send_at:
        notifications_results = send_notification(title, body, url, tokens)
        notifications_sent = [n['token'] for n in notifications_results if n['status'] == 'ok']
        notifications_error = [n['token'] for n in notifications_results if n['status'] == 'error']
        status = NotificationStatusEnum.sent
    else:
        notifications_sent = []
        notifications_error = []
        status = NotificationStatusEnum.scheduled

    notification = {
        'title': title,
        'body': body,
        'url': url,
        'filter': users_filter.dict(),
        'send_at': send_at,
        'status': status,
        'test': test,
        'notifications_sent': len(notifications_sent),
        'notifications_error': len(notifications_error),
        'date_created': datetime.utcnow()
    }
    r = conn.notifications.insert_one(notification)
    notification['_id'] = r.inserted_id

    service.User().new_notifications(notifications_sent, r.inserted_id, error=False)
    service.User().new_notifications(notifications_error, r.inserted_id, error=True)

    return notification


def send_scheduled() -> list:
    notifications = []
    query = {
        'status': NotificationStatusEnum.scheduled,
        'send_at': {'$lte': datetime.utcnow()}
    }
    for notification in conn.notifications.find(query):
        q = {}
        if notification.get('filter'):
            if favourite_talents := notification.get('filter').get('favourite_talents'):
                q['favourite_talents'] = favourite_talents
            if favourite_events := notification.get('filter').get('favourite_events'):
                q['favourite_events'] = favourite_events
        if notification.get('test', False):
            q['test'] = True

        tokens = [user['expo_token'] for user in conn.users.find(q, {'expo_token': 1})]
        title, body, url = notification['title'], notification['body'], notification.get('url')
        notifications_results = send_notification(title, body, url, tokens)
        notifications_sent = [n['token'] for n in notifications_results if n['status'] == 'ok']
        notifications_error = [n['token'] for n in notifications_results if n['status'] == 'error']
        conn.notifications.update_one(
            {'_id': notification['_id']},
            {
                '$set': {
                    'status': NotificationStatusEnum.sent,
                    'notifications_sent': len(notifications_sent),
                    'notifications_error': len(notifications_error),
                }
            }
        )
        service.User().new_notifications(notifications_sent, notification['_id'], error=False)
        service.User().new_notifications(notifications_error, notification['_id'], error=True)
        notifications.append(notification['_id'])

    return list(conn.notifications.find({'_id': {'$in': notifications}}))


def update(notification_id: ObjectId, notification: dict) -> Optional[dict]:
    notification_db = conn.notifications.find_one({'_id': notification_id}, {'status': 1})
    if not notification_db:
        return
    if notification_db['status'] != NotificationStatusEnum.scheduled:
        raise UpdateNotificationException()

    to_update = notification.copy()
    to_update["last_modified"] = datetime.utcnow()

    updated_notification = conn.notifications.find_one_and_update(
        {"_id": notification_id},
        {"$set": to_update},
        return_document=ReturnDocument.AFTER
    )
    return updated_notification


def cancel(notification_id: ObjectId) -> Optional[dict]:
    notification = conn.notifications.find_one(notification_id)
    if not notification:
        return

    if notification['status'] != NotificationStatusEnum.scheduled:
        raise CancelNotificationException(notification['status'])

    to_update = {
        'status': NotificationStatusEnum.canceled,
        'last_modified': datetime.utcnow()
    }
    updated_notification = conn.notifications.find_one_and_update(
        {"_id": notification_id},
        {"$set": to_update},
        return_document=ReturnDocument.AFTER
    )

    return updated_notification
