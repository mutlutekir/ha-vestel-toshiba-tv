"""Shared helpers for Vestel & Toshiba TV entities."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo

from .api import TvConnectionError, async_send_key_repeated
from .const import CONF_VOLUME_STEPS, DEFAULT_VOLUME_STEPS, DOMAIN


def tv_device_info(entry_id: str, name: str) -> DeviceInfo:
    """Return the device that groups the TV's entities."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)},
        name=name,
        manufacturer="Vestel",
    )


def volume_steps(entry: ConfigEntry) -> int:
    """Number of key presses for one volume button press."""
    return int(entry.options.get(CONF_VOLUME_STEPS, DEFAULT_VOLUME_STEPS))


async def async_press_key(host: str, port: int, code: int, count: int = 1) -> None:
    """Press a remote key (count times); fail the action if the TV is unreachable."""
    try:
        await async_send_key_repeated(host, port, code, count)
    except TvConnectionError as err:
        raise HomeAssistantError(f"Could not reach the TV at {host}: {err}") from err
