import re
import logging
import random, string
from aiohttp import web
from app import db
from http.client import RemoteDisconnected
from tenacity import retry, retry_if_exception_type, stop_after_attempt


log = logging.getLogger(__name__)
URL_REGEX = r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+"
alphanumeric_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits

class ApiView(web.View):
    async def get(self):
        return await self.handler(self.request.query)
    
    async def post(self):
        try:
            return await self.handler(await self.request.json())
        except:
            return web.Response(status=400, text="400: Bad Request, Invalid JSON provided.")
    
    @retry(retry=retry_if_exception_type(RemoteDisconnected), stop=stop_after_attempt(3))
    async def handler(self, data):
        log.debug(data)
    
        if not data.get('url'):
            return web.Response(status=400, text="400: Bad Request, Request doesn't have any key named 'url'.")
    
        url = data['url']
        if not re.match(URL_REGEX, url):
            return web.Response(status=400, text="400: Bad Request, Invalid URL provided.")
    
        key = str(data['key']) if data.get('key') else await generate_key(data)
        if not key.isalnum():
            return web.Response(status=400, text="400: Bad Request, Key should only contain alphanumeric characters.")
    
        if db.get(key):
            return web.Response(status=400, text="400: Bad Request, Key already exists enter new one.")
    
        db.put({'url':url}, key)
        return web.Response(status=200, text=key)



async def generate_key(dict):
    return "".join(random.choices(alphanumeric_chars, k=8))