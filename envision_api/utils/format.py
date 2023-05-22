from typing import List
from copy import deepcopy
from pymongo.collection import Collection

from models.response import ListModel, Paging


class PaginationQueryParams:
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = limit


def regex_query(field: str, q: str) -> dict:
    return {field: {'$regex': q, '$options': 'i'}}


def format_dict(old_dict, to_delete: list = None, to_rename: dict = None, to_extend: dict = None):
    new_dict = deepcopy(old_dict)
    if to_delete:
        for d in to_delete:
            if d in new_dict:
                del new_dict[d]

    if to_rename:
        for old, new in to_rename.items():
            if old in new_dict:
                new_dict[new] = new_dict.pop(old)

    if to_extend:
        for k, v in to_extend.items():
            new_dict[k] = v

    return new_dict


def create_response_paginated(collection: Collection, *,
                              query: dict = None, pipeline: List[dict] = None,
                              limit: int = None, offset: int = None,
                              sort_by: str = None, ascending: bool = True,
                              format_func: callable = None) -> ListModel:
    if query is not None and pipeline is not None:
        raise TypeError('create_response_paginated() takes only one argument')
    if query is None and pipeline is None:
        raise TypeError('one of the following arguments should not be None: query, pipeline')

    pipeline = pipeline if pipeline else [{'$match': query}]

    r = list(collection.aggregate(pipeline + [{'$count': 'count'}]))
    total = r[0]['count'] if r else 0

    if sort_by:
        sort_by = '_id' if sort_by == 'id' else sort_by
        pipeline = add_sort_stages_to_pipeline(pipeline, sort_by=sort_by, ascending=ascending)

    if offset is not None:
        pipeline.append({'$skip': offset})
    else:
        offset = 0
    if limit is not None:
        pipeline.append({'$limit': limit})
    else:
        limit = total

    cursor = collection.aggregate(pipeline)

    results = list(map(format_func, cursor)) if format_func else list(cursor)

    return create_list_response(results, total=total, limit=limit, offset=offset)


def paginate_list(results: list, limit: int = None, offset: int = None):
    results.sort()
    total = len(results)
    if not total:
        total = len(results)
    if not limit:
        limit = total
    if not offset:
        offset = 0

    return create_list_response(results[offset:offset + limit], total=total, limit=limit, offset=offset)


def create_list_response(results: list, total: int = None, limit: int = None, offset: int = None) -> ListModel:
    if not total:
        total = len(results)
    if not limit:
        limit = total
    if not offset:
        offset = 0

    return ListModel(
        results=results,
        paging=Paging(total=total, limit=limit, offset=offset)
    )


def add_sort_stages_to_pipeline(pipeline: list, sort_by: str, ascending: bool) -> list:
    pipeline.extend([
        {
            '$fill': {
                'output': {
                    sort_by: {'value': None}
                }
            }
        }, {
            '$addFields': {
                'has_field': {
                    '$ne': [f'${sort_by}', None]
                }
            }
        }, {
            '$sort': {
                'has_field': -1,
                sort_by: 1 if ascending else -1
            }
        }, {
            '$unset': 'has_field'
        }
    ])

    return pipeline
