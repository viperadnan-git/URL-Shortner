import logging
import aiohttp_jinja2
from aiohttp import web
from app import db, url_prefix
from http.client import RemoteDisconnected
from tenacity import retry, retry_if_exception_type, stop_after_attempt


log = logging.getLogger(__name__)

@aiohttp_jinja2.template('main.html')
async def MainView(request):
    return {'url_prefix':url_prefix}

@retry(retry=retry_if_exception_type(RemoteDisconnected), stop=stop_after_attempt(3))
async def RedirectView(request):
    try:
        return web.HTTPFound(db.get(request.match_info['key'])['url'])
    except TypeError:
        return aiohttp_jinja2.render_template('main.html', request, {"error":"404: Shortened URL not found."})