from typing import Optional, Union
from bson import ObjectId
from datetime import datetime
import pytz

from exceptions.events_exceptions import (EventsOverlap, EventDatesInverted, MissingDate,
                                          EventTooShortDuration, EventTooLongDuration)

from utils.format import create_response_paginated, paginate_list, regex_query

from models.event import EventModel
from models.response import ListModel
from models.filters import EventFilters
from service.base import Base

EVENT_MINIMUM_DURATION = 15  # in minutes
EVENT_MAXIMUM_DURATION = 23  # in hours

lookup_stages = [
    {
        '$lookup': {
            'from': 'talents',
            'localField': 'talents_ids',
            'foreignField': '_id',
            'as': 'talents',
            'pipeline': [{'$project': {'name': 1, 'short_bio': 1}}]
        }
    }, {
        '$lookup': {
            'from': 'talents',
            'localField': 'collaborators_ids',
            'foreignField': '_id',
            'as': 'collaborators',
            'pipeline': [{'$project': {'name': 1, 'short_bio': 1}}]
        }
    }, {
        '$lookup': {
            'from': 'venues',
            'localField': 'stage_id',
            'foreignField': '_id',
            'as': 'stage',
            'pipeline': [{'$project': {'name': 1}}]
        }
    }, {
        '$addFields': {
            'stage': {'$first': '$stage'}
        }
    }
]


def _event_entity(event: dict) -> dict:
    if not event:
        return event
    for field in ['talent', 'collaborator']:
        if f'{field}s' in event:
            for talent in event[f'{field}s']:
                talent['id'] = str(talent.pop('_id'))
        else:
            event[f'{field}s'] = [{'id': talent_id} for talent_id in event[f'{field}s_ids']]
        # del event[f'{field}s_ids']

    if 'stage' in event:
        event['stage']['id'] = event['stage'].pop('_id')
    else:
        event['stage'] = {'id': event['stage_id']}
    del event['stage_id']

    return event


def _dates_verifications(start_date: datetime, end_date: datetime) -> None:
    start_date = start_date.astimezone(pytz.utc) if start_date.tzinfo else start_date.replace(tzinfo=pytz.utc)
    end_date = end_date.astimezone(pytz.utc) if end_date.tzinfo else end_date.replace(tzinfo=pytz.utc)
    if start_date >= end_date:
        raise EventDatesInverted()
    duration_in_minutes = (end_date - start_date).total_seconds() / 60
    duration_in_hours = duration_in_minutes / 60
    if duration_in_minutes < EVENT_MINIMUM_DURATION:
        raise EventTooShortDuration(EVENT_MINIMUM_DURATION)
    if duration_in_hours > EVENT_MAXIMUM_DURATION:
        raise EventTooLongDuration(EVENT_MAXIMUM_DURATION)


class Event(Base):
    def __init__(self):
        super().__init__(resource='events', q_fields=['name', 'stage_name', 'talent_name'])

    def _create_pipeline(self, filters: EventFilters, last_modified: datetime = None, sort_by: str = None,
                         ascending: bool = True, offset: int = None, limit: int = None) -> list:
        match_stage = {}
        end_date_filter = {}
        if filters.ids:
            match_stage['_id'] = {'$in': filters.ids}
        if filters.end_date_from:
            end_date_filter['$gte'] = filters.end_date_from
        if filters.end_date_to:
            end_date_filter['$lte'] = filters.end_date_to
        if end_date_filter:
            match_stage['end_date'] = end_date_filter
        if last_modified:
            match_stage['last_modified'] = {'$gte': last_modified}
        else:
            match_stage['deleted'] = False

        fields = [('stage_id', filters.stage_id),
                  ('talents_ids', filters.talent_id),
                  ('collaborators_ids', filters.talent_id)]

        for field_name, field_filter in fields:
            if field_filter:
                if '$or' not in match_stage:
                    match_stage['$or'] = []
                field_filter = [ObjectId(f) if ObjectId.is_valid(f) else f for f in field_filter]
                match_stage['$or'].append({field_name: {'$in': field_filter}})

        if filters.type:
            match_stage['type'] = filters.type
        if filters.tags:
            match_stage['tags'] = {'$in': filters.tags}

        pipeline = [{'$match': match_stage}]
        pipeline.extend(lookup_stages)
        if filters.q:
            match_stage_2 = {'$or': [regex_query(field, filters.q) for field in self.q_fields]}
            pipeline.append({'$match': match_stage_2})

        if sort_by:
            pipeline.append({'$sort': {sort_by: 1 if ascending else -1}})
        if offset:
            pipeline.append({'$skip': offset})
        if limit:
            pipeline.append({'$limit': limit})

        return pipeline

    def _find_overlap(self, start_date: datetime, end_date: datetime, stage_id: ObjectId,
                      exclude_event: ObjectId = None) -> list:
        if not stage_id:
            return []
        return [e['name'] for e in self.collection.find(
            {
                'start_date': {'$lt': end_date},
                'end_date': {'$gt': start_date},
                'stage_id': stage_id,
                'deleted': False,
                '_id': {'$ne': exclude_event}
            },
            {'name': 1}
        )]

    def find(self, *, filters: EventFilters, last_modified: datetime = None, sort_by: str = None,
             ascending: bool = True, limit: int = None, offset: int = None) -> ListModel[EventModel]:
        pipeline = self._create_pipeline(filters=filters, last_modified=last_modified, sort_by=sort_by,
                                         ascending=ascending, limit=limit, offset=offset)

        response = create_response_paginated(self.collection,
                                             pipeline=pipeline,
                                             limit=limit, offset=offset,
                                             sort_by=sort_by, ascending=ascending,
                                             format_func=_event_entity)
        return response

    def get(self, event_id: ObjectId) -> Optional[dict]:
        pipeline = [{
            '$match': {
                '_id': event_id,
                'deleted': False
            }
        }]
        pipeline.extend(lookup_stages)
        response = list(self.collection.aggregate(pipeline))

        return _event_entity(response[0]) if len(response) > 0 else None

    def create(self, event: dict) -> dict:
        if type(event['start_date']) != type(event['end_date']):
            raise MissingDate()

        for f in ['start_date', 'end_date']:
            event[f] = event[f].replace(second=0, microsecond=0) if event[f] else None

        if event['start_date'] and event['end_date']:
            _dates_verifications(event['start_date'], event['end_date'])

        events_overlap = self._find_overlap(event['start_date'], event['end_date'], event['stage_id'])
        if events_overlap:
            raise EventsOverlap(events_overlap)

        mongo_event = super().create(event)
        return _event_entity(mongo_event)

    def update(self, event_id: ObjectId, event: dict) -> Optional[dict]:
        event_db = self.get(event_id)

        if not event_db or not event:
            return event_db

        to_update = event.copy()
        for f in ['start_date', 'end_date']:
            if date := to_update.get(f):
                to_update[f] = date.replace(second=0, microsecond=0)

        fields = ['start_date', 'end_date', 'stage_id']
        if any(f in to_update for f in fields):
            start_date = to_update.get('start_date', event_db.get('start_date'))
            end_date = to_update.get('end_date', event_db.get('end_date'))
            stage_id = to_update.get('stage_id', event_db.get('stage_id'))

            if type(start_date) != type(end_date):
                raise MissingDate()

            if start_date and end_date:
                _dates_verifications(start_date, end_date)

            events_overlap = self._find_overlap(start_date, end_date, stage_id, event_id)
            if events_overlap:
                raise EventsOverlap(events_overlap)

        super().update(event_id, to_update)
        return self.get(event_id)

    def exists(self, event_id: Union[str, ObjectId] = None,
               talent_id: Union[str, ObjectId] = None,
               stage_id: Union[str, ObjectId] = None) -> bool:
        q = {'deleted': False}

        for v in [event_id, talent_id, stage_id]:
            if v is not None and not ObjectId.is_valid(v):
                return False

        if event_id:
            q['_id'] = ObjectId(event_id)
        if talent_id:
            q['$or'] = [{'talents_ids': ObjectId(talent_id)}, {'collaborators_ids': ObjectId(talent_id)}]
        if stage_id:
            q['stage_id'] = ObjectId(stage_id)

        return self.collection.count_documents(q) > 0

    def get_tags(self, limit: int = None, offset: int = None) -> ListModel:
        tags = [tag for tag in self.collection.distinct('tags', filter={'deleted': False}) if tag]
        return paginate_list(tags, limit=limit, offset=offset)
