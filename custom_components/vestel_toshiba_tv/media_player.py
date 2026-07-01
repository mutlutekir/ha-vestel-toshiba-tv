"""Media player entity for Vestel & Toshiba TV Remote Control."""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET

import aiohttp

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    DEFAULT_PORT,
    DIAL_APP_PATH,
    KEY_CODES,
    SOURCE_LIST,
    SOURCE_CODES,
)

_LOGGER = logging.getLogger(__name__)

SUPPORTED_FEATURES = (
    MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.STOP
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the TV media player from a config entry."""
    data = entry.data
    entity = VestelToshibaTV(
        host=data["host"],
        port=data.get("port", DEFAULT_PORT),
        name=data.get("name", "Vestel & Toshiba TV"),
        unique_id=entry.entry_id,
    )
    async_add_entities([entity], update_before_add=True)


class VestelToshibaTV(MediaPlayerEntity):
    """Representation of a Vestel/Toshiba TV via DIAL protocol."""

    _attr_has_entity_name = False
    _attr_supported_features = SUPPORTED_FEATURES
    _attr_source_list = SOURCE_LIST
    _attr_icon = "mdi:television-play"

    def __init__(self, host: str, port: int, name: str, unique_id: str) -> None:
        self._host = host
        self._port = port
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_state = MediaPlayerState.OFF
        self._attr_source = None
        self._attr_is_volume_muted = False
        self._base_url = f"http://{host}:{port}"
        self._dial_url = f"{self._base_url}{DIAL_APP_PATH}"
        self._available = False

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> MediaPlayerState:
        return self._attr_state

    # ── Polling ────────────────────────────────────────────────────────

    async def async_update(self) -> None:
        """Fetch TV state from DIAL endpoint."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self._dial_url,
                    timeout=aiohttp.ClientTimeout(total=3),
                ) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        self._available = True
                        state = self._parse_dial_state(text)
                        self._attr_state = (
                            MediaPlayerState.ON
                            if state == "running"
                            else MediaPlayerState.STANDBY
                        )
                    else:
                        self._available = True
                        self._attr_state = MediaPlayerState.STANDBY
        except aiohttp.ClientConnectorError:
            self._available = False
            self._attr_state = MediaPlayerState.OFF
        except Exception as err:
            _LOGGER.debug("Update error: %s", err)
            self._available = False

    def _parse_dial_state(self, xml_text: str) -> str:
        try:
            root = ET.fromstring(xml_text)
            ns = {"dial": "urn:dial-multiscreen-org:schemas:dial"}
            state_el = root.find("dial:state", ns)
            if state_el is not None:
                return state_el.text or "unknown"
        except ET.ParseError:
            pass
        return "unknown"

    # ── Key sender ─────────────────────────────────────────────────────

    async def _send_key(self, code: int) -> None:
        url = f"{self._base_url}/apps/SmartCenter"
        # DİKKAT: TV tırnak işaretlerini sevmediği için code değişkeni tırnaksız gönderiliyor
        payload = f"<remote><key code={code} /></remote>"
        try:
            # TV'nin sunucusu kilitlenmesin diye bağlantıyı zorla kapatıyoruz (force_close)
            connector = aiohttp.TCPConnector(force_close=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    url,
                    data=payload,
                    headers={
                        "Content-Type": "application/xml",
                        "Connection": "close"
                    },
                    timeout=aiohttp.ClientTimeout(total=3),
                ) as resp:
                    _LOGGER.debug("Tus %s gonderildi, TV yaniti: %s", code, resp.status)
        except Exception as err:
            _LOGGER.error("Tus gonderilirken hata olustu %s: %s", code, err)

    # ── Standard actions ───────────────────────────────────────────────

    async def async_turn_on(self) -> None:
        await self._send_key(KEY_CODES["power"])

    async def async_turn_off(self) -> None:
        await self._send_key(KEY_CODES["power"])

    async def async_volume_up(self) -> None:
        await self._send_key(KEY_CODES["volume_up"])

    async def async_volume_down(self) -> None:
        await self._send_key(KEY_CODES["volume_down"])

    async def async_mute_volume(self, mute: bool) -> None:
        await self._send_key(KEY_CODES["mute"])
        self._attr_is_volume_muted = not self._attr_is_volume_muted

    async def async_media_next_track(self) -> None:
        await self._send_key(KEY_CODES["channel_up"])

    async def async_media_previous_track(self) -> None:
        await self._send_key(KEY_CODES["channel_down"])

    async def async_media_play(self) -> None:
        await self._send_key(KEY_CODES["play"])

    async def async_media_stop(self) -> None:
        await self._send_key(KEY_CODES["stop"])

    async def async_select_source(self, source: str) -> None:
        code = SOURCE_CODES.get(source, KEY_CODES["source"])
        await self._send_key(code)
        self._attr_source = source

    # ── Extra: send key by name ────────────────────────────────────────

    async def async_send_key(self, key: str) -> None:
        code = KEY_CODES.get(key.lower())
        if code is not None:
            await self._send_key(code)
        else:
            _LOGGER.warning(
                "Unknown key: %s. Available: %s", key, list(KEY_CODES.keys())
            )
