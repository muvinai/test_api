from datetime import datetime

from fastapi import APIRouter, status, Header, Query
from typing import Optional

from models.event import EventModel, CreateEventRequest, UpdateEventRequest
from models.venue import VenueTypeEnum
from models.admin import RoleEnum
from models.response import ListModel
from models.filters import Filter, EventFilters
from models.envisionBaseModel import PyObjectId
import service.admin
import service.event
import service.talent
import service.venue
from utils.logger import log_request_body
from config.auth import verify_credentials, ENVISION_APP_API_KEY
from exceptions.resource_exceptions import ResourceNotFound

prefix = '/events'
event_routes = APIRouter(
    prefix=prefix,
    tags=['Events']
)

allowed_roles = [RoleEnum.superadmin, RoleEnum.admin, RoleEnum.staff, RoleEnum.talent]


@event_routes.get('/', response_model=ListModel[EventModel], status_code=status.HTTP_200_OK)
async def get_events(filters: EventFilters = Filter(EventFilters, alias='filter'),
                     last_modified: datetime = Query(default=None,
                                                     description='Filter all the events modified after this time'),
                     sort_by: str = 'start_date',
                     ascending: bool = True,
                     limit: int = None,
                     offset: int = None,
                     x_api_key: Optional[str] = Header(None),
                     authorization: str = Header(None, alias='Authorization')):
    admin = verify_credentials(api_key=x_api_key,
                               token=authorization,
                               allowed_roles=[RoleEnum.superadmin, RoleEnum.admin, RoleEnum.staff, RoleEnum.talent])
    if admin and admin.get('role') == RoleEnum.talent:
        admin = service.Admin().get(admin.get('_id'))
        filters.talent_id = [admin['talent_id']]
    if x_api_key == ENVISION_APP_API_KEY:
        limit, offset = None, None
    return service.Event().find(filters=filters, last_modified=last_modified,
                                sort_by=sort_by, ascending=ascending, limit=limit, offset=offset)


@event_routes.get('/tags', response_model=ListModel[str], status_code=status.HTTP_200_OK)
async def get_event_tags(limit: int = None,
                         offset: int = None,
                         x_api_key: Optional[str] = Header(None),
                         authorization: str = Header(None, alias='Authorization')):
    verify_credentials(api_key=x_api_key,
                       token=authorization,
                       allowed_roles=[RoleEnum.superadmin, RoleEnum.admin, RoleEnum.staff, RoleEnum.talent])
    return service.Event().get_tags(limit=limit, offset=offset)


@event_routes.get('/{event_id}', response_model=EventModel, status_code=status.HTTP_200_OK)
async def get_event(event_id: PyObjectId,
                    x_api_key: Optional[str] = Header(None),
                    authorization: str = Header(None, alias='Authorization')):
    verify_credentials(api_key=x_api_key,
                       token=authorization,
                       allowed_roles=[RoleEnum.superadmin, RoleEnum.admin, RoleEnum.staff, RoleEnum.talent])
    event = service.Event().get(event_id)
    if event is None:
        raise ResourceNotFound(event_id, 'Event')
    return event


@event_routes.post('/', response_model=EventModel, status_code=status.HTTP_201_CREATED)
async def create_event(event: CreateEventRequest,
                       authorization: str = Header(alias='Authorization')):
    log_request_body(f'POST {prefix}', event)
    verify_credentials(token=authorization,
                       allowed_roles=[RoleEnum.superadmin, RoleEnum.admin, RoleEnum.staff])

    for talent_id in event.talents_ids + event.collaborators_ids:
        if not service.Talent().exists(talent_id):
            raise ResourceNotFound(talent_id, 'Talent')
    if event.stage_id and not service.Venue().exists(event.stage_id, venue_types=[VenueTypeEnum.stage,
                                                                                  VenueTypeEnum.theme_camp]):
        raise ResourceNotFound(event.stage_id, 'Stage')

    return service.Event().create(event.dict())


@event_routes.put('/{event_id}', response_model=EventModel)
async def update_event(event_id: PyObjectId,
                       event: UpdateEventRequest,
                       authorization: str = Header(alias='Authorization')):
    log_request_body(f'PUT {prefix}/{event_id}', event)
    verify_credentials(token=authorization,
                       allowed_roles=[RoleEnum.superadmin, RoleEnum.admin, RoleEnum.staff, RoleEnum.talent])

    talents_ids = event.talents_ids if event.talents_ids else []
    talents_ids = [t for t in talents_ids if t]
    collaborators_ids = event.collaborators_ids if event.collaborators_ids else []
    collaborators_ids = [t for t in collaborators_ids if t]
    for talent_id in talents_ids + collaborators_ids:
        if not service.Talent().exists(talent_id):
            raise ResourceNotFound(talent_id, 'Talent')
    if event.stage_id and not service.Venue().exists(event.stage_id, venue_types=[VenueTypeEnum.stage,
                                                                                  VenueTypeEnum.theme_camp]):
        raise ResourceNotFound(event.stage_id, 'Stage')

    updated_event = service.Event().update(event_id, event.dict(exclude_unset=True))
    if not updated_event:
        raise ResourceNotFound(event_id, 'Event')

    return updated_event


@event_routes.delete('/{event_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: PyObjectId,
                       authorization: str = Header(alias='Authorization')):
    verify_credentials(token=authorization,
                       allowed_roles=[RoleEnum.superadmin, RoleEnum.admin, RoleEnum.staff])
    r = service.Event().delete(event_id)
    if not r:
        raise ResourceNotFound(event_id, 'Event')
