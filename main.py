import asyncio
import cv2
from aiohttp import web
import uuid
import threading


class Server:
    _COMPRESSION_QUALITY: int = 80

    def __init__(self):
        self._app = web.Application()
        self._app.router.add_get("/", self._index)
        self._app.router.add_get("/stream", self._stream)

        self.frame: cv2.Mat | None = None
        self.cached_chunk: bytes | None = None
        self.has_cache: bool = False
        self._app["sessions_chunk_sent_flag"] = {}

    async def _index(self, request: web.Request):
        return web.Response(
            content_type="text/html",
            text="""
                <!DOCTYPE html>
                <html>
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>osion</title>
                    </head>
                    <body>
                        <img src="stream"/>
                    </body>
                </html>
                """,
        )

    async def _stream(self, request: web.Request):
        session_id = str(uuid.uuid4())
        self._app["sessions_chunk_sent_flag"][session_id] = False

        response = web.StreamResponse(
            status=200,
            reason="OK",
            headers={"Content-Type": "multipart/x-mixed-replace; boundary=--FRAME"},
        )
        await response.prepare(request)

        while True:
            if not self._app["sessions_chunk_sent_flag"][session_id]:
                if not self.has_cache:
                    _, jpeg = cv2.imencode(
                        ".jpeg",
                        self.frame,
                        [cv2.IMWRITE_JPEG_QUALITY, self._COMPRESSION_QUALITY],
                    )
                    jpeg_bytes = jpeg.tobytes()

                    self.cached_chunk = (
                        b"--FRAME\r\n"
                        b"Content-Type: image/jpeg\r\n"
                        b"Content-Length: %d\r\n\r\n"
                        b"%s\r\n"
                        % (
                            len(jpeg_bytes),
                            jpeg_bytes,
                        )
                    )
                    self.has_cache = True

                await response.write(self.cached_chunk)

                self._app["sessions_chunk_sent_flag"][session_id] = True

            await asyncio.sleep(1 / 60)

        return response

    def start(self, port: int):
        web.run_app(
            self._app,
            host="0.0.0.0",
            port=port,
            handler_cancellation=True,
            reuse_address=True,
            reuse_port=True,
        )

    def set_frame(self, frame: cv2.Mat):
        self.frame = frame
        self.has_cache = False

        for key in self._app["sessions_chunk_sent_flag"]:
            self._app["sessions_chunk_sent_flag"][key] = False


_PORT: int = 8080

if __name__ == "__main__":

    def video_capture_thread():
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
            server.set_frame(frame)

    threading.Thread(target=video_capture_thread).start()

    server = Server()
    server.start(_PORT)
