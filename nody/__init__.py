"""
Nody: High-performance Unrolled Linked List data type in Python, powered by a native C core.
"""

# Try importing the high-performance C-accelerated implementation
try:
    from .c_binding import CNodyList, CNodeRef
    C_BACKEND_AVAILABLE = True
except (ImportError, FileNotFoundError, OSError):
    C_BACKEND_AVAILABLE = False
    CNodyList = None
    CNodeRef = None

# Pure Python implementation (always available as reference / fallback)
from .node import Node
from .unrolled_list import NodyList as PyNodyList

# Default NodyList is the C-accelerated version if available, else pure Python
if C_BACKEND_AVAILABLE:
    NodyList = CNodyList
else:
    NodyList = PyNodyList

__all__ = [
    "NodyList",
    "CNodyList",
    "CNodeRef",
    "PyNodyList",
    "Node",
    "C_BACKEND_AVAILABLE",
]
__version__ = "0.2.0"
