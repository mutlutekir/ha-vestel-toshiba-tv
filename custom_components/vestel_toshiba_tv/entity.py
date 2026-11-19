"""Shared helpers for Vestel & Toshiba TV entities."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo

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
