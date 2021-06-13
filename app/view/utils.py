import logging
import aiohttp_jinja2
from app import db, url_prefix
from aiohttp import web
from http.client import RemoteDisconnected
from tenacity import retry, retry_if_exception_type, stop_after_attempt

log = logging.getLogger(__name__)

@retry(retry=retry_if_exception_type(RemoteDisconnected), stop=stop_after_attempt(3))
@aiohttp_jinja2.template('main.html')
async def GetView(request):
    key = request.match_info['key']
    data = db.get(key)
    if data:
        return {
            "info":data,
            "url_prefix":url_prefix
        }
    else:
        return {'error':'404: Shortened URL not found.'}

@aiohttp_jinja2.template('main.html')
async def WildView(request):
    return {'error':'404: Page not found.'}