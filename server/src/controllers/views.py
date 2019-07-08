# -*- encoding: utf-8 -*-

import json

import aiohttp_jinja2
from aiohttp.web_exceptions import HTTPMovedPermanently

from emoji.repositories import emoji_log_repository


# Views : ja
#~~~~~~~~~~~~~~~~~~

async def index_ja(request):
    return await _render(request, 'home.html', locale='ja')

async def contact_ja(request):
    return await _render(request, 'contact.html', locale='ja')


# Views : ko
#~~~~~~~~~~~~~~~~~~

async def redirect_index_ko(request):
    return HTTPMovedPermanently('/ko/', headers={
        'Cache-Control': 'public, immutable, max-age=31536000', # 1 year
    })

async def index_ko(request):
    return await _render(request, 'home.html', locale='ko')

async def contact_ko(request):
    return await _render(request, 'contact.html', locale='ko')


async def _fetch_emoji_logs(emoji_service):
    emoji_logs_records = await emoji_log_repository.filter_recently()
    emoji_logs = [ {
        'text': v['text'],
        'url': emoji_service.make_url(
            v['text'],
            v['font'],
            v['color'],
            v['back_color'],
            v['size_fixed'],
            v['align'],
            v['stretch'],
        ),
    } for v in emoji_logs_records ]

    return emoji_logs


async def _render(request, template, *, locale='ja'):
    request['locale'] = locale
    fonts = json.dumps(request.app['repos']['font'].all())

    emoji_service = request.app['services']['emoji']
    emoji_logs = json.dumps(await _fetch_emoji_logs(emoji_service))

    response = aiohttp_jinja2.render_template(template, request, {
        'fonts': fonts,
        'emoji_logs': emoji_logs,
        'locale': locale,
    })
    if request.app.debug:
        response.headers['Cache-Control'] = 'private, no-store, no-cache, must-revalidate'
    else:
        response.headers['Cache-Control'] = 'public, max-age={}'.format(10) # 10 sec

    return response