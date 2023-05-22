import asyncio
import logging

logger = logging.getLogger('main-logger')


def log_request_body(request_id, body):
    asyncio.ensure_future(_log_request_body(request_id, body))


async def _log_request_body(request_id, body):
    logger.info(f'Request: {request_id} - Body: {body}')


def log_error(msg):
    asyncio.ensure_future(_log_error(msg))


async def _log_error(msg):
    logger.error(msg)
