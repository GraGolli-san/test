#!/usr/bin/python3.7

import aiohttp
from aiohttp import web, WSCloseCode
import asyncio

import ssl

from dummy_image_publisher import DummyImagePublisher

class AIOHTTPServer():

    def __init__(self):
        self.loop = asyncio.new_event_loop()

        self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.ssl_context.load_cert_chain('server.crt', 'server.key')

        self.camera = DummyImagePublisher()

        self.stream_event = asyncio.Event()
        self.stream_event.clear()


    def html_response(self, fname):
        s = open(fname, "r", encoding="utf-8")
        return web.Response(text=s.read(), content_type='text/html')

    async def index_handler(self, request):
        return self.html_response('index.html')

    async def http_handler(self, request):
        return web.Response(text='Hello, world')

    async def gen(self):
        while True:
            frame = self.camera.get_png_frame().tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')
            await asyncio.sleep(0.01)
            # await self.stream_event.wait()
            while not self.stream_event.is_set():
                await asyncio.sleep(0.01)

    async def stream_test_handler(self, request):
        # return web.Response(self.gen(), content_type='multipart/x-mixed-replace; boundary=frame')
        return web.Response(body=self.gen(), content_type='multipart/x-mixed-replace; boundary=frame')

    def gen2(self):
        return self.camera.get_png_frame().tobytes()

    async def stream_test_handler2(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    img = self.gen2()
                    await ws.send_bytes(img)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' % ws.exception())

        return ws



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

    async def stream_control_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                elif msg.data == 'start':
                    print('start stream ...')
                    self.loop.call_soon_threadsafe(self.stream_event.set)
                elif msg.data == 'stop':
                    print('stop stream ...')
                    self.loop.call_soon_threadsafe(self.stream_event.clear)
                else:
                    await ws.send_str('no control')
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' % ws.exception())

        return ws


    async def make_app(self):
        app = web.Application()
        app.add_routes([
            web.get('/',   self.http_handler),
            web.get('/index.html',   self.index_handler),
            web.get('/ws', self.websocket_handler),
            web.get('/stream_test', self.stream_test_handler),
            web.get('/ws/stream_test2', self.stream_test_handler2),
            web.get('/ws/stream_test', self.stream_control_handler),
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
        self.loop.run_until_complete(self.start())
        self.loop.run_forever()
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
