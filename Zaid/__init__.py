"""Compatibility alias for older imports; the active package is ICC."""
import ICC as _icc
from ICC import *

# Keep legacy imports such as ``from Zaid.helper import ...`` working.
__path__ = _icc.__path__
