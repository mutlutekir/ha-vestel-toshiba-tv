"""Media player entity for Vestel & Toshiba TV Remote Control."""
from __future__ import annotations

import asyncio
import logging
import xml.etree.ElementTree as ET

import aiohttp

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import voluptuous as vol

from .api import (
    TvEventListener,
    async_get_app_state,
    async_get_mute,
    async_get_volume,
    async_launch_app,
    async_send_key,
    async_send_key_repeated,
    async_stop_app,
)
from .const import (
    APP_CLOSE_DELAY,
    CHANNEL_KEYS,
    CONF_SHORTCUT_SOURCES,
    DMR_PORT,
    DEFAULT_PORT,
    DIAL_APP_PATH,
    DIAL_APPS,
    HOMEKIT_KEY_MAP,
    HOMEKIT_REMOTE_EVENT,
    KEY_CODES,
    SHORTCUT_SOURCES,
    SIGNAL_OPTIONS_UPDATED,
    SOURCE_LIST,
    TV_SOURCE,
    VOLUME_KEYS,
    VOLUME_SET_ROUNDS,
    WS_PORT,
    WS_RECONNECT_DELAY,
)
from .entity import tv_device_info, volume_steps

_LOGGER = logging.getLogger(__name__)

SUPPORTED_FEATURES = (
    MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_SET
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
        entry=entry,
    )
    async_add_entities([entity], update_before_add=True)

    # Entity service: Home Assistant resolves the targeted TV(s)
    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        "send_key", {vol.Required("key"): cv.string}, "async_send_key"
    )


class VestelToshibaTV(MediaPlayerEntity):
    """Representation of a Vestel/Toshiba TV via DIAL protocol."""

    _attr_has_entity_name = False
    _attr_supported_features = SUPPORTED_FEATURES
    _attr_icon = "mdi:television-play"
    _attr_device_class = MediaPlayerDeviceClass.TV

    def __init__(
        self, host: str, port: int, name: str, unique_id: str, entry: ConfigEntry
    ) -> None:
        self._entry = entry
        self._host = host
        self._port = port
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_device_info = tv_device_info(unique_id, name)
        self._attr_state = MediaPlayerState.OFF
        self._attr_source = None
        self._attr_is_volume_muted = False
        self._base_url = f"http://{host}:{port}"
        self._dial_url = f"{self._base_url}{DIAL_APP_PATH}"
        self._available = False
        # Normal standby: the TV stays on the network, only the websocket says so
        self._standby = False
        self._reachable: bool | None = None
        self._listener = TvEventListener(
            host, WS_PORT, self._handle_tv_event, WS_RECONNECT_DELAY
        )

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> MediaPlayerState:
        return self._attr_state

    # ── Sources (inputs) ───────────────────────────────────────────────

    def _shortcut_sources(self) -> dict[str, str]:
        """Shortcut input name -> remote key, or {} when the option is off."""
        if not self._entry.options.get(CONF_SHORTCUT_SOURCES, False):
            return {}
        language = "en"
        if self.hass is not None and (self.hass.config.language or "").startswith(
            "tr"
        ):
            language = "tr"
        return {names[language]: key for key, names in SHORTCUT_SOURCES.items()}

    @property
    def source_list(self) -> list[str]:
        # Shortcuts go last so the real inputs stay at the top
        return [*SOURCE_LIST, *self._shortcut_sources()]

    # ── Apple Home (HomeKit Bridge) remote ─────────────────────────────

    async def async_added_to_hass(self) -> None:
        """Listen for Apple Home remote keys and for the TV's own events."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self.hass.bus.async_listen(
                HOMEKIT_REMOTE_EVENT, self._handle_homekit_key
            )
        )
        task = self._entry.async_create_background_task(
            self.hass, self._listener.run(), f"{self.entity_id} TV events"
        )
        self.async_on_remove(task.cancel)
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_OPTIONS_UPDATED.format(self._entry.entry_id),
                self._handle_options_updated,
            )
        )

    @callback
    def _handle_options_updated(self) -> None:
        """New options: publish the new input list (HomeKit picks it up)."""
        self.async_write_ha_state()

    @callback
    def _handle_tv_event(self, kind: str, value: str) -> None:
        """Standby / wake-up events pushed by the TV."""
        if kind == "status":
            standby = value == "1"
        elif kind == "state":
            standby = False  # the TV reports its state only while in use
        else:
            return
        if standby != self._standby:
            _LOGGER.debug("TV %s", "bekleme modunda" if standby else "acildi")
            self._standby = standby
            self._attr_state = MediaPlayerState.OFF if standby else MediaPlayerState.ON
            if self.hass is not None:
                self.async_write_ha_state()

    async def _handle_homekit_key(self, event: Event) -> None:
        """Translate an Apple Home remote key into a TV key."""
        if event.data.get("entity_id") != self.entity_id:
            return
        key = HOMEKIT_KEY_MAP.get(event.data.get("key_name"))
        if key is not None:
            await self.async_send_key(key)

    # ── Polling ────────────────────────────────────────────────────────

    async def async_update(self) -> None:
        """Fetch TV state from DIAL, volume and mute from the DLNA renderer."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self._dial_url,
                    timeout=aiohttp.ClientTimeout(total=3),
                ) as resp:
                    self._available = True
                    if self._reachable is False:
                        # Back on the network after being fully off: it booted
                        # up, so it is on, and the old websocket is dead
                        self._standby = False
                        await self._listener.async_reconnect()
                    self._reachable = True
                    if self._standby:
                        self._attr_state = MediaPlayerState.OFF
                    elif resp.status == 200:
                        state = self._parse_dial_state(await resp.text())
                        self._attr_state = (
                            MediaPlayerState.ON
                            if state == "running"
                            else MediaPlayerState.STANDBY
                        )
                    else:
                        self._attr_state = MediaPlayerState.STANDBY
        except (aiohttp.ClientError, TimeoutError) as err:
            # Fully switched off: the TV drops off the network
            _LOGGER.debug("TV yanit vermiyor (tamamen kapali): %s", err)
            self._available = True
            self._reachable = False
            self._attr_state = MediaPlayerState.OFF
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Update error: %s", err)
            self._available = False

        if self._attr_state == MediaPlayerState.ON:
            await self._async_read_volume()
            await self._async_read_running_app()

    async def _async_read_running_app(self) -> None:
        """Show Netflix/YouTube as the input while they are open."""
        for source, (app, origin) in DIAL_APPS.items():
            state = await async_get_app_state(self._host, self._port, app, origin)
            if state == "running":
                self._attr_source = source
                return
        if self._attr_source in DIAL_APPS:
            # The app was closed: the TV went back to its broadcast
            self._attr_source = TV_SOURCE

    async def _async_read_volume(self) -> None:
        """Read the real volume and mute state from the TV's DLNA renderer."""
        volume = await async_get_volume(self._host, DMR_PORT)
        if volume is not None:
            self._attr_volume_level = min(volume, 100) / 100
        muted = await async_get_mute(self._host, DMR_PORT)
        if muted is not None:
            self._attr_is_volume_muted = muted

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
        await async_send_key(self._host, self._port, code)

    # ── Standard actions ───────────────────────────────────────────────

    async def async_turn_on(self) -> None:
        # The power key toggles, so only press it when the TV is off
        if self._attr_state == MediaPlayerState.OFF:
            await self._send_key(KEY_CODES["power"])
            if self._reachable is not False:
                self._standby = False
                self._attr_state = MediaPlayerState.ON

    async def async_turn_off(self) -> None:
        if self._attr_state != MediaPlayerState.OFF:
            await self._send_key(KEY_CODES["power"])
            self._standby = True
            self._attr_state = MediaPlayerState.OFF

    async def async_volume_up(self) -> None:
        await self._send_key(KEY_CODES["volume_up"])

    async def async_volume_down(self) -> None:
        await self._send_key(KEY_CODES["volume_down"])

    async def async_set_volume_level(self, volume: float) -> None:
        """Reach an exact volume with remote keys (the TV only accepts keys)."""
        target = round(volume * 100)
        for _ in range(VOLUME_SET_ROUNDS):
            current = await async_get_volume(self._host, DMR_PORT)
            if current is None:
                _LOGGER.warning(
                    "TV ses seviyesi okunamadi (DLNA port %s); ses ayarlanamadi",
                    DMR_PORT,
                )
                return
            diff = target - current
            if diff == 0:
                break
            key = "volume_up" if diff > 0 else "volume_down"
            await async_send_key_repeated(
                self._host, self._port, KEY_CODES[key], min(abs(diff), 100)
            )
            await asyncio.sleep(0.5)  # let the renderer catch up
        await self._async_read_volume()

    async def async_mute_volume(self, mute: bool) -> None:
        current = await async_get_mute(self._host, DMR_PORT)
        if current is None or current != mute:
            await self._send_key(KEY_CODES["mute"])
        self._attr_is_volume_muted = mute

    async def async_media_next_track(self) -> None:
        await self._send_key(KEY_CODES["channel_up"])

    async def async_media_previous_track(self) -> None:
        await self._send_key(KEY_CODES["channel_down"])

    async def async_media_play(self) -> None:
        await self._send_key(KEY_CODES["play"])

    async def async_media_stop(self) -> None:
        await self._send_key(KEY_CODES["stop"])

    async def async_select_source(self, source: str) -> None:
        if (key := self._shortcut_sources().get(source)) is not None:
            await self._async_run_shortcut(source, key)
            return
        if source == TV_SOURCE:
            # Back to the broadcast: closes Netflix/YouTube if one is open
            await self._async_return_to_broadcast()
            self._attr_source = TV_SOURCE
            return
        if (dial_app := DIAL_APPS.get(source)) is None:
            raise ServiceValidationError(f"Unknown source: {source}")
        app, origin = dial_app
        if not await async_launch_app(self._host, self._port, app, origin):
            raise HomeAssistantError(f"The TV did not start {source}")
        self._attr_source = source

    async def _async_run_shortcut(self, source: str, key: str) -> None:
        """Run a shortcut input, then show a real input again.

        After a channel step the TV is on its broadcast, so "TV" is shown;
        after a volume step the previous input is shown again. Either way
        Apple Home deselects the shortcut, so it can be chosen again.
        """
        is_channel = key in CHANNEL_KEYS
        previous = self._attr_source
        self._attr_source = source
        self.async_write_ha_state()
        try:
            if is_channel:
                # Channel keys only work on the broadcast, not inside an app
                await self._async_return_to_broadcast()
            count = volume_steps(self._entry) if key in VOLUME_KEYS else 1
            await async_send_key_repeated(
                self._host, self._port, KEY_CODES[key], count
            )
        finally:
            self._attr_source = TV_SOURCE if is_channel else previous
            self.async_write_ha_state()

    async def _async_return_to_broadcast(self) -> bool:
        """Close Netflix/YouTube if running. Return True if one was closed."""
        closed = False
        for app, origin in DIAL_APPS.values():
            state = await async_get_app_state(self._host, self._port, app, origin)
            if state == "running" and await async_stop_app(
                self._host, self._port, app, origin
            ):
                _LOGGER.debug("%s kapatildi, TV yayinina donuluyor", app)
                closed = True
        if closed:
            await asyncio.sleep(APP_CLOSE_DELAY)
        return closed

    # ── Extra: send key by name ────────────────────────────────────────

    async def async_send_key(self, key: str) -> None:
        code = KEY_CODES.get(key.lower())
        if code is not None:
            await self._send_key(code)
        else:
            _LOGGER.warning(
                "Unknown key: %s. Available: %s", key, list(KEY_CODES.keys())
            )
