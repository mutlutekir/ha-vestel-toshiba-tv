"""Config flow for Vestel & Toshiba TV Remote Control."""
from __future__ import annotations

import asyncio
import ipaddress
import logging
import xml.etree.ElementTree as ET
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import network
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_SHORTCUT_SOURCES,
    CONF_VOLUME_STEPS,
    DEFAULT_PORT,
    DEFAULT_VOLUME_STEPS,
    DIAL_APP_PATH,
    DOMAIN,
    MAX_VOLUME_STEPS,
    MIN_VOLUME_STEPS,
)

MANUAL_OPTION = "manual"

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("host"): str,
        vol.Optional("port", default=DEFAULT_PORT): int,
        vol.Optional("name", default="Vestel & Toshiba TV"): str,
    }
)


async def _test_connection(host: str, port: int) -> dict | None:
    """Test connection and fetch TV info from DIAL endpoint."""
    url = f"http://{host}:{port}{DIAL_APP_PATH}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    return {"raw": text}
    except Exception:
        pass
    return None


_LOGGER = logging.getLogger(__name__)


async def _async_get_local_subnets(hass: HomeAssistant) -> list[str]:
    """Return local /24 subnets from HA's enabled network adapters."""
    subnets: list[str] = []
    try:
        for adapter in await network.async_get_adapters(hass):
            if not adapter["enabled"]:
                continue
            for ip_info in adapter["ipv4"]:
                ip = ip_info["address"]
                if ip and not ip.startswith("127."):
                    net = str(ipaddress.IPv4Network(f"{ip}/24", strict=False))
                    if net not in subnets:
                        subnets.append(net)
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Network adapters could not be read: %s", err)

    # Fallback: derive from HA's own IP stored in config
    if not subnets:
        try:
            ha_ip = str(hass.config.api.local_ip)  # type: ignore[union-attr]
            if ha_ip and not ha_ip.startswith("127."):
                subnets.append(str(ipaddress.IPv4Network(f"{ha_ip}/24", strict=False)))
        except Exception:
            pass

    # Last resort
    if not subnets:
        subnets = ["192.168.1.0/24"]

    return list(dict.fromkeys(subnets))  # deduplicate


async def _discover_tvs(hass: HomeAssistant) -> list[dict]:
    """Discover Vestel/Toshiba TVs on the local network via DIAL."""
    found: list[dict] = []
    subnets = await _async_get_local_subnets(hass)

    async def check_host(ip: str) -> None:
        url = f"http://{ip}:{DEFAULT_PORT}{DIAL_APP_PATH}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=1)
                ) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        name = "Vestel/Toshiba TV"
                        try:
                            root = ET.fromstring(text)
                            ns = {"dial": "urn:dial-multiscreen-org:schemas:dial"}
                            name_el = root.find("dial:name", ns)
                            if name_el is not None and name_el.text:
                                name = name_el.text
                        except Exception:
                            pass
                        found.append({"host": ip, "name": f"{name} ({ip})"})
        except Exception:
            pass

    all_ips: list[str] = []
    for subnet in subnets:
        try:
            net = ipaddress.IPv4Network(subnet, strict=False)
            all_ips.extend(str(ip) for ip in net.hosts())
        except Exception:
            pass

    # Deduplicate and scan
    tasks = [check_host(ip) for ip in dict.fromkeys(all_ips)]
    await asyncio.gather(*tasks)
    return found


class VestelToshibaTVConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vestel & Toshiba TV Remote Control."""

    VERSION = 1

    def __init__(self) -> None:
        self._discovered_tvs: list[dict] = []

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> VestelToshibaTVOptionsFlow:
        """Return the options flow."""
        return VestelToshibaTVOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step — show discovery or manual entry."""
        # Kick off discovery first
        self._discovered_tvs = await _discover_tvs(self.hass)

        if self._discovered_tvs:
            return await self.async_step_discovery_confirm()
        return await self.async_step_manual()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show discovered TVs and let the user pick one."""
        errors: dict[str, str] = {}

        if user_input is not None:
            selected = user_input["tv"]
            if selected == MANUAL_OPTION:
                return await self.async_step_manual()

            host, _, label = selected.partition("|")
            result = await _test_connection(host, DEFAULT_PORT)
            if result is None:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"{host}_{DEFAULT_PORT}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=label or f"TV ({host})",
                    data={"host": host, "port": DEFAULT_PORT, "name": label},
                )

        tv_options = [
            SelectOptionDict(value=f"{tv['host']}|{tv['name']}", label=tv["name"])
            for tv in self._discovered_tvs
        ]
        # Label comes from translations (selector.tv.options.manual);
        # the English text here is only a fallback.
        tv_options.append(
            SelectOptionDict(value=MANUAL_OPTION, label="➕ Enter IP address manually")
        )

        schema = vol.Schema(
            {
                vol.Required("tv"): SelectSelector(
                    SelectSelectorConfig(
                        options=tv_options,
                        mode=SelectSelectorMode.LIST,
                        translation_key="tv",
                    )
                )
            }
        )

        return self.async_show_form(
            step_id="discovery_confirm",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "count": str(len(self._discovered_tvs))
            },
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual IP entry step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input["host"].strip()
            port = user_input.get("port", DEFAULT_PORT)
            name = user_input.get("name", "Vestel & Toshiba TV")

            result = await _test_connection(host, port)
            if result is None:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"{host}_{port}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=name,
                    data={"host": host, "port": port, "name": name},
                )

        return self.async_show_form(
            step_id="manual",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class VestelToshibaTVOptionsFlow(config_entries.OptionsFlow):
    """Options: volume step size and the Apple Home / Siri shortcut inputs."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(
                data={
                    CONF_VOLUME_STEPS: int(user_input[CONF_VOLUME_STEPS]),
                    CONF_SHORTCUT_SOURCES: bool(
                        user_input.get(CONF_SHORTCUT_SOURCES, False)
                    ),
                }
            )

        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_VOLUME_STEPS,
                    default=options.get(CONF_VOLUME_STEPS, DEFAULT_VOLUME_STEPS),
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=MIN_VOLUME_STEPS,
                        max=MAX_VOLUME_STEPS,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_SHORTCUT_SOURCES,
                    default=options.get(CONF_SHORTCUT_SOURCES, False),
                ): BooleanSelector(),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
