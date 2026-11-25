"""Key sender for the Vestel/Toshiba SmartCenter virtual remote."""
from __future__ import annotations

import asyncio
from collections.abc import Callable, Sequence
import logging
import re

import aiohttp

from .const import DIAL_APP_PATH, DMR_CONTROL_PATH, KEY_REPEAT_DELAY

_LOGGER = logging.getLogger(__name__)


class TvConnectionError(Exception):
    """The TV could not be reached."""


async def async_send_key(host: str, port: int, code: int) -> None:
    """Send one remote key code to the TV.

    Raises TvConnectionError if the TV cannot be reached.
    """
    url = f"http://{host}:{port}{DIAL_APP_PATH}"
    # The TV rejects a quoted code, so it is sent without quotes
    payload = f"<remote><key code={code} /></remote>"
    try:
        # Close the connection after each key so the TV's server does not hang
        connector = aiohttp.TCPConnector(force_close=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(
                url,
                data=payload,
                headers={
                    "Content-Type": "application/xml",
                    "Connection": "close",
                },
                timeout=aiohttp.ClientTimeout(total=3),
            ) as resp:
                _LOGGER.debug("Key %s sent, TV answered %s", code, resp.status)
    except (aiohttp.ClientError, TimeoutError, OSError) as err:
        raise TvConnectionError(f"Could not send key {code} to {host}: {err}") from err


async def async_send_keys(host: str, port: int, codes: Sequence[int]) -> None:
    """Send key codes one after another with a short pause in between."""
    for index, code in enumerate(codes):
        if index:
            await asyncio.sleep(KEY_REPEAT_DELAY)
        await async_send_key(host, port, code)


async def async_send_key_repeated(
    host: str, port: int, code: int, count: int
) -> None:
    """Send the same key code several times with a short pause in between."""
    await async_send_keys(host, port, [code] * count)


async def async_launch_app(
    host: str, port: int, app: str, origin: str | None = None
) -> bool:
    """Start an app on the TV via DIAL. Return True if the TV accepted it."""
    url = f"http://{host}:{port}/apps/{app}"
    headers = {"Content-Type": "text/plain", "Connection": "close"}
    if origin:
        headers["Origin"] = origin
    try:
        connector = aiohttp.TCPConnector(force_close=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(
                url,
                data="",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                _LOGGER.debug("DIAL start %s: TV answered %s", app, resp.status)
                return resp.status in (200, 201)
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("DIAL start %s failed: %s", app, err)
        return False


_STATE_RE = re.compile(r"<state>\s*([^<\s]+)\s*</state>")


async def async_get_app_state(
    host: str, port: int, app: str, origin: str | None = None
) -> str | None:
    """Return the DIAL state of an app ("running", "stopped", ...) or None."""
    url = f"http://{host}:{port}/apps/{app}"
    headers = {"Connection": "close"}
    if origin:
        headers["Origin"] = origin
    try:
        connector = aiohttp.TCPConnector(force_close=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=3),
            ) as resp:
                if resp.status != 200:
                    return None
                match = _STATE_RE.search(await resp.text())
                return match.group(1) if match else None
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("DIAL state of %s not readable: %s", app, err)
        return None


async def async_stop_app(
    host: str, port: int, app: str, origin: str | None = None
) -> bool:
    """Close a running app via DIAL. Return True if the TV accepted it."""
    url = f"http://{host}:{port}/apps/{app}/run"
    headers = {"Connection": "close"}
    if origin:
        headers["Origin"] = origin
    try:
        connector = aiohttp.TCPConnector(force_close=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.delete(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                _LOGGER.debug("DIAL stop %s: TV answered %s", app, resp.status)
                return 200 <= resp.status < 300
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("DIAL stop %s failed: %s", app, err)
        return False


_RC_SERVICE = "urn:schemas-upnp-org:service:RenderingControl:1"
_CURRENT_RE = re.compile(r"<Current\w+>\s*([^<\s]*)\s*</")


async def async_dmr_get(host: str, port: int, action: str) -> str | None:
    """Read a value from the TV's DLNA renderer (GetVolume / GetMute)."""
    body = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
        's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>'
        f'<u:{action} xmlns:u="{_RC_SERVICE}">'
        "<InstanceID>0</InstanceID><Channel>Master</Channel>"
        f"</u:{action}></s:Body></s:Envelope>"
    )
    try:
        connector = aiohttp.TCPConnector(force_close=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(
                f"http://{host}:{port}{DMR_CONTROL_PATH}",
                data=body,
                headers={
                    "Content-Type": 'text/xml; charset="utf-8"',
                    "SOAPACTION": f'"{_RC_SERVICE}#{action}"',
                    "Connection": "close",
                },
                timeout=aiohttp.ClientTimeout(total=3),
            ) as resp:
                if resp.status != 200:
                    return None
                match = _CURRENT_RE.search(await resp.text())
                return match.group(1) if match else None
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("DLNA %s not readable: %s", action, err)
        return None


async def async_get_volume(host: str, port: int) -> int | None:
    """Current TV volume (0-100) or None."""
    value = await async_dmr_get(host, port, "GetVolume")
    return int(value) if value is not None and value.isdigit() else None


async def async_get_mute(host: str, port: int) -> bool | None:
    """Current TV mute state or None."""
    value = await async_dmr_get(host, port, "GetMute")
    if value is None:
        return None
    return value.lower() in ("1", "true")


_TV_STATUS_RE = re.compile(r"tv_status:(\d+)")
_TV_STATE_RE = re.compile(r"<tv_state\s+value=['\"]([^'\"]*)['\"]")


class TvEventListener:
    """Keeps a websocket to the TV open and reports its events.

    on_event is called with ("status", "1"), ("status", "0") or
    ("state", "<value>").
    """

    def __init__(
        self,
        host: str,
        port: int,
        on_event: Callable[[str, str], None],
        reconnect_delay: float,
    ) -> None:
        self._url = f"http://{host}:{port}/"
        self._on_event = on_event
        self._reconnect_delay = reconnect_delay
        self._ws: aiohttp.ClientWebSocketResponse | None = None

    async def run(self) -> None:
        """Listen until cancelled, reconnecting when the connection drops."""
        while True:
            try:
                timeout = aiohttp.ClientTimeout(total=None, sock_connect=5)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.ws_connect(self._url, autoping=True) as ws:
                        self._ws = ws
                        _LOGGER.debug("TV websocket connected: %s", self._url)
                        async for msg in ws:
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                self._handle(msg.data)
                            elif msg.type in (
                                aiohttp.WSMsgType.CLOSED,
                                aiohttp.WSMsgType.ERROR,
                            ):
                                break
            except asyncio.CancelledError:
                raise
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug("TV websocket not available: %s", err)
            finally:
                self._ws = None
            await asyncio.sleep(self._reconnect_delay)

    @property
    def connected(self) -> bool:
        """True while the websocket to the TV is open."""
        return self._ws is not None and not self._ws.closed

    async def async_reconnect(self) -> None:
        """Drop the current connection (e.g. after the TV rebooted)."""
        if self._ws is not None and not self._ws.closed:
            await self._ws.close()

    def _handle(self, text: str) -> None:
        _LOGGER.debug("TV websocket event: %s", text)
        if match := _TV_STATUS_RE.search(text):
            self._on_event("status", match.group(1))
        if match := _TV_STATE_RE.search(text):
            self._on_event("state", match.group(1))
