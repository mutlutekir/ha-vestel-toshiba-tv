"""Sensors for Vestel & Toshiba TV: what the TV is doing and its volume.

They follow the TV's media player entity, so they always match it.
"""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_OFF,
    STATE_STANDBY,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import Event, EventStateChangedData, HomeAssistant, State, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

from .const import DATA_TV_ENTITY, DOMAIN, SIGNAL_TV_ENTITY, SOURCE_LIST
from .entity import tv_device_info

# Activity sensor states (translated in strings.json)
ACTIVITY_OFF = "off"
ACTIVITY_OPTIONS = [ACTIVITY_OFF, *(source.lower() for source in SOURCE_LIST)]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the TV sensors from a config entry."""
    async_add_entities([VestelActivitySensor(entry), VestelVolumeSensor(entry)])


class _TvFollowerSensor(SensorEntity):
    """A sensor computed from the TV's media player state."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, key: str) -> None:
        self._entry = entry
        self._attr_translation_key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = tv_device_info(
            entry.entry_id, entry.data.get("name", "Vestel & Toshiba TV")
        )
        self._attr_available = False
        self._unsub_state = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        signal = SIGNAL_TV_ENTITY.format(self._entry.entry_id)
        self.async_on_remove(
            async_dispatcher_connect(self.hass, signal, self._follow)
        )
        self.async_on_remove(self._unfollow)
        # The media player may already be there (platforms load in any order)
        key = DATA_TV_ENTITY.format(self._entry.entry_id)
        if (tv_entity_id := self.hass.data.get(DOMAIN, {}).get(key)) is not None:
            self._start_following(tv_entity_id)  # first state is written by HA

    @callback
    def _follow(self, tv_entity_id: str) -> None:
        """The media player announced itself (it was added after us)."""
        self._start_following(tv_entity_id)
        self.async_write_ha_state()

    @callback
    def _start_following(self, tv_entity_id: str) -> None:
        self._unfollow()
        self._unsub_state = async_track_state_change_event(
            self.hass, [tv_entity_id], self._on_tv_state
        )
        self._apply(self.hass.states.get(tv_entity_id))

    @callback
    def _unfollow(self) -> None:
        if self._unsub_state is not None:
            self._unsub_state()
            self._unsub_state = None

    @callback
    def _on_tv_state(self, event: Event[EventStateChangedData]) -> None:
        self._apply(event.data["new_state"])
        self.async_write_ha_state()

    @callback
    def _apply(self, state: State | None) -> None:
        self._attr_available = state is not None and state.state not in (
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
        )
        if self._attr_available:
            self._update_value(state)

    @callback
    def _update_value(self, state: State) -> None:
        raise NotImplementedError


class VestelActivitySensor(_TvFollowerSensor):
    """Off, TV broadcast, YouTube or Netflix."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ACTIVITY_OPTIONS
    _attr_icon = "mdi:television-classic"

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "activity")

    @callback
    def _update_value(self, state: State) -> None:
        if state.state in (STATE_OFF, STATE_STANDBY):
            self._attr_native_value = ACTIVITY_OFF
            return
        source = state.attributes.get("source")
        if source in SOURCE_LIST:
            self._attr_native_value = source.lower()
        elif self._attr_native_value in (None, ACTIVITY_OFF):
            # On, but no input known yet (or a shortcut is running): broadcast
            self._attr_native_value = "tv"
        # A shortcut input (e.g. "Volume up") is shown only briefly: keep the
        # last real activity


class VestelVolumeSensor(_TvFollowerSensor):
    """The TV's real volume (0-100); unknown while the TV is off."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:volume-high"

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry, "volume")

    @callback
    def _update_value(self, state: State) -> None:
        level = state.attributes.get("volume_level")
        self._attr_native_value = (
            round(level * 100) if isinstance(level, (int, float)) else None
        )
