from fastapi import APIRouter, status, Header, Path
from typing import Optional
from datetime import datetime
import pytz
from threading import Thread

from models.notification import (NotificationModel, CreateNotificationRequest, UpdateNotificationRequest,
                                 NotificationStatusEnum)
from models.admin import RoleEnum
from models.response import ListModel, Paging
from models.envisionBaseModel import PyObjectId
import service.notification
from config.auth import verify_credentials, ENVISION_APP_API_KEY
from utils.logger import log_request_body
from exceptions.resource_exceptions import ResourceNotFound
from exceptions.notification_exceptions import SendAtPast

costa_rica_tz = pytz.timezone('America/Costa_Rica')

prefix = '/notifications'
notification_routes = APIRouter(
    prefix=prefix,
    tags=['Notifications']
)

allowed_roles = [RoleEnum.superadmin, RoleEnum.admin, RoleEnum.staff]


@notification_routes.get('/', response_model=ListModel[NotificationModel], status_code=status.HTTP_200_OK)
async def get_notifications(limit: int = None,
                            offset: int = None,
                            x_api_key: Optional[str] = Header(None),
                            authorization: str = Header(None, alias='Authorization')):
    verify_credentials(api_key=x_api_key, token=authorization, allowed_roles=allowed_roles)
    if x_api_key == ENVISION_APP_API_KEY:
        limit, offset = None, None
    return service.notification.find(limit=limit, offset=offset)


@notification_routes.post('/send_scheduled', response_model=ListModel[NotificationModel],
                          status_code=status.HTTP_200_OK)
async def send_scheduled_notifications(x_api_key: Optional[str] = Header(None),
                                       authorization: str = Header(None, alias='Authorization')):
    verify_credentials(api_key=x_api_key, token=authorization, allowed_roles=allowed_roles)
    notifications = service.notification.send_scheduled()
    return ListModel[NotificationModel](
        results=notifications,
        paging=Paging(total=len(notifications), limit=len(notifications), offset=0)
    )


@notification_routes.get('/{notification_id}', response_model=NotificationModel, status_code=status.HTTP_200_OK)
async def get_notification(notification_id: PyObjectId = Path(title='The ID of the Notification to get'),
                           x_api_key: Optional[str] = Header(None),
                           authorization: str = Header(None, alias='Authorization')):
    verify_credentials(api_key=x_api_key, token=authorization, allowed_roles=allowed_roles)
    notification = service.notification.get(notification_id)
    if notification is None:
        raise ResourceNotFound(notification_id, 'Notification')
    return notification


@notification_routes.post('/', response_model=NotificationModel, status_code=status.HTTP_201_CREATED)
async def create_notification(notification: CreateNotificationRequest,
                              x_api_key: Optional[str] = Header(None),
                              authorization: str = Header(None, alias='Authorization')):
    log_request_body(f'POST {prefix}', notification)
    verify_credentials(api_key=x_api_key, token=authorization, allowed_roles=allowed_roles)
    send_at_utc = None
    if notification.send_at:
        send_at_utc = costa_rica_tz.localize(notification.send_at.replace(tzinfo=None)).astimezone(pytz.utc)
        if send_at_utc < datetime.utcnow().replace(tzinfo=pytz.utc):
            raise SendAtPast()

    t = Thread(target=service.notification.create, args=(notification.title, notification.body, notification.url,
                                                         notification.test, notification.users_filter, send_at_utc))
    t.start()
    return NotificationModel(
        title=notification.title,
        body=notification.body,
        url=notification.url,
        send_at=notification.send_at,
        status=NotificationStatusEnum.sent if notification.send_at is None else NotificationStatusEnum.canceled,
        notifications_sent=0,
        notifications_error=0,
        date_created=datetime.utcnow(),
        test=notification.test
    )


@notification_routes.put('/{notification_id}', response_model=NotificationModel)
async def update_notification(notification_id: PyObjectId,
                              notification: UpdateNotificationRequest,
                              x_api_key: Optional[str] = Header(None),
                              authorization: str = Header(None, alias='Authorization')):
    log_request_body(f'PUT /notifications/{notification_id}', notification)
    verify_credentials(api_key=x_api_key, token=authorization, allowed_roles=allowed_roles)
    if notification.send_at:
        send_at_utc = costa_rica_tz.localize(notification.send_at.replace(tzinfo=None)).astimezone(pytz.utc)
        if send_at_utc < datetime.utcnow().replace(tzinfo=pytz.utc):
            raise SendAtPast()

    updated_notification = service.notification.update(notification_id, notification.dict(exclude_unset=True))
    if not updated_notification:
        raise ResourceNotFound(notification_id, 'Notification')

    return updated_notification


@notification_routes.post('/{notification_id}/cancel_scheduled', response_model=NotificationModel,
                          status_code=status.HTTP_200_OK)
async def cancel_scheduled_notification(notification_id: PyObjectId = Path(title='The ID of the Notification to cancel'),
                                        x_api_key: Optional[str] = Header(None),
                                        authorization: str = Header(None, alias='Authorization')):
    verify_credentials(api_key=x_api_key, token=authorization, allowed_roles=allowed_roles)
    notification = service.notification.cancel(notification_id)
    if notification is None:
        raise ResourceNotFound(notification_id, 'Notification')
    return notification
