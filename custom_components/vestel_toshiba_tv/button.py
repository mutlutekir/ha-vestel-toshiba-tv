"""Buttons for Vestel & Toshiba TV (volume steps and channel up/down).

These exist mainly for Apple Home: HomeKit Bridge exposes buttons as
switches, which Apple Home scenes (and therefore Siri) can trigger.
"""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import async_send_key_repeated
from .const import DEFAULT_PORT, KEY_CODES
from .entity import tv_device_info, volume_steps


@dataclass(frozen=True, kw_only=True)
class VestelToshibaButtonDescription(ButtonEntityDescription):
    """Describes a TV button."""

    key_name: str
    uses_volume_steps: bool = False


BUTTONS: tuple[VestelToshibaButtonDescription, ...] = (
    VestelToshibaButtonDescription(
        key="volume_up",
        translation_key="volume_up",
        icon="mdi:volume-plus",
        key_name="volume_up",
        uses_volume_steps=True,
    ),
    VestelToshibaButtonDescription(
        key="volume_down",
        translation_key="volume_down",
        icon="mdi:volume-minus",
        key_name="volume_down",
        uses_volume_steps=True,
    ),
    VestelToshibaButtonDescription(
        key="channel_up",
        translation_key="channel_up",
        icon="mdi:chevron-up-box",
        key_name="channel_up",
    ),
    VestelToshibaButtonDescription(
        key="channel_down",
        translation_key="channel_down",
        icon="mdi:chevron-down-box",
        key_name="channel_down",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the TV buttons from a config entry."""
    async_add_entities(
        VestelToshibaButton(entry, description) for description in BUTTONS
    )


class VestelToshibaButton(ButtonEntity):
    """A button that sends a remote key (optionally several times) to the TV."""

    _attr_has_entity_name = True
    entity_description: VestelToshibaButtonDescription

    def __init__(
        self, entry: ConfigEntry, description: VestelToshibaButtonDescription
    ) -> None:
        self.entity_description = description
        self._entry = entry
        self._host: str = entry.data["host"]
        self._port: int = entry.data.get("port", DEFAULT_PORT)
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = tv_device_info(
            entry.entry_id, entry.data.get("name", "Vestel & Toshiba TV")
        )

    async def async_press(self) -> None:
        """Send the key; volume buttons repeat it the configured number of times."""
        count = 1
        if self.entity_description.uses_volume_steps:
            count = volume_steps(self._entry)
        await async_send_key_repeated(
            self._host,
            self._port,
            KEY_CODES[self.entity_description.key_name],
            count,
        )
