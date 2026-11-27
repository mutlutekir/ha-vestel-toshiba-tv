"""Media player entity for Vestel & Toshiba TV Remote Control."""
from __future__ import annotations

import asyncio
import logging
import time
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
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoredExtraData, RestoreEntity
import voluptuous as vol

from .api import (
    TvEventListener,
    async_get_app_state,
    async_get_mute,
    async_get_volume,
    async_launch_app,
    async_stop_app,
)
from .const import (
    APP_CLOSE_DELAY,
    CHANNEL_KEYS,
    CONF_SHORTCUT_SOURCES,
    DATA_TV_ENTITY,
    DOMAIN,
    DMR_PORT,
    DEFAULT_PORT,
    DIAL_APP_PATH,
    DIAL_APPS,
    HOMEKIT_KEY_MAP,
    HOMEKIT_REMOTE_EVENT,
    KEY_CODES,
    LONG_OFFLINE,
    POWER_CONFIRM_TIMEOUT,
    POWER_RETRY_DELAY,
    SHORTCUT_SOURCES,
    SIGNAL_OPTIONS_UPDATED,
    SIGNAL_TV_ENTITY,
    SOURCE_LIST,
    TV_SOURCE,
    VOLUME_KEYS,
    VOLUME_SET_ROUNDS,
    WS_PORT,
    WS_RECONNECT_DELAY,
)
from .entity import async_press_key, tv_device_info, volume_steps

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


class VestelToshibaTV(MediaPlayerEntity, RestoreEntity):
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
        # Normal standby: the TV stays on the network, only the websocket says
        # so. Kept across restarts and short network drops.
        self._standby = False
        self._reachable: bool | None = None
        self._offline_since: float | None = None
        # Set while a power key press waits for the TV's websocket answer
        self._power_answer: asyncio.Future[bool] | None = None
        self._listener = TvEventListener(
            host, WS_PORT, self._handle_tv_event, WS_RECONNECT_DELAY
        )

    @property
    def available(self) -> bool:
        return self._available

    @property
    def state(self) -> MediaPlayerState:
        return self._attr_state

    @property
    def extra_restore_state_data(self) -> RestoredExtraData:
        """Remember standby across restarts (DIAL says "running" in standby)."""
        return RestoredExtraData({"standby": self._standby})

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
        if (last := await self.async_get_last_extra_data()) is not None:
            self._standby = bool(last.as_dict().get("standby", False))
            if self._standby:
                _LOGGER.debug("Restored: the TV was in standby before the restart")
                self._attr_state = MediaPlayerState.OFF
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

        # Tell the sensors which entity to follow
        self.hass.data[DOMAIN][DATA_TV_ENTITY.format(self._entry.entry_id)] = (
            self.entity_id
        )
        async_dispatcher_send(
            self.hass, SIGNAL_TV_ENTITY.format(self._entry.entry_id), self.entity_id
        )

    @callback
    def _handle_options_updated(self) -> None:
        """New options: publish the new input list (HomeKit picks it up)."""
        self.async_write_ha_state()

    @callback
    def _handle_tv_event(self, kind: str, value: str) -> None:
        """Standby / wake-up and volume events pushed by the TV."""
        if kind == "volume":
            self._attr_volume_level = int(value) / 100
            if self.hass is not None:
                self.async_write_ha_state()
            return
        if kind == "status":
            standby = value == "1"
        elif kind == "state":
            standby = False  # the TV reports its state only while in use
        else:
            return
        if self._power_answer is not None and not self._power_answer.done():
            self._power_answer.set_result(standby)
        new_state = MediaPlayerState.OFF if standby else MediaPlayerState.ON
        if standby != self._standby or new_state != self._attr_state:
            _LOGGER.debug(
                "Websocket: TV is %s (%s %s)",
                "in standby" if standby else "on",
                kind,
                value,
            )
            self._standby = standby
            self._attr_state = new_state
            if self.hass is not None:
                self.async_write_ha_state()

    async def _handle_homekit_key(self, event: Event) -> None:
        """Translate an Apple Home remote key into a TV key."""
        if event.data.get("entity_id") != self.entity_id:
            return
        key = HOMEKIT_KEY_MAP.get(event.data.get("key_name"))
        if key is not None:
            try:
                await self.async_send_key(key)
            except HomeAssistantError as err:
                _LOGGER.warning("Apple Home remote key %s not sent: %s", key, err)

    # ── Polling ────────────────────────────────────────────────────────

    async def async_update(self) -> None:
        """Fetch DIAL state and audio information from DLNA or SmartCenter."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self._dial_url,
                    timeout=aiohttp.ClientTimeout(total=3),
                ) as resp:
                    self._available = True
                    if self._reachable is False:
                        await self._async_back_on_network()
                    self._reachable = True
                    self._offline_since = None
                    if resp.status == 200:
                        dial = self._parse_dial_state(await resp.text())
                    else:
                        dial = f"HTTP {resp.status}"
                    if self._standby:
                        # DIAL says "running" in standby too
                        new_state = MediaPlayerState.OFF
                    elif dial == "running":
                        new_state = MediaPlayerState.ON
                    else:
                        new_state = MediaPlayerState.STANDBY
                    if new_state != self._attr_state:
                        _LOGGER.debug(
                            "Poll: TV is %s (standby %s, DIAL SmartCenter %s)",
                            new_state,
                            self._standby,
                            dial,
                        )
                    self._attr_state = new_state
        except (aiohttp.ClientError, TimeoutError) as err:
            # Switched fully off, or a short network drop (some TVs drop off
            # the network now and then while in standby)
            if self._reachable is not False:
                _LOGGER.debug(
                    "Poll: TV is not answering (fully off or off the network): %s",
                    err,
                )
                self._offline_since = time.monotonic()
            self._available = True
            self._reachable = False
            self._attr_state = MediaPlayerState.OFF
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Update error: %s", err)
            self._available = False

        if self._attr_state == MediaPlayerState.ON:
            await self._async_read_volume()
            await self._async_read_running_app()

    async def _async_back_on_network(self) -> None:
        """The TV answers again after being off the network."""
        offline = time.monotonic() - (self._offline_since or time.monotonic())
        if self._standby and offline >= LONG_OFFLINE:
            # Off the network for a long time: it was switched fully off
            # and has started up again, so let DIAL decide
            _LOGGER.debug(
                "TV is back after %.0f s off the network: no longer in standby",
                offline,
            )
            self._standby = False
        else:
            # A short drop does not mean the TV was switched on
            _LOGGER.debug(
                "TV is back after %.0f s off the network; keeping its last state (%s)",
                offline,
                "standby" if self._standby else "on",
            )
        # The old websocket is dead
        await self._listener.async_reconnect()

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

    async def _async_get_volume(self) -> int | None:
        """Use the existing event listener when DLNA volume is unavailable."""
        return await async_get_volume(
            self._host,
            DMR_PORT,
            smartcenter=lambda: self._listener.async_get_volume(self._port),
        )

    async def _async_read_volume(self) -> None:
        """Read volume from DLNA or SmartCenter; mute still uses DLNA."""
        volume = await self._async_get_volume()
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

    async def _send_key(self, code: int, count: int = 1) -> None:
        await async_press_key(self._host, self._port, code, count)

    # ── Standard actions ───────────────────────────────────────────────

    async def async_turn_on(self) -> None:
        # The power key toggles, so only press it when the TV is off
        if self._attr_state == MediaPlayerState.OFF:
            await self._async_power(turn_on=True)

    async def async_turn_off(self) -> None:
        if self._attr_state != MediaPlayerState.OFF:
            await self._async_power(turn_on=False)

    async def _async_power(self, turn_on: bool) -> None:
        """Press the power key (a toggle) and make sure it went the right way.

        Home Assistant can be wrong about the power state, for example right
        after a restart. The TV answers a power press on its websocket:
        "tv_status:1" when it goes to standby, "tv_state" when it wakes up.
        If it answers the opposite of what was asked, the TV was already in
        the wanted state and the press toggled it, so press power again.
        """
        went_to_standby = await self._async_press_power()
        if went_to_standby == turn_on:
            # Let the TV settle: a later event may still show it went right
            await asyncio.sleep(POWER_RETRY_DELAY)
            if self._standby == turn_on:
                _LOGGER.warning(
                    "The TV was already %s, so the power key switched it %s; "
                    "pressing power again",
                    "on" if turn_on else "in standby",
                    "off" if turn_on else "on",
                )
                went_to_standby = await self._async_press_power()
                if went_to_standby is None:
                    _LOGGER.warning(
                        "The TV did not answer the second power key press"
                    )
        if went_to_standby is None:
            # No answer from the TV: assume the key did what was asked
            if turn_on:
                if self._reachable is not False:
                    self._standby = False
                    self._attr_state = MediaPlayerState.ON
            else:
                self._standby = True
                self._attr_state = MediaPlayerState.OFF

    async def _async_press_power(self) -> bool | None:
        """Press power. Return True (standby) / False (awake) as the TV
        reports it on its websocket, or None if it does not answer."""
        answer: asyncio.Future[bool] | None = None
        if self._listener.connected:
            answer = asyncio.get_running_loop().create_future()
        self._power_answer = answer
        try:
            await self._send_key(KEY_CODES["power"])
            if answer is None:
                _LOGGER.debug("Power key sent (no websocket to confirm it)")
                return None
            try:
                return await asyncio.wait_for(answer, POWER_CONFIRM_TIMEOUT)
            except TimeoutError:
                _LOGGER.debug("Power key sent, no answer from the TV's websocket")
                return None
        finally:
            self._power_answer = None

    async def async_volume_up(self) -> None:
        await self._send_key(KEY_CODES["volume_up"])

    async def async_volume_down(self) -> None:
        await self._send_key(KEY_CODES["volume_down"])

    async def async_set_volume_level(self, volume: float) -> None:
        """Reach an exact volume with remote keys (the TV only accepts keys)."""
        target = round(volume * 100)
        for _ in range(VOLUME_SET_ROUNDS):
            current = await self._async_get_volume()
            if current is None:
                raise HomeAssistantError(
                    "Could not read the TV volume via DLNA or SmartCenter"
                )
            diff = target - current
            if diff == 0:
                break
            key = "volume_up" if diff > 0 else "volume_down"
            await self._send_key(KEY_CODES[key], min(abs(diff), 100))
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
            await self._send_key(KEY_CODES[key], count)
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
                _LOGGER.debug("%s closed, back to the TV broadcast", app)
                closed = True
        if closed:
            await asyncio.sleep(APP_CLOSE_DELAY)
        return closed

    # ── Extra: send key by name ────────────────────────────────────────

    async def async_send_key(self, key: str) -> None:
        code = KEY_CODES.get(key.lower())
        if code is None:
            raise ServiceValidationError(
                f"Unknown key: {key}. Available keys: {', '.join(KEY_CODES)}"
            )
        await self._send_key(code)
