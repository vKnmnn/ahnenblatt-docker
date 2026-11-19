#!/usr/bin/env python3
"""Check the settings delivered to browser clients by a running Selkies server."""
import asyncio
import json
import sys

import aiohttp


async def check(expected):
    async with asyncio.timeout(30):
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(
                'https://localhost:3001/api/websockets',
                ssl=False, origin='https://localhost:3001',
            ) as socket:
                async for message in socket:
                    if message.type != aiohttp.WSMsgType.TEXT:
                        continue
                    try:
                        payload = json.loads(message.data)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(payload, dict) or payload.get('type') != 'server_settings':
                        continue
                    settings = payload['settings']
                    for name in ('ui_sidebar_show_stats', 'ui_sidebar_show_video_settings',
                                 'ui_sidebar_show_screen_settings', 'ui_sidebar_show_sharing',
                                 'enable_sharing'):
                        if settings[name]['value'] is not expected:
                            raise SystemExit(f'Selkies {name}: expected {expected}, got {settings[name]}')
                    if not expected and not settings['enable_sharing']['locked']:
                        raise SystemExit('Sharing must be locked off by default')
                    print(f'Selkies browser settings verified: optional features={expected}')
                    return
    raise SystemExit('Selkies did not send browser settings')


if __name__ == '__main__':
    asyncio.run(check(sys.argv[1] == 'true'))
