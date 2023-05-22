from typing import Optional
from bson import ObjectId
from datetime import datetime

from exceptions.resource_exceptions import DuplicatedKey
from exceptions.thinkific_exceptions import ThinkificCreateError, ThinkificUpdateError, ThinkificDeleteError

from utils import thinkific
from utils.logger import logger
from utils.image import create_image_obj
from utils.format import format_dict, create_response_paginated, paginate_list, regex_query
from utils.ai import generate_talent_bio

from models.talent import TalentModel
from models.response import ListModel
from models.filters import TalentFilters
from service.base import Base

# CMS_TALENTS_COLLECTION_ID = '637e2f87ca19c0a56162d15f'
THINKIFIC_COLLECTION = 'instructors'


def _format_thinkific_dict(talent_dict: dict) -> dict:
    to_keep = {'name', 'short_bio', 'email', 'slug', 'title'}
    to_delete = list(set(talent_dict.keys()) - to_keep)
    to_rename = {'name': 'first_name', 'short_bio': 'bio'}
    to_extend = {'user_id': None}

    if talent_dict.get('picture.original'):
        to_extend['avatar_url'] = talent_dict.get('picture.original')

    if 'slug' in talent_dict:
        to_extend['last_name'] = talent_dict['slug']

    return format_dict(talent_dict, to_delete=to_delete, to_rename=to_rename, to_extend=to_extend)


class Talent(Base):
    def __init__(self):
        super().__init__(resource='talents', q_fields=['title', 'subtitle', 'body', 'author'])

    def find(self, filters: TalentFilters, last_modified: datetime = None, sort_by: str = None,
             ascending: bool = True, limit: int = None, offset: int = None) -> ListModel[TalentModel]:
        mongo_query = {}
        if filters.ids:
            mongo_query['_id'] = {'$in': filters.ids}
        if filters.q:
            fields = ['name', 'description']
            mongo_query['$or'] = [regex_query(field, filters.q) for field in fields]
        if filters.slug:
            mongo_query['slug'] = filters.slug
        if filters.email:
            mongo_query['email'] = filters.email
        if filters.envision_festival is not None:
            mongo_query['envision_festival'] = filters.envision_festival
        if last_modified:
            mongo_query['last_modified'] = {'$gte': last_modified}
        else:
            mongo_query['deleted'] = False

        return create_response_paginated(self.collection, query=mongo_query, limit=limit, offset=offset,
                                         sort_by=sort_by, ascending=ascending)

    def generate_bio(self, talent_id: ObjectId) -> Optional[dict]:
        talent = self.get(talent_id)
        if not talent:
            return
        return generate_talent_bio(talent)

    def get_categories(self, limit: int = None, offset: int = None) -> ListModel:
        categories = [c for c in self.collection.distinct('main_category', filter={'deleted': False}) if c]
        return paginate_list(categories, limit=limit, offset=offset)

    def get_pillars(self, limit: int = None, offset: int = None) -> ListModel:
        pillars = [c for c in self.collection.distinct('pillars', filter={'deleted': False}) if c]
        return paginate_list(pillars, limit=limit, offset=offset)

    def create(self, talent: dict) -> dict:
        super()._format_slug(talent)
        talent['picture'] = create_image_obj(talent['picture'], self.resource)

        # create_cms_item = talent['envision_festival']
        # if create_cms_item:
        #     cms_dict = _format_cms_dict(talent)
        #     cms_response = cms.create_item(CMS_TALENTS_COLLECTION_ID, cms_dict)
        #     if cms_response['status'] >= 400:
        #         raise CMSError(cms_response['error'])
        #     talent['cms_id'] = cms_response['response']['_id']

        ethos_id = None
        if talent['ethos_instructor']:
            thinkific_response = thinkific.create_item(THINKIFIC_COLLECTION, _format_thinkific_dict(talent))
            if thinkific_response['status'] >= 400:
                # if create_cms_item:
                #     cms.delete_item(CMS_TALENTS_COLLECTION_ID, talent['cms_id'])
                raise ThinkificCreateError(THINKIFIC_COLLECTION, thinkific_response['error'])
            ethos_id = thinkific_response['response']['id']
            talent['ethos_id'] = ethos_id

        del talent['ethos_instructor']

        try:
            return super().create(talent)
        except DuplicatedKey as e:
            # cms.delete_item(CMS_TALENTS_COLLECTION_ID, talent['cms_id'])
            if ethos_id:
                thinkific.delete_item(THINKIFIC_COLLECTION, ethos_id)
            raise e

    def update(self, talent_id: ObjectId, talent: dict) -> Optional[dict]:
        talent_db = self.collection.find_one({'_id': talent_id, 'deleted': False})
        to_update = talent.copy()
        if not talent_db or not to_update:
            return talent_db

        if talent_db.get('ethos_id'):
            thinkific_item = _format_thinkific_dict(to_update)
            logger.info(f'Thinkific: Update item {thinkific_item}')
            r = thinkific.update_item(THINKIFIC_COLLECTION, talent_db['ethos_id'], thinkific_item)
            if r['status'] >= 400:
                logger.error('ERROR when updating thinkific talent')
                raise ThinkificUpdateError(THINKIFIC_COLLECTION, r['error'])

        self._update_mongo(talent_id, to_update)
    

    def create_ethos_instructor(self, talent_id: ObjectId) -> Optional[dict]:
        talent_db: dict = self.collection.find_one(talent_id)
        if not talent_db:
            return
        if talent_db.get('ethos_id'):
            return talent_db

        thinkific_response = thinkific.create_item(THINKIFIC_COLLECTION, _format_thinkific_dict(talent_db))
        if thinkific_response['status'] >= 400:
            raise ThinkificCreateError(THINKIFIC_COLLECTION, thinkific_response['error'])
        ethos_id = thinkific_response['response']['id']
        to_update = {'ethos_id': ethos_id}
        return self._update_mongo(talent_id, to_update)

    def delete(self, talent_id: ObjectId) -> bool:
        talent = self.collection.find_one({'_id': talent_id, 'deleted': False}, {'ethos_id': 1})
        if not talent:
            return False

        if talent.get('ethos_id'):
            ethos_id = talent['ethos_id']
            r = thinkific.delete_item(THINKIFIC_COLLECTION, ethos_id)
            if r['status'] >= 400:
                raise ThinkificDeleteError(THINKIFIC_COLLECTION, r['error'])
        r = self.collection.update_one(
            {'_id': talent_id, 'deleted': False},
            {'$set': {'deleted': True, 'slug': str(talent_id), 'last_modified': datetime.utcnow()}}
        )
        return r.modified_count > 0

    # def _format_cms_dict(talent_dict: dict) -> dict:
    #     to_rename = {
    #         'cms_status': 'status',
    #         'picture': 'profile',
    #         'short_bio': 'short-bio',
    #         'published_status': 'status',
    #         'main_stage': 'stage',
    #         'main_category': 'main-category-2'
    #     }
    #     to_delete = list(
    #         set(talent_dict.keys()) - set(to_rename.keys()) - {'name', 'slug', 'message', '_draft', '_archived'}
    #     )
    #     to_extend = {}
    #     if original_picture := talent_dict.get('picture', {}).get('original'):
    #         to_extend['artist-logo'] = original_picture
    #     if 'media' in talent_dict:
    #         media = talent_dict['media']
    #         if instagram_url := media.get('instagram', {}).get('url'):
    #             to_extend['instagram'] = instagram_url
    #         for m in ['youtube', 'soundcloud', 'spotify']:
    #             if m in media:
    #                 if 'url' in media[m]:
    #                     to_extend[m] = media[m]['url']
    #                 if 'embed' in media[m]:
    #                     to_extend[f'{m}-embed'] = media[m]['embed']
    #                 if 'description' in media[m]:
    #                     to_extend[f'{m}-description'] = media[m]['description']
    #
    #     for p in ['music', 'art', 'movement', 'spirituality', 'health', 'education', 'sustainability']:
    #         pillars = talent_dict.get('pillars', [])
    #         main_category = talent_dict.get('main_category')
    #         to_extend[p] = p in [p.lower() for p in pillars] or main_category == p
    #
    #     return format_dict(talent_dict, to_delete=to_delete, to_rename=to_rename, to_extend=to_extend)
