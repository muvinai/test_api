import uvicorn
from fastapi import FastAPI, Response, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pydantic

from docs import tags_metadata
from logging.config import dictConfig
from config.log_conf import log_config
from config.constants import CURRENT_ENVIRONMENT

from utils.logger import logger

from routes.admin import admin_routes
from routes.amenity import amenities_routes
from routes.event import event_routes
from routes.faq import faq_routes
from routes.hero import hero_routes
from routes.home import home_routes
from routes.lead import lead_routes
from routes.login import login_routes
from routes.notifications import notification_routes
from routes.post import post_routes
from routes.ranking import ranking_routes
from routes.talent import talent_routes
from routes.user import user_routes
from routes.venue import venue_routes

dictConfig(log_config)
app = FastAPI(
    title=f'Backend for Ethos (running on {CURRENT_ENVIRONMENT.name.upper()})',
    description='REST API using FastAPI and MongoDB',
    version='0.0.1',
    openapi_tags=tags_metadata,
    swagger_ui_parameters={'defaultModelsExpandDepth': -1}
)


@app.exception_handler(pydantic.error_wrappers.ValidationError)
async def pydantic_validation_error(request: Request, exc: pydantic.error_wrappers.ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={'detail': exc.errors()}
    )


# TODO: This should not be left like this in production
origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(admin_routes)
app.include_router(amenities_routes)
app.include_router(event_routes)
app.include_router(faq_routes)
app.include_router(hero_routes)
app.include_router(home_routes)
app.include_router(lead_routes)
app.include_router(login_routes)
app.include_router(notification_routes)
app.include_router(post_routes)
app.include_router(ranking_routes)
app.include_router(talent_routes)
app.include_router(user_routes)
app.include_router(venue_routes)
logger.debug('Running server on {}'.format(CURRENT_ENVIRONMENT.name.upper()))


@app.get('/', include_in_schema=False)
def ping():
    return Response(status_code=200)


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
