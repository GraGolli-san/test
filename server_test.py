#!/usr/bin/python3.7

import aiohttp
from aiohttp import web, WSCloseCode
import asyncio

import ssl


class AIOHTTPServer():

    def __init__(self):
        self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.ssl_context.load_cert_chain('server.crt', 'server.key')


    def html_response(self, fname):
        s = open(fname, "r")
        return web.Response(text=s.read(), content_type='text/html')

    async def index_handler(self, request):
        return self.html_response('index.html')

    async def http_handler(self, request):
        return web.Response(text='Hello, world')

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    await ws.send_str('some websocket message payload')
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' % ws.exception())

        return ws


    async def make_app(self):
        app = web.Application()
        app.add_routes([
            web.get('/',   self.http_handler),
            web.get('/index.html',   self.index_handler),
            web.get('/ws', self.websocket_handler),
        ])
        return app

    async def start(self) -> None:
        app = await self.make_app()
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, host='0.0.0.0', port=8000, ssl_context=self.ssl_context)
        try:
            await self.site.start()
        except OSError:
            pass
        finally:
            print('done')

    def run(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.start())
        loop.run_forever()
        self.runner.cleanup()



if __name__ == "__main__":
    # app = AIOHTTPServer().make_app()
    # # server = web.TCPSite(runner, 'localhost', 8080)
    # try:
    #     web.run_app(app)
    # except KeyboardInterrupt:
    #     pass
    # finally:
    #     print('done')

    server = AIOHTTPServer()
    try:
        server.run()
    except KeyboardInterrupt:
        pass
    finally:
        print('done')
