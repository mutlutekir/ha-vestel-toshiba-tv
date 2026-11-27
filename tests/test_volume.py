"""Protocol tests using a local HTTP/WebSocket TV; no Home Assistant needed."""

import asyncio
import importlib.util
import sys
import unittest
from contextlib import suppress
from pathlib import Path
from unittest.mock import AsyncMock, patch

from aiohttp import web

# Load the dependency-free API without executing the integration's HA setup.
component = Path(__file__).resolve().parents[1] / "custom_components/vestel_toshiba_tv"
spec = importlib.util.spec_from_file_location(
    "vestel_api_under_test",
    component / "api.py",
    submodule_search_locations=[str(component)],
)
api = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = api
spec.loader.exec_module(api)


class VolumeFallbackTests(unittest.IsolatedAsyncioTestCase):
    async def test_valid_dlna_volume_including_zero_keeps_existing_path(self):
        for value in ("0", "7", "100"):
            fallback = AsyncMock(return_value=42)
            with patch.object(api, "async_dmr_get", AsyncMock(return_value=value)):
                self.assertEqual(
                    await api.async_get_volume("tv", 2870, smartcenter=fallback),
                    int(value),
                )
            fallback.assert_not_awaited()

    async def test_missing_or_invalid_dlna_volume_uses_fallback(self):
        for value in (None, "", "invalid", "-1", "101", "7.0"):
            fallback = AsyncMock(return_value=7)
            with patch.object(api, "async_dmr_get", AsyncMock(return_value=value)):
                self.assertEqual(
                    await api.async_get_volume("tv", 2870, smartcenter=fallback), 7
                )
            fallback.assert_awaited_once_with()

    async def test_unavailable_on_both_paths_stays_unknown(self):
        with patch.object(api, "async_dmr_get", AsyncMock(return_value=None)):
            self.assertIsNone(
                await api.async_get_volume(
                    "tv", 2870, smartcenter=AsyncMock(return_value=None)
                )
            )
            self.assertIsNone(await api.async_get_volume("tv", 2870))


class SmartCenterTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.events = []
        self.requests = []
        self.replies = ["<volume level='7'/>"]
        self.status = 200
        self.disconnect = False
        self.server_ws = None
        self.active_queries = 0
        self.max_active_queries = 0
        self.no_reply_requested = asyncio.Event()

        async def websocket(request):
            self.server_ws = web.WebSocketResponse()
            await self.server_ws.prepare(request)
            async for message in self.server_ws:
                pass
            return self.server_ws

        async def query(request):
            self.requests.append((await request.text(), dict(request.headers)))
            self.active_queries += 1
            self.max_active_queries = max(self.max_active_queries, self.active_queries)
            try:
                if self.disconnect:
                    await self.server_ws.close()
                elif self.status == 200:
                    for reply in self.replies:
                        await self.server_ws.send_str(reply)
                # Force the websocket reply to arrive before the HTTP response.
                await asyncio.sleep(0.01)
                self.no_reply_requested.set()
                return web.Response(status=self.status)
            finally:
                self.active_queries -= 1

        app = web.Application()
        app.router.add_get("/", websocket)
        app.router.add_post("/apps/SmartCenter", query)
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, "127.0.0.1", 0)
        await self.site.start()
        self.port = self.site._server.sockets[0].getsockname()[1]
        self.listener = api.TvEventListener(
            "127.0.0.1", self.port, lambda *args: self.events.append(args), 0.01
        )
        self.task = asyncio.create_task(self.listener.run())
        async with asyncio.timeout(2):
            while not self.listener.connected:
                await asyncio.sleep(0.001)

    async def asyncTearDown(self):
        self.task.cancel()
        with suppress(asyncio.CancelledError):
            await self.task
        await self.runner.cleanup()

    async def test_reads_reply_before_http_response_on_existing_socket(self):
        socket = self.listener._ws
        self.assertEqual(await self.listener.async_get_volume(self.port), 7)
        self.assertIs(self.listener._ws, socket)
        self.assertEqual(self.events, [("volume", "7")])
        body, headers = self.requests[0]
        self.assertEqual(body, "<command>volume</command>")
        self.assertEqual(headers["application_name"], "toshiba smart center")
        self.assertEqual(headers["Content-Type"], "text/plain; charset=ISO-8859-1")
        self.assertEqual(headers["Connection"], "close")
        self.assertIsNone(self.listener._volume_answer)

    async def test_zero_is_a_real_volume(self):
        self.replies = ['<volume level="0"/>']
        self.assertEqual(await self.listener.async_get_volume(self.port), 0)

    async def test_fresh_query_does_not_return_cached_volume(self):
        self.assertEqual(await self.listener.async_get_volume(self.port), 7)
        self.replies = ["<volume level='19'/>"]
        self.assertEqual(await self.listener.async_get_volume(self.port), 19)
        self.assertEqual(len(self.requests), 2)

    async def test_ignores_other_events_and_invalid_volume_messages(self):
        self.replies = [
            "tv_status:1",
            "<tv_state value='TV'/>",
            "<volume",
            "<volume/>",
            "<volume level='-1'/>",
            "<volume level='101'/>",
            "<volume level='bad'/>",
            "<volumetric level='88'/>",
            "<volume level='100'></volume>",
        ]
        self.assertEqual(await self.listener.async_get_volume(self.port), 100)
        self.assertEqual(
            self.events, [("status", "1"), ("state", "TV"), ("volume", "100")]
        )

    async def test_http_200_without_volume_is_not_a_measurement(self):
        self.replies = []
        with patch.object(api, "VOLUME_QUERY_TIMEOUT", 0.1):
            self.assertIsNone(await self.listener.async_get_volume(self.port))
        self.assertIsNone(self.listener._volume_answer)

    async def test_timeout_reconnects_before_accepting_another_reply(self):
        old_socket = self.server_ws
        old_client_socket = self.listener._ws
        self.replies = []
        with patch.object(api, "VOLUME_QUERY_TIMEOUT", 0.1):
            self.assertIsNone(await self.listener.async_get_volume(self.port))
        self.assertTrue(old_client_socket.closed)
        async with asyncio.timeout(2):
            while not self.listener.connected or self.server_ws is old_socket:
                await asyncio.sleep(0.001)
        self.assertTrue(old_socket.closed)
        self.assertIsNot(self.server_ws, old_socket)
        self.replies = ["<volume level='9'/>"]
        self.assertEqual(await self.listener.async_get_volume(self.port), 9)

    async def test_http_failure_leaves_no_waiter(self):
        self.status = 500
        self.assertIsNone(await self.listener.async_get_volume(self.port))
        self.assertIsNone(self.listener._volume_answer)

    async def test_disconnected_listener_does_not_send_a_query(self):
        disconnected = api.TvEventListener(
            "127.0.0.1", self.port, lambda *args: None, 1
        )
        self.assertIsNone(await disconnected.async_get_volume(self.port))
        self.assertEqual(self.requests, [])

    async def test_disconnect_releases_pending_query(self):
        self.disconnect = True
        async with asyncio.timeout(1):
            self.assertIsNone(await self.listener.async_get_volume(self.port))
        self.assertIsNone(self.listener._volume_answer)

    async def test_concurrent_queries_are_serialized(self):
        self.assertEqual(
            await asyncio.gather(
                self.listener.async_get_volume(self.port),
                self.listener.async_get_volume(self.port),
            ),
            [7, 7],
        )
        self.assertEqual(self.max_active_queries, 1)
        self.assertEqual(len(self.requests), 2)

    async def test_cancellation_cleans_up_and_propagates(self):
        self.replies = []
        task = asyncio.create_task(self.listener.async_get_volume(self.port))
        await self.no_reply_requested.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertIsNone(self.listener._volume_answer)
        async with asyncio.timeout(2):
            while not self.listener.connected:
                await asyncio.sleep(0.001)
        self.replies = ["<volume level='8'/>"]
        self.assertEqual(await self.listener.async_get_volume(self.port), 8)

    async def test_unsolicited_volume_still_updates_event_consumer(self):
        self.listener._handle("<volume level='23'/>")
        self.assertEqual(self.events, [("volume", "23")])
        self.assertIsNone(self.listener._volume_answer)


if __name__ == "__main__":
    unittest.main()
