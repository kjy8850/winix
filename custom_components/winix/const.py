"""Constants for the Winix Dehumidifier component."""

from enum import Enum, unique
from typing import Final

__min_ha_version__ = "2024.8"

WINIX_DOMAIN: Final = "winix"  # WINIX 도메인 유지

WINIX_NAME: Final = "Winix Dehumidifier"  # 이름만 제습기로 변경
WINIX_DATA_KEY: Final = "winix_dehumidifier"
WINIX_DATA_COORDINATOR: Final = "coordinator"
WINIX_AUTH_RESPONSE: Final = "WinixAuthResponse"
WINIX_ACCESS_TOKEN_EXPIRATION: Final = "access_token_expiration"

# 제습기 관련 속성 추가
ATTR_HUMIDITY: Final = "current_humidity"  # 현재 습도
ATTR_TARGET_HUMIDITY: Final = "target_humidity"  # 목표 습도
ATTR_MODE: Final = "mode"  # 운전 모드
ATTR_FAN_SPEED: Final = "fan_speed"  # 팬 속도
ATTR_POWER: Final = "power"  # 전원 상태
ATTR_TIMER: Final = "timer"  # 타이머 설정
ATTR_CHILD_LOCK: Final = "child_lock"  # 차일드락 기능
ATTR_UV_STERILIZATION: Final = "uv_sterilization"  # UV 살균 기능

SENSOR_HUMIDITY: Final = "humidity"
SENSOR_TARGET_HUMIDITY: Final = "target_humidity"

OFF_VALUE: Final = "off"
ON_VALUE: Final = "on"

# 제습기 관련 서비스 추가
SERVICE_SET_HUMIDITY: Final = "set_humidity"  # 목표 습도 설정
SERVICE_SET_MODE: Final = "set_mode"  # 모드 변경 (자동, 연속, 의류 건조 등)
SERVICE_SET_FAN_SPEED: Final = "set_fan_speed"  # 팬 속도 조절
SERVICE_SET_TIMER: Final = "set_timer"  # 타이머 설정
SERVICE_CHILD_LOCK: Final = "set_child_lock"  # 차일드락 기능 ON/OFF
SERVICE_UV_STERILIZATION: Final = "set_uv_sterilization"  # UV 살균 기능 ON/OFF
SERVICE_REMOVE_STALE_ENTITIES: Final = "remove_stale_entities"  # 불필요한 엔티티 제거

HUMIDIFIER_SERVICES: Final = [
    SERVICE_SET_HUMIDITY,
    SERVICE_SET_MODE,
    SERVICE_SET_FAN_SPEED,
    SERVICE_SET_TIMER,
    SERVICE_CHILD_LOCK,
    SERVICE_UV_STERILIZATION,
]

# 팬 속도 정의 (API에 맞게 조정)
FAN_SPEED_HIGH: Final = "high"  # 강 (1)
FAN_SPEED_LOW: Final = "low"  # 약 (2)
FAN_SPEED_TURBO: Final = "turbo"  # 터보 (3)

ORDERED_NAMED_FAN_SPEEDS: Final = [
    FAN_SPEED_HIGH,
    FAN_SPEED_LOW,
    FAN_SPEED_TURBO,
]

# 제습기 운전 모드 (API에 맞게 조정)
MODE_AUTO: Final = "auto"  # 자동 (1)
MODE_MANUAL: Final = "manual"  # 수동 (2)
MODE_LAUNDRY: Final = "laundry_dry"  # 의류 건조 (3)
MODE_SHOES: Final = "shoes_dry"  # 신발 건조 (4)
MODE_SILENT: Final = "silent"  # 저소음 (5)
MODE_CONTINUOUS: Final = "continuous"  # 연속 (6)

PRESET_MODES: Final = [
    MODE_AUTO,
    MODE_MANUAL,
    MODE_LAUNDRY,
    MODE_SHOES,
    MODE_SILENT,
    MODE_CONTINUOUS,
]

# UI 표시용 한글 라벨
PRESET_MODE_LABELS: Final = {
    MODE_AUTO: "자동",
    MODE_MANUAL: "수동",
    MODE_LAUNDRY: "의류 건조",
    MODE_SHOES: "신발 건조",
    MODE_SILENT: "저소음",
    MODE_CONTINUOUS: "연속",
}

