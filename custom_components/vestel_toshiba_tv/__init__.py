"""Vestel & Toshiba TV Remote Control integration."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.loader import async_get_integration

from .const import DOMAIN, SIGNAL_OPTIONS_UPDATED

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["media_player", "button"]

CARD_FILENAME = "vestel_toshiba_tv-card.js"
# The card is served straight from custom_components/vestel_toshiba_tv/www
CARD_URL_BASE = f"/{DOMAIN}"
CARD_URL = f"{CARD_URL_BASE}/{CARD_FILENAME}"
# Versions up to 1.1.x copied the card to config/www and used this URL
LEGACY_CARD_URL = f"/local/{CARD_FILENAME}"
DATA_CARD_REGISTERED = f"{DOMAIN}_card_registered"


async def _async_register_card(hass: HomeAssistant) -> None:
    """Serve the dashboard card and add it as a dashboard resource (once)."""
    if hass.data.get(DATA_CARD_REGISTERED) or hass.http is None:
        return
    hass.data[DATA_CARD_REGISTERED] = True

    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL_BASE, str(Path(__file__).parent / "www"), False)]
    )
    integration = await async_get_integration(hass, DOMAIN)
    url = f"{CARD_URL}?v={integration.version}"

    lovelace = hass.data.get("lovelace")
    resources = getattr(lovelace, "resources", None)
    if resources is None or getattr(lovelace, "resource_mode", "storage") != "storage":
        _LOGGER.info(
            "Dashboard resources are managed in YAML; add the card yourself: "
            "url: %s, type: module",
            url,
        )
        return

    try:
        await resources.async_get_info()  # makes sure the resources are loaded
        found = False
        for item in list(resources.async_items()):
            if item.get("url", "").split("?")[0] not in (CARD_URL, LEGACY_CARD_URL):
                continue
            if found:  # duplicate entry for the card
                await resources.async_delete_item(item["id"])
            elif item["url"] != url:  # old /local/ URL or older version
                await resources.async_update_item(
                    item["id"], {"res_type": "module", "url": url}
                )
            found = True
        if not found:
            await resources.async_create_item({"res_type": "module", "url": url})
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning(
            "Could not add the card as a dashboard resource (%s). Add it under "
            "Settings > Dashboards > Resources: %s (JavaScript module)",
            err,
            url,
        )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Vestel & Toshiba TV from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await _async_register_card(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Apply new options without reloading the entry.

    A reload makes the TV briefly unavailable, and HomeKit Bridge only rebuilds
    the TV's inputs when the input list changes while the TV is available.
    """
    async_dispatcher_send(hass, SIGNAL_OPTIONS_UPDATED.format(entry.entry_id))


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
