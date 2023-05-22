import pytest
from datetime import datetime, timedelta
from copy import deepcopy
from functools import wraps

from config.db import conn
from config.constants import CURRENT_ENVIRONMENT, EnvironmentEnum
from utils.security import encode
from utils.format import paginate_list
from models.admin import RoleEnum


def verify_environment(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if CURRENT_ENVIRONMENT != EnvironmentEnum.test:
            raise Exception('Tests should run on a test environment. Verify the .env file')
        return func(*args, **kwargs)

    return wrapper


@pytest.fixture()
@verify_environment
def mongo_empty():
    conn.admins.delete_many({})
    conn.amenities.delete_many({})
    conn.events.delete_many({})
    conn.faqs.delete_many({})
    conn.leads.delete_many({})
    conn.posts.delete_many({})
    conn.talents.delete_many({})
    conn.users.delete_many({})
    conn.venues.delete_many({})


class DummyAdmins:
    admin = {
        'name': 'johndoe',
        'email': 'johndoe@test.com',
        'role': RoleEnum.superadmin,
        'date_created': datetime.utcnow() - timedelta(minutes=1),
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'deleted': False
    }

    admin_token = encode(admin)

    deleted_admin = {
        'name': 'deleted admin',
        'email': 'deleted@test.com',
        'role': RoleEnum.admin,
        'date_create': datetime.utcnow() - timedelta(minutes=1),
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'deleted': True
    }

    deleted_admin_token = encode(deleted_admin)

    talent = {
        'name': 'talent',
        'email': 'talent@test.com',
        'role': RoleEnum.talent,
        'talent_id': None,
        'date_create': datetime.utcnow() - timedelta(minutes=1),
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'deleted': True
    }

    talent_token = encode(talent)


@pytest.fixture()
@verify_environment
def mongo_insert_dummy_admins():
    conn.admins.insert_many([DummyAdmins.admin, DummyAdmins.talent, DummyAdmins.deleted_admin])


@pytest.fixture()
@verify_environment
def mongo_insert_dummy_amenities():
    amenity1 = {
        'name': 'charly',
        'menu': {},
        'date_created': datetime.utcnow() - timedelta(minutes=1),
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'deleted': False
    }
    amenity2 = {
        'name': 'lo de gus',
        'menu': {},
        'date_create': datetime.utcnow() - timedelta(minutes=1),
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'deleted': True
    }
    conn.amenities.insert_many([amenity1, amenity2])


@pytest.fixture()
@verify_environment
def mongo_insert_dummy_events():
    event1 = {
        'name': 'Fake event 1',
        'type': 'show',
        'description': 'Some description',
        'talents_ids': [],
        'collaborators_ids': [],
        'good_to_know': '',
        'picture': {'alt': '', 'local': None, 'original': '', 'thumbnail': None},
        'stage_id': None,
        'start_date': datetime(2023, 3, 6, 12, 0),
        'end_date': datetime(2023, 3, 6, 15, 30),
        'tags': ['Movement', 'Music'],
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'date_created': datetime.utcnow() - timedelta(minutes=1),
        'deleted': False
    }
    event2 = {
        'name': 'Fake event 2',
        'type': 'show',
        'description': 'Some other description',
        'talents_ids': [],
        'collaborators_ids': [],
        'good_to_know': '',
        'picture': {'alt': '', 'local': None, 'original': '', 'thumbnail': None},
        'stage_id': None,
        'start_date': datetime(2023, 3, 6, 16, 0),
        'end_date': datetime(2023, 3, 6, 17, 30),
        'tags': ['Movement', 'Yoga'],
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'date_created': datetime.utcnow() - timedelta(minutes=1),
        'deleted': True
    }
    conn.events.insert_many([event1, event2])


@pytest.fixture()
@verify_environment
def mongo_insert_dummy_faqs():
    faq1 = {
        'question': 'question 1',
        'answer': 'answer 1',
        'category': 'Ticketing',
        'slug': 'slug-1',
        'cms_id': '123',
        '_archived': False,
        '_draft': False,
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'date_created': datetime.utcnow() - timedelta(minutes=1),
        'deleted': False
    }
    faq2 = {
        'question': 'question 2',
        'answer': 'answer 2',
        'category': 'Ticketing',
        'slug': 'slug-2',
        'cms_id': '456',
        '_archived': False,
        '_draft': False,
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'date_created': datetime.utcnow() - timedelta(minutes=1),
        'deleted': True
    }

    conn.faqs.insert_many([faq1, faq2])


@pytest.fixture()
@verify_environment
def mongo_insert_dummy_leads():
    lead1 = {
        'name': 'lead1',
        'last_name': 'lead 1 last name',
        'tel': '12345678',
        'email': 'lead1@test.com',
        'type': 'academy',
        'deleted': False,
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'date_created': datetime.utcnow() - timedelta(minutes=1)
    }
    lead2 = {
        'name': 'deleted lead',
        'last_name': 'lead 2 last name',
        'tel': '87654321',
        'email': 'lead2@test.com',
        'type': 'academy',
        'deleted': True,
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'date_created': datetime.utcnow() - timedelta(minutes=1)
    }
    conn.leads.insert_many([lead1, lead2])


@pytest.fixture()
@verify_environment
def mongo_insert_dummy_posts():
    post1 = {
        'title': 'Test post',
        'subtitle': 'A subtitle',
        'author': 'Test author',
        'body': 'body',
        'category': 'Guides',
        'picture': {'alt': None, 'local': None, 'original': None, 'thumbnail': None},
        'slug': '',
        'tags': ['Music'],
        'visibility': 'Guest',
        'date_created': datetime.utcnow() - timedelta(minutes=1),
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'deleted': False
    }
    post2 = {
        'title': 'Deleted post',
        'subtitle': 'A subtitle',
        'author': 'Test author',
        'body': 'body',
        'category': 'Guides',
        'picture': {'alt': None, 'local': None, 'original': None, 'thumbnail': None},
        'slug': '',
        'tags': [],
        'visibility': 'Guest',
        'date_created': datetime.utcnow() - timedelta(minutes=1),
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'deleted': True
    }
    conn.posts.insert_many([post1, post2])


class DummyTalents:
    talent1 = {
        '_archived': False,
        '_draft': False,
        'approved_tracks': '',
        'categories': [],
        'contact_name': 'asd',
        'country': 'USA',
        'date_created': datetime.utcnow() - timedelta(minutes=1),
        'deleted': False,
        'email': 'asd@asd.com',
        'envision_festival': True,
        'ethos_id': None,
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'long_bio': 'this is the long bio',
        'main_category': 'Music',
        'main_stage': None,
        'flags': [],
        'media': {
            'instagram': {'description': None, 'embed': None, 'url': None},
            'soundcloud': {'description': None, 'embed': None, 'url': None},
            'spotify': {'description': None, 'embed': None, 'url': None},
            'youtube': {'description': None, 'embed': None, 'url': None},
        },
        'message': 'nan',
        'name': 'test name',
        'name_logo': {'has_logo': False, 'logo': None, 'replace_name': False, 'alt': ''},
        'online_content': False,
        'phone': None,
        'picture': {'local': None, 'original': None, 'thumbnail': None},
        'pillars': ['Music'],
        'published_status': 'review',
        'short_bio': '',
        'slogan': None,
        'slug': 'talent-1',
        'title': ''
    }
    talent2 = deepcopy(talent1)
    talent2['name'] = 'Another talent'
    talent2['slug'] = 'talent-2'
    talent2['ethos_id'] = 123


@pytest.fixture()
@verify_environment
def mongo_insert_dummy_talents():
    talent1 = {
        '_archived': False,
        '_draft': False,
        'approved_tracks': '',
        'categories': [],
        'contact_name': 'asd',
        'country': 'USA',
        'date_created': datetime.utcnow() - timedelta(minutes=1),
        'deleted': False,
        'email': 'asd@asd.com',
        'envision_festival': True,
        'ethos_id': None,
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'long_bio': 'this is the long bio',
        'main_category': 'Music',
        'main_stage': None,
        'flags': [],
        'media': {
            'instagram': {'description': None, 'embed': None, 'url': None},
            'soundcloud': {'description': None, 'embed': None, 'url': None},
            'spotify': {'description': None, 'embed': None, 'url': None},
            'youtube': {'description': None, 'embed': None, 'url': None},
        },
        'message': 'nan',
        'name': 'test name',
        'name_logo': {'has_logo': False, 'logo': None, 'replace_name': False, 'alt': ''},
        'online_content': False,
        'phone': None,
        'picture': {'local': None, 'original': None, 'thumbnail': None},
        'pillars': ['Music'],
        'published_status': 'review',
        'short_bio': '',
        'slogan': None,
        'slug': 'talent-1',
        'title': ''
    }
    talent2 = deepcopy(talent1)
    talent2['name'] = 'Another talent'
    talent2['slug'] = 'talent-2'
    talent2['ethos_id'] = 123
    conn.talents.insert_many([talent1, talent2])


@pytest.fixture()
@verify_environment
def mongo_insert_dummy_users():
    user1 = {
        'badges': [],
        'bio': None,
        'birthdate': None,
        'buddies': [],
        'country': None,
        'date_created': datetime.utcnow() - timedelta(minutes=1),
        'email': 'test@test.com',
        'enrolled_courses': [],
        'envision_app_id': None,
        'ethos_passport_id': None,
        'ethos_subscription': None,
        'expo_token': 'test expo token',
        'favourite_events': [],
        'favourite_talents': [],
        'festival_ticket': None,
        'firebase_id': None,
        'first_name': None,
        'gender': None,
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'last_name': None,
        'login_source': None,
        'national_id': None,
        'password': None,
        'phone': None,
        'profile_picture': None,
        'user_category': None,
        'user_name': None,
        'deleted': False
    }

    user2 = {
        'badges': [],
        'bio': None,
        'birthdate': None,
        'buddies': [],
        'country': None,
        'date_created': datetime.utcnow() - timedelta(minutes=1),
        'email': None,
        'enrolled_courses': [],
        'envision_app_id': None,
        'ethos_passport_id': None,
        'ethos_subscription': None,
        'expo_token': 'test expo token 2',
        'favourite_events': [],
        'favourite_talents': [],
        'festival_ticket': None,
        'firebase_id': None,
        'first_name': None,
        'gender': None,
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'last_name': None,
        'login_source': None,
        'national_id': None,
        'password': None,
        'phone': None,
        'profile_picture': None,
        'user_category': None,
        'user_name': None,
        'deleted': False
    }

    conn.users.insert_many([user1, user2])


@pytest.fixture()
@verify_environment
def mongo_insert_dummy_venues():
    venue1 = {
        'name': 'Luna',
        'description': 'This stage is located in a secluded and intimate area of the '
                       'festival, with a focus on downtempo and meditative music. It '
                       'will feature acts such as ambient and yoga-inspired music, as '
                       'well as other genres that promote self-reflection and '
                       'spiritual connection.',
        'location': 'Located in a secluded and intimate area of the festival',
        'type': 'stage',
        'images': None,
        'open_times': {
            'Monday': 'CLOSED',
            'Tuesday': 'CLOSED',
            'Wednesday': '5:30 PM',
            'Thursday': '5:30 PM',
            'Friday': '5:30 PM',
            'Saturday': '5:30 PM',
            'Sunday': '5:30 PM'
        },
        'deleted': False,
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'date_created': datetime.utcnow() - timedelta(minutes=1)
    }
    venue2 = {
        'name': 'SOL',
        'description': 'This stage is located in a sunny and open area of the '
                       'festival, featuring upbeat and energetic acts that will make '
                       'you want to dance and enjoy the sun. It will host live music '
                       'and DJs, with a focus on electronic and world music.',
        'location': 'Located in a sunny and open area of the festival',
        'type': 'stage',
        'images': None,
        'open_times': {
            'Monday': 'CLOSED',
            'Tuesday': 'CLOSED',
            'Wednesday': 'CLOSED',
            'Thursday': '6:30 PM',
            'Friday': '5:30 PM',
            'Saturday': '6:30 PM',
            'Sunday': '6:00 PM'
        },
        'deleted': True,
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'date_created': datetime.utcnow() - timedelta(minutes=1)
    }
    venue3 = {
        'name': 'Sushi',
        'description': 'some description',
        'location': 'Located in a sunny and open area of the festival',
        'type': 'restaurant',
        'images': None,
        'open_times': {
            'Monday': 'CLOSED',
            'Tuesday': 'CLOSED',
            'Wednesday': 'CLOSED',
            'Thursday': '6:30 PM',
            'Friday': '5:30 PM',
            'Saturday': '6:30 PM',
            'Sunday': '6:00 PM'
        },
        'deleted': False,
        'last_modified': datetime.utcnow() - timedelta(minutes=1),
        'date_created': datetime.utcnow() - timedelta(minutes=1)
    }

    conn.venues.insert_many([venue1, venue2, venue3])


@pytest.fixture()
@verify_environment
def mock_faq_get_categories(mocker):
    categories = [
        'Work Exchange FAQ',
        'Camping FAQ',
        'Getting there',
        'General Festival FAQ',
        'Ticketing'
    ]
    mocker.patch('service.FAQ.get_categories', return_value=paginate_list(categories))


@pytest.fixture()
@verify_environment
def mock_cms(mocker):
    mocker.patch('utils.cms.create_item', return_value={
        'status': 200,
        'response': {'_id': '000'}
    })
    mocker.patch('utils.cms.update_item', return_value={
        'status': 200
    })
    mocker.patch('utils.cms.delete_item', return_value={
        'status': 200
    })


@pytest.fixture()
@verify_environment
def mock_thinkific(mocker):
    mocker.patch('utils.thinkific.create_item', return_value={
        'status': 200,
        'response': {'id': '000'}
    })
    mocker.patch('utils.cms.update_item', return_value={
        'status': 200
    })
    mocker.patch('utils.cms.delete_item', return_value={
        'status': 200
    })


@pytest.fixture()
@verify_environment
def mock_send_mail(mocker):
    mocker.patch('utils.mail.send_mail', return_value=None)
