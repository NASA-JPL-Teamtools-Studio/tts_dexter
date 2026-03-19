from abc import ABC, abstractmethod
from copy import deepcopy
from enum import Enum, auto

from tts_utilities.logger import create_logger
from tts_dexter.core.dispo import Disposition, get_dispo_joiner, DISPO_SEVERITY

logger = create_logger(__name__)

class DISPO_CHOICE(Enum):
    """
    Enumeration defining strategies for selecting which disposition to display 
    when multiple dispositions are generated for a single data item.
    """
    FIRST = auto()
    """Select only the first disposition generated."""

    LAST = auto()
    """Select only the last disposition generated."""

    ALL = auto()
    """Include all generated dispositions in the output."""

    SEVERITY = auto()
    """Select the single disposition with the highest severity level."""