""" Sunology const file """
from enum import StrEnum

DOMAIN = "sunology"

CONF_GATEWAY_HOST = "lan_gateway_host"
CONF_GATEWAY_PORT = "lan_gateway_port"

# NEW: cloud credentials for write operations
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

GATEWAY_DEFAULT_PORT = 20199

MIN_UNTIL_REFRESH = 2

PACKAGE_NAME = f"custom_components.{DOMAIN}"


class SmartMeterPhase(StrEnum):
    """Phase of a smart meter."""
    ALL = "All"
    PHASE_1 = "P1"
    PHASE_2 = "P2"
    PHASE_3 = "P3"

class SmartMeterTarifIndex(StrEnum):
    """Phase of a smart meter."""
    INDEX_1 = "idx1"
    INDEX_2 = "idx2"
    INDEX_3 = "idx3"
    INDEX_4 = "idx4"
    INDEX_5 = "idx5"
    INDEX_6 = "idx6"
    INDEX_7 = "idx7"
    INDEX_8 = "idx8"
    INDEX_9 = "idx9"
    INDEX_10 = "idx10"

class ElectricalDataFeature(StrEnum):
    """Phase of a smart meter."""
    UNUSED = "UNUSED"
    PRODUCER = "PRODUCER"
    LOAD = "LOAD"
    GRID = "GRID"
    PRODUCER_REV = "PRODUCER_REV"
    LOAD_REV = "LOAD_REV"
    GRID_REV = "GRID_REV"

class FlowWorkingModes(StrEnum):
    """Phase of a smart meter."""
    COST_OPTIM = "COST_OPTIM"
    POWER_OPTIM = "POWER_OPTIM"


# NEW: known STOREY working modes (incomplete — capture MANUEL/SUNCAST/EXPERT
# values via the mobile app to extend this enum)
class StoreyWorkingMode(StrEnum):
    HUB_REMOTE = "HUB_REMOTE"
    CLOUD_SCHEDULE = "CLOUD_SCHEDULE"


class StoreyPilotMode(StrEnum):
    """User-facing battery pilot mode (as shown in the Sunology app)."""
    MANUEL = "MANUEL"
    SUNCAST = "SUNCAST"
    EXPERT = "EXPERT"


# Mapping pilot mode → (cloudScheduleParameter on /api/client, workingMode on STOREY)
PILOT_MODE_TO_CLOUD_PARAM: dict[str, str | None] = {
    StoreyPilotMode.MANUEL: "MANUAL",
    StoreyPilotMode.SUNCAST: "SUNCAST",
    StoreyPilotMode.EXPERT: None,
}

PILOT_MODE_TO_WORKING_MODE: dict[str, str] = {
    StoreyPilotMode.MANUEL: StoreyWorkingMode.CLOUD_SCHEDULE,
    StoreyPilotMode.SUNCAST: StoreyWorkingMode.CLOUD_SCHEDULE,
    StoreyPilotMode.EXPERT: StoreyWorkingMode.HUB_REMOTE,
}

# Reverse mapping to derive the pilot mode from a cloudScheduleParameter value
CLOUD_PARAM_TO_PILOT_MODE: dict[str | None, str] = {
    "MANUAL": StoreyPilotMode.MANUEL,
    "SUNCAST": StoreyPilotMode.SUNCAST,
    None: StoreyPilotMode.EXPERT,
}