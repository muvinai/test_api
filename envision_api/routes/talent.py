from datetime import datetime

from fastapi import APIRouter, status, Header, Query
from typing import Optional

from models.talent import TalentModel, CreateTalentRequest, UpdateTalentRequest
from models.venue import VenueTypeEnum
from models.admin import RoleEnum
from models.response import ListModel
from models.envisionBaseModel import PyObjectId
from models.filters import TalentFilters
from models.filters import Filter
import service.admin
import service.event
import service.talent
import service.venue
from utils.logger import log_request_body
from config.auth import verify_credentials, ENVISION_APP_API_KEY
from exceptions.resource_exceptions import ResourceNotFound, ResourceReference
from exceptions.auth_exceptions import AdminNotAllowed

prefix = '/talents'
talent_routes = APIRouter(
    prefix=prefix,
    tags=['Talents']
)

allowed_roles = [RoleEnum.superadmin, RoleEnum.admin, RoleEnum.staff, RoleEnum.talent]


@talent_routes.get('/', response_model=ListModel[TalentModel], status_code=status.HTTP_200_OK)
async def get_talents(filters: TalentFilters = Filter(TalentFilters, alias='filter'),
                      last_modified: datetime = Query(default=None,
                                                      description='Filter all the talents modified after this time'),
                      sort_by: Optional[str] = 'name',
                      ascending: Optional[bool] = True,
                      limit: int = None,
                      offset: int = None,
                      x_api_key: Optional[str] = Header(None),
                      authorization: str = Header(None, alias='Authorization')):
    admin = verify_credentials(api_key=x_api_key, token=authorization, allowed_roles=allowed_roles)
    if admin and admin.get('role') == RoleEnum.talent:
        admin = service.Admin().get(admin.get('_id'))
        filters.ids = [admin['talent_id']]
    if x_api_key == ENVISION_APP_API_KEY:
        limit, offset = None, None
        if filters.envision_festival is None:
            filters.envision_festival = True
    return service.Talent().find(filters=filters, last_modified=last_modified, sort_by=sort_by, ascending=ascending,
                                 limit=limit, offset=offset)


@talent_routes.get('/categories', response_model=ListModel[str], status_code=status.HTTP_200_OK)
async def get_talent_categories(limit: int = None,
                                offset: int = None,
                                x_api_key: Optional[str] = Header(None),
                                authorization: str = Header(None, alias='Authorization')):
    verify_credentials(api_key=x_api_key, token=authorization, allowed_roles=allowed_roles)
    return service.Talent().get_categories(limit=limit, offset=offset)


@talent_routes.get('/pillars', response_model=ListModel[str], status_code=status.HTTP_200_OK)
async def get_talent_pillars(limit: int = None,
                             offset: int = None,
                             x_api_key: Optional[str] = Header(None),
                             authorization: str = Header(None, alias='Authorization')):
    verify_credentials(api_key=x_api_key, token=authorization, allowed_roles=allowed_roles)
    return service.Talent().get_pillars(limit=limit, offset=offset)


@talent_routes.get('/{talent_id}', response_model=TalentModel, status_code=status.HTTP_200_OK)
async def get_talent(talent_id: PyObjectId,
                     x_api_key: Optional[str] = Header(None),
                     authorization: str = Header(None, alias='Authorization')):
    admin = verify_credentials(api_key=x_api_key, token=authorization, allowed_roles=allowed_roles)
    if admin and admin.get('role') == RoleEnum.talent:
        admin = service.Admin().get(admin.get('_id'))
        if str(admin['talent_id']) != talent_id:
            raise AdminNotAllowed()

    talent = service.Talent().get(talent_id)
    if talent is None:
        raise ResourceNotFound(talent_id, 'Talent')
    return talent


@talent_routes.get('/{talent_id}/generate_bio', status_code=status.HTTP_200_OK)
async def generate_talent_bio(talent_id: PyObjectId,
                              x_api_key: Optional[str] = Header(None),
                              authorization: str = Header(None, alias='Authorization')):
    admin = verify_credentials(api_key=x_api_key, token=authorization, allowed_roles=allowed_roles)
    if admin and admin.get('role') == RoleEnum.talent:
        admin = service.Admin().get(admin.get('_id'))
        if str(admin['talent_id']) != talent_id:
            raise AdminNotAllowed()

    bio = service.Talent().generate_bio(talent_id)
    if bio is None:
        raise ResourceNotFound(talent_id, 'Talent')
    return {'result': bio}


@talent_routes.post('/', response_model=TalentModel, status_code=status.HTTP_201_CREATED)
async def create_talent(talent: CreateTalentRequest,
                        authorization: str = Header(alias='Authorization')):
    log_request_body(f'POST {prefix}', talent)
    verify_credentials(token=authorization, allowed_roles=[RoleEnum.superadmin, RoleEnum.admin, RoleEnum.staff])

    if talent.main_stage and not service.Venue().exists(talent.main_stage,
                                                        venue_types=[VenueTypeEnum.stage, VenueTypeEnum.theme_camp]):
        raise ResourceNotFound(talent.main_stage, 'Stage')

    return service.Talent().create(talent.dict())


@talent_routes.put('/{talent_id}', response_model=TalentModel)
async def update_talent(talent_id: PyObjectId,
                        talent: UpdateTalentRequest,
                        authorization: str = Header(alias='Authorization')):
    log_request_body(f'PUT {prefix}/{talent_id}', talent)
    verify_credentials(token=authorization, allowed_roles=[RoleEnum.superadmin, RoleEnum.admin, RoleEnum.staff])

    if talent.main_stage and not service.Venue().exists(talent.main_stage, venue_types=[VenueTypeEnum.stage,
                                                                                        VenueTypeEnum.theme_camp]):
        raise ResourceNotFound(talent.main_stage, 'Stage')

    updated_talent = service.Talent().update(talent_id, talent.dict(exclude_unset=True))
    if not updated_talent:
        raise ResourceNotFound(talent_id, 'Talent')

    return updated_talent



@talent_routes.delete('/{talent_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_talent(talent_id: PyObjectId,
                        authorization: str = Header(None, alias='Authorization')):
    verify_credentials(token=authorization, allowed_roles=[RoleEnum.superadmin, RoleEnum.admin, RoleEnum.staff])
    if service.Event().exists(talent_id=talent_id):
        raise ResourceReference(resource_to_delete='Talent', resource_reference='Event')
    r = service.Talent().delete(talent_id)
    if not r:
        raise ResourceNotFound(talent_id, 'Talent')
