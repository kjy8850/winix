from __future__ import annotations

import dataclasses
import aiohttp

from .const import (
    FAN_SPEED_LOW,
    FAN_SPEED_HIGH,
    FAN_SPEED_TURBO,
    ATTR_HUMIDITY,
    ATTR_TARGET_HUMIDITY,
    ATTR_MODE,
    ATTR_POWER,
    ATTR_TIMER,
    ATTR_CHILD_LOCK,
    ATTR_UV_STERILIZATION,
    MODE_AUTO,
    MODE_MANUAL,
    MODE_LAUNDRY,
    MODE_SHOES,
    MODE_CONTINUOUS,
    MODE_SILENT,
    OFF_VALUE,
    ON_VALUE,
)
from .driver import WinixDriver

@dataclasses.dataclass
class MyWinixDeviceStub:
    """Winix dehumidifier device information."""
    
    id: str
    mac: str
    alias: str
    location_code: str
    filter_replace_date: str
    model: str
    sw_version: str

class WinixDeviceWrapper:
    """Representation of the Winix dehumidifier data."""

    def __init__(
        self,
        client: aiohttp.ClientSession,
        device_stub: MyWinixDeviceStub,
        logger,
    ) -> None:
        """Initialize the wrapper."""

        self._driver = WinixDriver(device_stub.id, client)
        self._state = {}
        self._on = False
        self._logger = logger
        self.device_stub = device_stub
        self._alias = device_stub.alias

    async def update(self) -> None:
        """Update the device data."""
        self._state = await self._driver.get_state()
        self._on = self._state.get(ATTR_POWER) == ON_VALUE
        
        self._logger.debug(
            "%s: updated on=%s, target_humidity=%s, fan_speed=%s, timer=%s",
            self._alias,
            self._on,
            self._state.get(ATTR_HUMIDITY),
            self._state.get(ATTR_TARGET_HUMIDITY),
            self._state.get(ATTR_MODE),
            self._state.get(ATTR_TIMER),
        )

    def get_state(self) -> dict[str, str]:
        """Return the device data."""
        return self._state

    @property
    def is_on(self) -> bool:
        """Return if the dehumidifier is on."""
        return self._on

    async def async_turn_on(self) -> None:
        """Turn on the dehumidifier."""
        if not self._on:
            self._on = True
            self._logger.debug("%s => turned on", self._alias)
            await self._driver.turn_on()

    async def async_turn_off(self) -> None:
        """Turn off the dehumidifier."""
        if self._on:
            self._on = False
            self._logger.debug("%s => turned off", self._alias)
            await self._driver.turn_off()

    async def async_set_humidity(self, target_humidity: int) -> None:
        """Set the target humidity level."""
        self._state[ATTR_TARGET_HUMIDITY] = target_humidity
        self._logger.debug("%s => set target humidity=%s", self._alias, target_humidity)
        await self._driver.set_humidity(target_humidity)

    async def async_set_mode(self, mode: str) -> None:
        """Set the operating mode."""
        self._state[ATTR_MODE] = mode
        self._logger.debug("%s => set mode=%s", self._alias, mode)
        await self._driver.set_mode(mode)

    async def async_set_fan_speed(self, speed: str) -> None:
        """Set the fan speed."""
        self._state[ATTR_MODE] = speed
        self._logger.debug("%s => set fan speed=%s", self._alias, speed)
        await self._driver.set_fan_speed(speed)

    async def async_set_timer(self, timer: int) -> None:
        """Set the timer (0-12 hours)."""
        self._state[ATTR_TIMER] = timer
        self._logger.debug("%s => set timer=%s", self._alias, timer)
        await self._driver.set_timer(timer)

    async def async_set_child_lock(self, lock: bool) -> None:
        """Enable or disable child lock."""
        self._state[ATTR_CHILD_LOCK] = ON_VALUE if lock else OFF_VALUE
        self._logger.debug("%s => set child lock=%s", self._alias, lock)
        await self._driver.set_child_lock(lock)

    async def async_set_uv_sterilization(self, uv: bool) -> None:
        """Enable or disable UV sterilization."""
        self._state[ATTR_UV_STERILIZATION] = ON_VALUE if uv else OFF_VALUE
        self._logger.debug("%s => set UV sterilization=%s", self._alias, uv)
        await self._driver.set_uv_sterilization(uv)
