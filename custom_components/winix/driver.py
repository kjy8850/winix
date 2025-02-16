from __future__ import annotations

import logging

import aiohttp

_LOGGER = logging.getLogger(__name__)

# Modified from https://github.com/hfern/winix to support async operations


class WinixDriver:
    """WinixDevice driver."""

    # pylint: disable=line-too-long
    CTRL_URL = "https://us.api.winix-iot.com/common/control/devices/{deviceid}/A211/{attribute}:{value}"
    STATE_URL = "https://us.api.winix-iot.com/common/event/sttus/devices/{deviceid}"
    PARAM_URL = "https://us.api.winix-iot.com/common/event/param/devices/{deviceid}"
    CONNECTED_STATUS_URL = (
        "https://us.api.winix-iot.com/common/event/connsttus/devices/{deviceid}"
    )

    category_keys = {
        "power": "D02",
        "mode": "D03",
        "fan_speed": "D04",
        "target_humidity": "D05",
        "child_lock": "D08",
        "current_humidity": "D10",
        "uv_sterilization": "D13",
        "timer": "D15",
    }

    state_keys = {
        "power": {"off": "0", "on": "1"},
        "mode": {
            "auto": "01",
            "manual": "02",
            "laundry_dry": "03",
            "shoes_dry": "04",
            "silent": "05",
            "continuous": "06"
        },
        "fan_speed": {
            "high": "01",
            "low": "02",
            "turbo": "03",
        },
        "child_lock": {"off": "0", "on": "1"},
        "uv_sterilization": {"off": "0", "on": "1"},
    }

    def __init__(self, device_id: str, client: aiohttp.ClientSession) -> None:
        """Create an instance of WinixDevice."""
        self.device_id = device_id
        self._client = client

    async def turn_off(self):
        """Turn the device off."""
        await self._rpc_attr(
            self.category_keys["power"], self.state_keys["power"]["off"]
        )

    async def turn_on(self):
        """Turn the device on."""
        await self._rpc_attr(
            self.category_keys["power"], self.state_keys["power"]["on"]
        )

    async def set_mode(self, mode):
        """Set device mode."""
        await self._rpc_attr(
            self.category_keys["mode"], self.state_keys["mode"].get(mode, "01")
        )

    async def set_fan_speed(self, speed):
        """Set fan speed."""
        await self._rpc_attr(
            self.category_keys["fan_speed"], self.state_keys["fan_speed"].get(speed, "01")
        )

    async def set_humidity(self, humidity):
        """Set target humidity."""
        await self._rpc_attr(self.category_keys["target_humidity"], str(humidity))

    async def set_timer(self, timer):
        """Set timer."""
        await self._rpc_attr(self.category_keys["timer"], str(timer))

    async def set_child_lock(self, lock: bool):
        """Enable or disable child lock."""
        value = "1" if lock else "0"
        await self._rpc_attr(self.category_keys["child_lock"], value)

    async def set_uv_sterilization(self, uv: bool):
        """Enable or disable UV sterilization."""
        value = "1" if uv else "0"
        await self._rpc_attr(self.category_keys["uv_sterilization"], value)

    async def _rpc_attr(self, attr: str, value: str):
        _LOGGER.debug("_rpc_attr attribute=%s, value=%s", attr, value)
        resp = await self._client.get(
            self.CTRL_URL.format(deviceid=self.device_id, attribute=attr, value=value),
            raise_for_status=True,
        )
        raw_resp = await resp.text()
        _LOGGER.debug("_rpc_attr response=%s", raw_resp)

    async def get_state(self) -> dict[str, str]:
        """Get device state."""
        response = await self._client.get(
            self.STATE_URL.format(deviceid=self.device_id)
        )
        json = await response.json()

        output = {}
        try:
            _LOGGER.debug(json)
            payload = json["body"]["data"][0]["attributes"]
        except Exception as err:
            _LOGGER.error(
                "Error parsing response json, received %s", json, exc_info=err
            )
            return output

        for payload_key, attribute in payload.items():
            for category, local_key in self.category_keys.items():
                if payload_key == local_key:
                    if category in self.state_keys:
                        for value_key, value in self.state_keys[category].items():
                            if attribute == value:
                                output[category] = value_key
                    else:
                        output[category] = int(attribute)
        return output
