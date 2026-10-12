"""Application-wide constants and configuration values."""

from typing import Final

# Application Information
APP_NAME: Final[str] = "SOS Desktop"
APP_VERSION: Final[str] = "0.1.0"
APP_ORG: Final[str] = "sos-desktop"

# Settings Keys


class SettingsKeys:
    """QSettings keys for persistent configuration."""

    CASE_ID: Final[str] = "case_id"
    UPLOAD_TARGET: Final[str] = "upload_target"
    VERBOSE_ENABLED: Final[str] = "verbose_enabled"
    COLLECT_NODES: Final[str] = "collect_nodes"
    COLLECT_CLUSTER_TYPE: Final[str] = "collect_cluster_type"
    COLLECT_TRANSPORT: Final[str] = "collect_transport"


# Upload Targets
class UploadTargets:
    """Valid upload targets for sos upload command."""

    AUTO: Final[str] = "auto"
    REDHAT: Final[str] = "redhat"
    CANONICAL: Final[str] = "canonical"
    GENERIC: Final[str] = "generic"
    LOCAL: Final[str] = "local"

    @classmethod
    def all(cls) -> list[str]:
        """Return list of all valid upload targets."""
        return [cls.AUTO, cls.REDHAT, cls.CANONICAL, cls.GENERIC, cls.LOCAL]


# Collect Options
class ClusterTypes:
    """Valid cluster types for sos collect --cluster-type."""

    TYPES: Final[list] = [
        "auto-detect", "ceph", "juju", "kubernetes", "ocp",
        "openstack", "ovirt", "pacemaker", "saltstack", "satellite",
    ]


class TransportTypes:
    """Valid transport types for sos collect --transport."""

    TYPES: Final[list] = ["auto", "ssh", "oc", "kubectl"]


# File System Paths
class Paths:
    """Default filesystem paths."""

    VAR_TMP: Final[str] = "/var/tmp"


# File Patterns
class FilePatterns:
    """Glob patterns for finding files and directories."""

    SOS_REPORT_XZ: Final[str] = "sosreport-*.tar.xz"
    SOS_REPORT_GZ: Final[str] = "sosreport-*.tar.gz"
    SOS_REPORT_DIR: Final[str] = "sosreport-*"


# UI Styling
class Styles:
    """CSS and styling constants."""

    STATUS_BAR_BG: Final[str] = "#a60000"
    STATUS_BAR_TEXT: Final[str] = "white"
    SMALL_BUTTON_SIZE: Final[str] = "12px"
