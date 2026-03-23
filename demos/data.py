"""Shared data and state for keyboard navigation demos."""

from dataclasses import dataclass, field


@dataclass
class DemoState:
    """State for demo applications."""
    items: list = field(default_factory=list)
    selected_indices: set = field(default_factory=set)
    queue: list = field(default_factory=list)


# Demo 1: Simple list
SIMPLE_LIST_ITEMS = [
    {"id": "1", "name": "Document A", "type": "pdf"},
    {"id": "2", "name": "Image B", "type": "png"},
    {"id": "3", "name": "Spreadsheet C", "type": "xlsx"},
    {"id": "4", "name": "Code File D", "type": "py"},
    {"id": "5", "name": "Archive E", "type": "zip"},
    {"id": "6", "name": "Text File F", "type": "txt"},
    {"id": "7", "name": "Database G", "type": "db"},
    {"id": "8", "name": "Config H", "type": "json"},
]

# Demo 2: Dual panel
DUAL_PANEL_ITEMS = [
    {"id": "src-1", "name": "Source Item 1"},
    {"id": "src-2", "name": "Source Item 2"},
    {"id": "src-3", "name": "Source Item 3"},
    {"id": "src-4", "name": "Source Item 4"},
    {"id": "src-5", "name": "Source Item 5"},
]

# Demo 3: Mode switching
MODE_SEGMENTS = [
    {"id": "seg-1", "text": "The art of war is of vital importance to the state."},
    {"id": "seg-2", "text": "It is a matter of life and death."},
    {"id": "seg-3", "text": "A road either to safety or to ruin."},
]

# Demo 4: WASD
WASD_ITEMS = [
    {"id": "w1", "name": "Move Forward"},
    {"id": "w2", "name": "Jump"},
    {"id": "w3", "name": "Attack"},
    {"id": "w4", "name": "Defend"},
    {"id": "w5", "name": "Use Item"},
]

# Demo 5: Hierarchy
CHILD_A_ITEMS = [
    {"id": "a1", "name": "Alpha Item 1"},
    {"id": "a2", "name": "Alpha Item 2"},
    {"id": "a3", "name": "Alpha Item 3"},
    {"id": "a4", "name": "Alpha Item 4"},
    {"id": "a5", "name": "Alpha Item 5"},
]

CHILD_B_ITEMS = [
    {"id": "b1", "name": "Beta Item 1"},
    {"id": "b2", "name": "Beta Item 2"},
    {"id": "b3", "name": "Beta Item 3"},
    {"id": "b4", "name": "Beta Item 4"},
]
