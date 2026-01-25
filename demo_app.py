"""Demo application for cjm-fasthtml-keyboard-navigation library.

This demo showcases the keyboard navigation framework:

1. Single Zone Navigation:
   - Simple list with up/down navigation
   - Space/Enter to select items
   - Delete to remove items

2. Dual Panel Navigation:
   - Left/Right to switch between panels
   - Independent focus tracking per panel
   - Cross-panel actions (move items between panels)

3. Mode Switching:
   - Navigation mode (default)
   - Split mode with horizontal caret movement
   - Mode indicators in UI

4. Custom Key Mappings:
   - WASD keys
   - Vim keys (hjkl)
   - Combined mappings

Run with: python demo_app.py
"""

from dataclasses import dataclass, field


def main():
    """Main entry point - initializes keyboard navigation demos."""
    from fasthtml.common import (
        fast_app, Div, H1, H2, H3, P, Span, A, Ul, Li, Script,
        APIRouter, Button, Form, Hidden
    )

    # DaisyUI and Tailwind utilities
    from cjm_fasthtml_daisyui.core.resources import get_daisyui_headers
    from cjm_fasthtml_daisyui.core.testing import create_theme_persistence_script
    from cjm_fasthtml_daisyui.components.actions.button import btn, btn_colors, btn_sizes
    from cjm_fasthtml_daisyui.components.data_display.badge import badge, badge_colors
    from cjm_fasthtml_daisyui.components.data_display.card import card, card_body
    from cjm_fasthtml_daisyui.utilities.semantic_colors import bg_dui, text_dui, border_dui, ring_dui

    from cjm_fasthtml_tailwind.utilities.spacing import p, m
    from cjm_fasthtml_tailwind.utilities.sizing import container, max_w, w, h, min_h
    from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight, text_align, font_family
    from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import (
        flex_display, flex_direction, items, justify, grid_display, grid_cols, gap, grow
    )
    from cjm_fasthtml_tailwind.utilities.borders import border, rounded, divide
    from cjm_fasthtml_tailwind.utilities.layout import overflow
    from cjm_fasthtml_tailwind.utilities.interactivity import cursor
    from cjm_fasthtml_tailwind.utilities.transitions_and_animation import transition, animate
    from cjm_fasthtml_tailwind.utilities.effects import shadow, ring, ring_color, inset_ring
    from cjm_fasthtml_tailwind.core.base import combine_classes

    # Lucide icons
    from cjm_fasthtml_lucide_icons.factory import lucide_icon

    # App core utilities
    from cjm_fasthtml_app_core.components.navbar import create_navbar
    from cjm_fasthtml_app_core.core.routing import register_routes
    from cjm_fasthtml_app_core.core.htmx import handle_htmx_request
    from cjm_fasthtml_app_core.core.layout import wrap_with_layout

    # Keyboard navigation components
    from cjm_fasthtml_keyboard_navigation.core.focus_zone import FocusZone
    from cjm_fasthtml_keyboard_navigation.core.actions import KeyAction
    from cjm_fasthtml_keyboard_navigation.core.modes import KeyboardMode
    from cjm_fasthtml_keyboard_navigation.core.manager import ZoneManager
    from cjm_fasthtml_keyboard_navigation.core.navigation import (
        LinearVertical, LinearHorizontal, Grid
    )
    from cjm_fasthtml_keyboard_navigation.core.key_mapping import (
        ARROW_KEYS, WASD_KEYS, VIM_KEYS, ARROWS_AND_WASD
    )
    from cjm_fasthtml_keyboard_navigation.components.system import (
        render_keyboard_system, KeyboardSystem
    )

    print("\n" + "=" * 70)
    print("Initializing cjm-fasthtml-keyboard-navigation Demo")
    print("=" * 70)

    # Create the FastHTML app
    app, rt = fast_app(
        pico=False,
        hdrs=[
            *get_daisyui_headers(),
            create_theme_persistence_script(),
        ],
        title="Keyboard Navigation Demo",
        htmlkw={'data-theme': 'light'},
        secret_key="demo-secret-key"
    )

    router = APIRouter(prefix="")

    print("  FastHTML app created successfully")

    # =========================================================================
    # Demo Data and State
    # =========================================================================

    @dataclass
    class DemoState:
        """State for demo applications."""
        items: list = field(default_factory=list)
        selected_indices: set = field(default_factory=set)
        queue: list = field(default_factory=list)

    # Demo 1: Simple list state
    simple_list_state = DemoState(
        items=[
            {"id": "1", "name": "Document A", "type": "pdf"},
            {"id": "2", "name": "Image B", "type": "png"},
            {"id": "3", "name": "Spreadsheet C", "type": "xlsx"},
            {"id": "4", "name": "Code File D", "type": "py"},
            {"id": "5", "name": "Archive E", "type": "zip"},
            {"id": "6", "name": "Text File F", "type": "txt"},
            {"id": "7", "name": "Database G", "type": "db"},
            {"id": "8", "name": "Config H", "type": "json"},
        ]
    )

    # Demo 2: Dual panel state
    dual_panel_state = DemoState(
        items=[
            {"id": "src-1", "name": "Source Item 1"},
            {"id": "src-2", "name": "Source Item 2"},
            {"id": "src-3", "name": "Source Item 3"},
            {"id": "src-4", "name": "Source Item 4"},
            {"id": "src-5", "name": "Source Item 5"},
        ],
        queue=[]
    )

    # Demo 3: Mode switching state
    mode_demo_state = {
        "segments": [
            {"id": "seg-1", "text": "The art of war is of vital importance to the state."},
            {"id": "seg-2", "text": "It is a matter of life and death."},
            {"id": "seg-3", "text": "A road either to safety or to ruin."},
        ],
        "active_segment": 0,
        "mode": "navigation",
        "caret_position": 0
    }

    print("\n[1/4] Creating demo configurations...")

    # =========================================================================
    # Demo 1: Simple Single-Zone List
    # =========================================================================

    simple_zone = FocusZone(
        id="simple-list",
        item_selector="li[data-item-id]",
        navigation=LinearVertical(),
        data_attributes=("item-id",),
        zone_focus_classes=(str(ring(2)), str(ring_dui.primary), str(inset_ring(2))),
        item_focus_classes=(str(bg_dui.primary.opacity(20)), str(ring(2)), str(ring_dui.primary)),
    )

    simple_actions = (
        KeyAction(
            key=" ",
            htmx_trigger="simple-toggle-btn",
            description="Toggle selection",
            hint_group="Selection"
        ),
        KeyAction(
            key="Enter",
            htmx_trigger="simple-toggle-btn",
            description="Toggle selection",
            hint_group="Selection",
            show_in_hints=False
        ),
        KeyAction(
            key="Delete",
            htmx_trigger="simple-delete-btn",
            description="Remove item",
            hint_group="Actions"
        ),
        KeyAction(
            key="a",
            modifiers=frozenset({"ctrl"}),
            htmx_trigger="simple-select-all-btn",
            description="Select all",
            hint_group="Selection"
        ),
    )

    simple_manager = ZoneManager(
        zones=(simple_zone,),
        actions=simple_actions,
    )

    # =========================================================================
    # Demo 2: Dual Panel Navigation
    # =========================================================================

    source_zone = FocusZone(
        id="source-panel",
        item_selector="li[data-item-id]",
        navigation=LinearVertical(),
        data_attributes=("item-id",),
        zone_focus_classes=(str(ring(2)), str(ring_dui.primary), str(inset_ring(2))),
        item_focus_classes=(str(bg_dui.primary.opacity(10)), str(ring(1)), str(ring_dui.primary)),
        on_focus_change="onSourceFocusChange",
    )

    queue_zone = FocusZone(
        id="queue-panel",
        item_selector="li[data-item-id]",
        navigation=LinearVertical(),
        data_attributes=("item-id",),
        zone_focus_classes=(str(ring(2)), str(ring_dui.secondary), str(inset_ring(2))),
        item_focus_classes=(str(bg_dui.secondary.opacity(10)), str(ring(1)), str(ring_dui.secondary)),
        on_focus_change="onQueueFocusChange",
    )

    dual_actions = (
        KeyAction(
            key=" ",
            htmx_trigger="dual-add-btn",
            zone_ids=("source-panel",),
            description="Add to queue",
            hint_group="Queue"
        ),
        KeyAction(
            key="Delete",
            htmx_trigger="dual-remove-btn",
            zone_ids=("queue-panel",),
            description="Remove from queue",
            hint_group="Queue"
        ),
        KeyAction(
            key="ArrowUp",
            modifiers=frozenset({"shift"}),
            htmx_trigger="dual-move-up-btn",
            zone_ids=("queue-panel",),
            description="Move up in queue",
            hint_group="Reorder"
        ),
        KeyAction(
            key="ArrowDown",
            modifiers=frozenset({"shift"}),
            htmx_trigger="dual-move-down-btn",
            zone_ids=("queue-panel",),
            description="Move down in queue",
            hint_group="Reorder"
        ),
    )

    dual_manager = ZoneManager(
        zones=(source_zone, queue_zone),
        actions=dual_actions,
        prev_zone_key="ArrowLeft",
        next_zone_key="ArrowRight",
    )

    # =========================================================================
    # Demo 3: Mode Switching
    # =========================================================================

    segment_zone = FocusZone(
        id="segment-list",
        item_selector="div[data-segment-id]",
        navigation=LinearVertical(),
        data_attributes=("segment-id",),
        zone_focus_classes=(str(ring(2)), str(ring_dui.primary)),
        item_focus_classes=(str(border_dui.primary), str(bg_dui.primary.opacity(5)), str(shadow.md)),
    )

    # Note: In a full implementation, split mode would have LinearHorizontal navigation
    # for caret movement within segments. Since caret tracking isn't implemented,
    # we use ScrollOnly to disable navigation in split mode.
    from cjm_fasthtml_keyboard_navigation.core.navigation import ScrollOnly
    split_mode = KeyboardMode(
        name="split",
        enter_key="Enter",
        exit_key="Escape",
        navigation_override=ScrollOnly(),  # Disables navigation (no caret tracking)
        on_enter="enterSplitMode",
        on_exit="exitSplitMode",
        indicator_text="Split Mode",
        zone_ids=("segment-list",),
    )

    mode_actions = (
        KeyAction(
            key="Backspace",
            htmx_trigger="mode-merge-btn",
            mode_names=("navigation",),
            description="Merge with previous",
            hint_group="Editing"
        ),
        KeyAction(
            key="Enter",
            htmx_trigger="mode-split-btn",
            mode_names=("split",),
            description="Split at caret",
            hint_group="Editing"
        ),
    )

    mode_manager = ZoneManager(
        zones=(segment_zone,),
        modes=(split_mode,),
        actions=mode_actions,
        on_mode_change="onModeChange",
    )

    # =========================================================================
    # Demo 4: Custom Key Mappings
    # =========================================================================

    wasd_zone = FocusZone(
        id="wasd-list",
        item_selector="li[data-item-id]",
        navigation=LinearVertical(),
        data_attributes=("item-id",),
        zone_focus_classes=(str(ring(2)), str(ring_dui.accent), str(inset_ring(2))),
        item_focus_classes=(str(bg_dui.accent.opacity(20)), str(ring(2)), str(ring_dui.accent)),
    )

    wasd_actions = (
        KeyAction(
            key="f",
            htmx_trigger="wasd-action-btn",
            description="Interact",
            hint_group="Actions"
        ),
    )

    wasd_manager = ZoneManager(
        zones=(wasd_zone,),
        actions=wasd_actions,
        key_mapping=WASD_KEYS,
    )

    print("  Created 4 demo configurations:")
    print("    - Simple list (single zone, arrow keys)")
    print("    - Dual panel (two zones, panel switching)")
    print("    - Mode switching (navigation/split modes)")
    print("    - Custom keys (WASD mapping)")

    # =========================================================================
    # Helper Functions
    # =========================================================================

    def render_list_item(item, is_selected=False, item_attr="data-item-id"):
        """Render a list item for the demos."""
        selected_cls = combine_classes(bg_dui.primary, text_dui.primary_content) if is_selected else ""
        check_icon = lucide_icon("check", size=4, cls=str(text_dui.success)) if is_selected else ""
        return Li(
            Div(
                Span(item.get("name", item.get("id", "Item")), cls=grow()),
                check_icon,
                cls=combine_classes(flex_display, items.center, gap(2))
            ),
            cls=combine_classes(
                p(3), border.b(), border_dui.base_300,
                cursor.pointer, transition.colors,
                selected_cls
            ),
            **{item_attr: item["id"]}
        )

    def render_segment_card(segment, index, is_active=False, mode="navigation", caret_pos=0):
        """Render a segment card for mode switching demo."""
        # Always use base border color - JavaScript handles focus styling
        # This prevents conflict between server-side active_cls and JS focus classes
        caret_cls = combine_classes(text_dui.error, font_weight.bold, animate.pulse)

        content = segment["text"]
        if is_active and mode == "split":
            # Show caret in split mode
            words = content.split(" ")
            word_spans = []
            for i, word in enumerate(words):
                if i == caret_pos:
                    word_spans.append(Span("|", cls=caret_cls))
                word_spans.append(Span(word + " "))
            if caret_pos >= len(words):
                word_spans.append(Span("|", cls=caret_cls))
            content = word_spans

        return Div(
            Div(
                Span(f"#{index + 1}", cls=combine_classes(font_family.mono, text_dui.base_content, font_size.sm)),
                cls=combine_classes(m.b(2))
            ),
            Div(
                *content if isinstance(content, list) else [content],
                cls=combine_classes(font_size.lg)
            ),
            cls=combine_classes(
                card, p(4), border(2), transition.all,
                border_dui.base_300  # Base color - JS adds focus styling
            ),
            **{"data-segment-id": segment["id"]}
        )

    # =========================================================================
    # Routes
    # =========================================================================

    @router
    def index(request):
        """Homepage with demo overview."""

        def home_content():
            return Div(
                H1("Keyboard Navigation Demo",
                   cls=combine_classes(font_size._4xl, font_weight.bold, m.b(4))),

                P("A declarative keyboard navigation framework for FastHTML applications.",
                  cls=combine_classes(font_size.lg, text_dui.base_content, m.b(8))),

                # Feature cards
                Div(
                    # Simple list card
                    Div(
                        Div(
                            H2("Simple List",
                               cls=combine_classes(font_size.xl, font_weight.semibold, m.b(2))),
                            P("Single zone with arrow key navigation and selection.",
                              cls=combine_classes(text_dui.base_content, m.b(4))),
                            Div(
                                Span(
                                    lucide_icon("arrow-down-up", size=3),
                                    Span("Navigate", cls=m.l(1)),
                                    cls=combine_classes(badge, badge_colors.primary, m.r(2), flex_display, items.center)
                                ),
                                Span(
                                    Span("Space", cls=combine_classes(font_family.mono, font_weight.bold)),
                                    Span("Select", cls=m.l(1)),
                                    cls=combine_classes(badge, badge_colors.secondary, flex_display, items.center)
                                ),
                                cls=combine_classes(flex_display, items.center, m.b(4))
                            ),
                            A(
                                Span("Try Demo", cls=m.r(1)),
                                lucide_icon("arrow-right", size=4),
                                href=demo_simple.to(),
                                cls=combine_classes(btn, btn_colors.primary, flex_display, items.center)
                            ),
                            cls=card_body
                        ),
                        cls=combine_classes(card, bg_dui.base_200)
                    ),

                    # Dual panel card
                    Div(
                        Div(
                            H2("Dual Panel",
                               cls=combine_classes(font_size.xl, font_weight.semibold, m.b(2))),
                            P("Two zones with panel switching and cross-panel actions.",
                              cls=combine_classes(text_dui.base_content, m.b(4))),
                            Div(
                                Span(
                                    lucide_icon("arrow-left-right", size=3),
                                    Span("Switch", cls=m.l(1)),
                                    cls=combine_classes(badge, badge_colors.primary, m.r(2), flex_display, items.center)
                                ),
                                Span(
                                    lucide_icon("arrow-big-up", size=3),
                                    lucide_icon("arrow-down-up", size=3),
                                    Span("Reorder", cls=m.l(1)),
                                    cls=combine_classes(badge, badge_colors.secondary, flex_display, items.center)
                                ),
                                cls=combine_classes(flex_display, items.center, m.b(4))
                            ),
                            A(
                                Span("Try Demo", cls=m.r(1)),
                                lucide_icon("arrow-right", size=4),
                                href=demo_dual.to(),
                                cls=combine_classes(btn, btn_colors.secondary, flex_display, items.center)
                            ),
                            cls=card_body
                        ),
                        cls=combine_classes(card, bg_dui.base_200)
                    ),

                    # Mode switching card
                    Div(
                        Div(
                            H2("Mode Switching",
                               cls=combine_classes(font_size.xl, font_weight.semibold, m.b(2))),
                            P("Navigation mode → Split mode with Enter/Escape.",
                              cls=combine_classes(text_dui.base_content, m.b(4))),
                            Div(
                                Span(
                                    lucide_icon("corner-down-left", size=3),
                                    lucide_icon("move-right", size=3),
                                    Span("Split", cls=m.l(1)),
                                    cls=combine_classes(badge, badge_colors.primary, m.r(2), flex_display, items.center)
                                ),
                                Span(
                                    lucide_icon("x", size=3),
                                    lucide_icon("move-right", size=3),
                                    Span("Exit", cls=m.l(1)),
                                    cls=combine_classes(badge, badge_colors.secondary, flex_display, items.center)
                                ),
                                cls=combine_classes(flex_display, items.center, m.b(4))
                            ),
                            A(
                                Span("Try Demo", cls=m.r(1)),
                                lucide_icon("arrow-right", size=4),
                                href=demo_modes.to(),
                                cls=combine_classes(btn, btn_colors.accent, flex_display, items.center)
                            ),
                            cls=card_body
                        ),
                        cls=combine_classes(card, bg_dui.base_200)
                    ),

                    # Custom keys card
                    Div(
                        Div(
                            H2("Custom Key Mappings",
                               cls=combine_classes(font_size.xl, font_weight.semibold, m.b(2))),
                            P("WASD, Vim, or custom key mappings for navigation.",
                              cls=combine_classes(text_dui.base_content, m.b(4))),
                            Div(
                                Span("WASD", cls=combine_classes(badge, badge_colors.primary, m.r(2))),
                                Span("Vim (hjkl)", cls=combine_classes(badge, badge_colors.secondary)),
                                cls=combine_classes(flex_display, items.center, m.b(4))
                            ),
                            A(
                                Span("Try Demo", cls=m.r(1)),
                                lucide_icon("arrow-right", size=4),
                                href=demo_wasd.to(),
                                cls=combine_classes(btn, btn_colors.info, flex_display, items.center)
                            ),
                            cls=card_body
                        ),
                        cls=combine_classes(card, bg_dui.base_200)
                    ),

                    cls=combine_classes(
                        grid_display, grid_cols(1),
                        grid_cols(2).md,
                        gap(6), m.b(8)
                    )
                ),

                # Features list
                Div(
                    H2("Features", cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                    Div(
                        *[Div(
                            lucide_icon("check", size=4, cls=str(text_dui.success)),
                            Span(feature, cls=m.l(2)),
                            cls=combine_classes(flex_display, items.center, m.b(2))
                        ) for feature in [
                            "Multi-zone focus management",
                            "Declarative action bindings",
                            "Mode system with transitions",
                            "HTMX + JS callback support",
                            "Custom key mappings (WASD, Vim, etc.)",
                            "State persistence support",
                            "Keyboard hints UI",
                            "Grid navigation ready",
                        ]],
                        cls=combine_classes(text_align.left, max_w.md, m.x.auto)
                    ),
                    cls=m.b(8)
                ),

                cls=combine_classes(
                    container,
                    max_w._6xl,
                    m.x.auto,
                    p(8),
                    text_align.center
                )
            )

        return handle_htmx_request(
            request,
            home_content,
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    @router
    def demo_simple(request):
        """Simple single-zone list demo."""

        def demo_content():
            system = render_keyboard_system(
                simple_manager,
                url_map={
                    "simple-toggle-btn": simple_toggle.to(),
                    "simple-delete-btn": simple_delete.to(),
                    "simple-select-all-btn": simple_select_all.to(),
                },
                target_map={
                    "simple-toggle-btn": "#simple-list-container",
                    "simple-delete-btn": "#simple-list-container",
                    "simple-select-all-btn": "#simple-list-container",
                },
            )

            return Div(
                # Header
                Div(
                    H1("Simple List Navigation",
                       cls=combine_classes(font_size._2xl, font_weight.bold)),
                    P("Use arrow keys to navigate, Space to select, Delete to remove.",
                      cls=combine_classes(text_dui.base_content, font_size.sm)),
                    cls=combine_classes(m.b(4))
                ),

                # Keyboard hints
                system.hints if system.hints else "",

                # List container
                Div(
                    render_simple_list(),
                    cls=combine_classes(m.t(4))
                ),

                # Scripts and hidden elements
                system.script,
                system.hidden_inputs,
                system.action_buttons,

                cls=combine_classes(container, max_w._2xl, m.x.auto, p(6))
            )

        return handle_htmx_request(
            request,
            demo_content,
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    def render_simple_list():
        """Render the simple list component."""
        return Div(
            Ul(
                *[render_list_item(item, item["id"] in simple_list_state.selected_indices)
                  for item in simple_list_state.items],
                id="simple-list",
                cls=combine_classes(border(), rounded.lg, overflow.hidden, divide.y())
            ),
            id="simple-list-container"
        )

    @router
    def simple_toggle(request, item_id: str = ""):
        """Toggle item selection."""
        if item_id:
            if item_id in simple_list_state.selected_indices:
                simple_list_state.selected_indices.discard(item_id)
            else:
                simple_list_state.selected_indices.add(item_id)
        return render_simple_list()

    @router
    def simple_delete(request, item_id: str = ""):
        """Delete an item."""
        if item_id:
            simple_list_state.items = [i for i in simple_list_state.items if i["id"] != item_id]
            simple_list_state.selected_indices.discard(item_id)
        return render_simple_list()

    @router
    def simple_select_all(request):
        """Select all items."""
        if len(simple_list_state.selected_indices) == len(simple_list_state.items):
            simple_list_state.selected_indices.clear()
        else:
            simple_list_state.selected_indices = {i["id"] for i in simple_list_state.items}
        return render_simple_list()

    @router
    def demo_dual(request):
        """Dual panel navigation demo."""

        def demo_content():
            system = render_keyboard_system(
                dual_manager,
                url_map={
                    "dual-add-btn": dual_add.to(),
                    "dual-remove-btn": dual_remove.to(),
                    "dual-move-up-btn": dual_move_up.to(),
                    "dual-move-down-btn": dual_move_down.to(),
                },
                target_map={
                    "dual-add-btn": "#dual-panels",
                    "dual-remove-btn": "#dual-panels",
                    "dual-move-up-btn": "#dual-panels",
                    "dual-move-down-btn": "#dual-panels",
                },
            )

            return Div(
                # Header
                Div(
                    H1("Dual Panel Navigation",
                       cls=combine_classes(font_size._2xl, font_weight.bold)),
                    P("Use ←/→ to switch panels, Space to add, Delete to remove, Shift+↑/↓ to reorder.",
                      cls=combine_classes(text_dui.base_content, font_size.sm)),
                    cls=combine_classes(m.b(4))
                ),

                # Keyboard hints
                system.hints if system.hints else "",

                # Panels
                Div(
                    render_dual_panels(),
                    cls=combine_classes(m.t(4))
                ),

                # Scripts and hidden elements
                system.script,
                system.hidden_inputs,
                system.action_buttons,

                # JS callbacks for focus change
                Script("""
                    function onSourceFocusChange(item, index, zoneId) {
                        console.log('Source focus:', item?.dataset?.itemId, 'at index', index);
                    }
                    function onQueueFocusChange(item, index, zoneId) {
                        console.log('Queue focus:', item?.dataset?.itemId, 'at index', index);
                    }
                """),

                cls=combine_classes(container, max_w._4xl, m.x.auto, p(6))
            )

        return handle_htmx_request(
            request,
            demo_content,
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    def render_dual_panels():
        """Render the dual panel layout."""
        return Div(
            Div(
                # Source panel
                Div(
                    H3("Source Items", cls=combine_classes(font_weight.semibold, m.b(2))),
                    Ul(
                        *[render_list_item(item) for item in dual_panel_state.items],
                        id="source-panel",
                        cls=combine_classes(border(), rounded.lg, overflow.hidden, divide.y(), min_h(64))
                    ),
                    cls=combine_classes(grow(), p(2))
                ),

                # Queue panel
                Div(
                    H3("Queue", cls=combine_classes(font_weight.semibold, m.b(2))),
                    Ul(
                        *[render_list_item({"id": item["id"], "name": item["name"]})
                          for item in dual_panel_state.queue] if dual_panel_state.queue else [
                            Li(
                                P("Queue is empty", cls=combine_classes(text_dui.base_content, font_size.sm)),
                                cls=combine_classes(p(4), text_align.center)
                            )
                        ],
                        id="queue-panel",
                        cls=combine_classes(border(), rounded.lg, overflow.hidden, divide.y(), min_h(64))
                    ),
                    cls=combine_classes(grow(), p(2))
                ),

                cls=combine_classes(grid_display, grid_cols(2), gap(4))
            ),
            id="dual-panels"
        )

    @router
    def dual_add(request, item_id: str = ""):
        """Add item to queue."""
        if item_id:
            item = next((i for i in dual_panel_state.items if i["id"] == item_id), None)
            if item and item not in dual_panel_state.queue:
                dual_panel_state.queue.append(item)
        return render_dual_panels()

    @router
    def dual_remove(request, item_id: str = ""):
        """Remove item from queue."""
        if item_id:
            dual_panel_state.queue = [i for i in dual_panel_state.queue if i["id"] != item_id]
        return render_dual_panels()

    @router
    def dual_move_up(request, item_id: str = ""):
        """Move item up in queue."""
        if item_id:
            for i, item in enumerate(dual_panel_state.queue):
                if item["id"] == item_id and i > 0:
                    dual_panel_state.queue[i], dual_panel_state.queue[i-1] = \
                        dual_panel_state.queue[i-1], dual_panel_state.queue[i]
                    break
        return render_dual_panels()

    @router
    def dual_move_down(request, item_id: str = ""):
        """Move item down in queue."""
        if item_id:
            for i, item in enumerate(dual_panel_state.queue):
                if item["id"] == item_id and i < len(dual_panel_state.queue) - 1:
                    dual_panel_state.queue[i], dual_panel_state.queue[i+1] = \
                        dual_panel_state.queue[i+1], dual_panel_state.queue[i]
                    break
        return render_dual_panels()

    @router
    def demo_modes(request):
        """Mode switching demo."""

        def demo_content():
            system = render_keyboard_system(
                mode_manager,
                url_map={
                    "mode-merge-btn": mode_merge.to(),
                    "mode-split-btn": mode_split.to(),
                },
                target_map={
                    "mode-merge-btn": "#segment-container",
                    "mode-split-btn": "#segment-container",
                },
            )

            return Div(
                # Header
                Div(
                    H1("Mode Switching",
                       cls=combine_classes(font_size._2xl, font_weight.bold)),
                    P("Press Enter to enter Split mode, Escape to exit. Use ↑/↓ to navigate segments. (Caret movement not implemented in demo)",
                      cls=combine_classes(text_dui.base_content, font_size.sm)),
                    cls=combine_classes(m.b(4))
                ),

                # Mode indicator
                Div(
                    Span("Current Mode: ", cls=font_weight.semibold),
                    Span(
                        mode_demo_state["mode"].title(),
                        id="mode-indicator",
                        cls=combine_classes(
                            badge,
                            badge_colors.primary if mode_demo_state["mode"] == "navigation" else badge_colors.warning
                        )
                    ),
                    cls=combine_classes(m.b(4))
                ),

                # Keyboard hints
                system.hints if system.hints else "",

                # Segments
                Div(
                    render_segments(),
                    cls=combine_classes(m.t(4))
                ),

                # Scripts and hidden elements
                system.script,
                system.hidden_inputs,
                system.action_buttons,

                # JS callbacks for mode changes
                Script("""
                    function enterSplitMode(modeName, zoneId) {
                        console.log('Entered split mode');
                        document.getElementById('mode-indicator').textContent = 'Split';
                        document.getElementById('mode-indicator').className = 'badge badge-warning';
                    }
                    function exitSplitMode(modeName, zoneId) {
                        console.log('Exited split mode');
                        document.getElementById('mode-indicator').textContent = 'Navigation';
                        document.getElementById('mode-indicator').className = 'badge badge-primary';
                    }
                    function onModeChange(newMode, oldMode) {
                        console.log('Mode changed from', oldMode, 'to', newMode);
                    }
                """),

                cls=combine_classes(container, max_w._3xl, m.x.auto, p(6))
            )

        return handle_htmx_request(
            request,
            demo_content,
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    def render_segments():
        """Render segment cards."""
        return Div(
            Div(
                *[render_segment_card(
                    seg, i,
                    is_active=(i == mode_demo_state["active_segment"]),
                    mode=mode_demo_state["mode"],
                    caret_pos=mode_demo_state["caret_position"]
                ) for i, seg in enumerate(mode_demo_state["segments"])],
                id="segment-list",
                cls=combine_classes(flex_display, flex_direction.col, gap(4))
            ),
            id="segment-container"
        )

    @router
    def mode_merge(request, segment_id: str = ""):
        """Merge segment with previous."""
        segments = mode_demo_state["segments"]
        for i, seg in enumerate(segments):
            if seg["id"] == segment_id and i > 0:
                # Merge text
                segments[i-1]["text"] = segments[i-1]["text"] + " " + seg["text"]
                segments.pop(i)
                mode_demo_state["active_segment"] = max(0, i - 1)
                break
        return render_segments()

    @router
    def mode_split(request, segment_id: str = ""):
        """Split segment at caret position (simplified demo)."""
        # In a real implementation, this would use the caret position
        # For demo, we just show that the action is triggered
        return render_segments()

    @router
    def demo_wasd(request):
        """Custom key mapping demo."""

        def demo_content():
            system = render_keyboard_system(
                wasd_manager,
                url_map={
                    "wasd-action-btn": wasd_action.to(),
                },
                target_map={
                    "wasd-action-btn": "#wasd-list-container",
                },
            )

            return Div(
                # Header
                Div(
                    H1("Custom Key Mappings",
                       cls=combine_classes(font_size._2xl, font_weight.bold)),
                    P("Use W/S to navigate up/down, F to interact.",
                      cls=combine_classes(text_dui.base_content, font_size.sm)),
                    cls=combine_classes(m.b(4))
                ),

                # Key mapping info
                Div(
                    H3("Active Mapping: WASD", cls=combine_classes(font_weight.semibold, m.b(2))),
                    Div(
                        Span("W = Up", cls=combine_classes(badge, badge_colors.accent, m.r(2))),
                        Span("S = Down", cls=combine_classes(badge, badge_colors.accent, m.r(2))),
                        Span("A = Left", cls=combine_classes(badge, badge_colors.accent, m.r(2))),
                        Span("D = Right", cls=combine_classes(badge, badge_colors.accent)),
                    ),
                    cls=combine_classes(m.b(4), p(4), bg_dui.base_200, rounded.lg)
                ),

                # Keyboard hints
                system.hints if system.hints else "",

                # List container
                Div(
                    render_wasd_list(),
                    cls=combine_classes(m.t(4))
                ),

                # Scripts and hidden elements
                system.script,
                system.hidden_inputs,
                system.action_buttons,

                cls=combine_classes(container, max_w._2xl, m.x.auto, p(6))
            )

        return handle_htmx_request(
            request,
            demo_content,
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    def render_wasd_list():
        """Render the WASD demo list."""
        items = [
            {"id": "w1", "name": "Move Forward"},
            {"id": "w2", "name": "Jump"},
            {"id": "w3", "name": "Attack"},
            {"id": "w4", "name": "Defend"},
            {"id": "w5", "name": "Use Item"},
        ]
        return Div(
            Ul(
                *[render_list_item(item) for item in items],
                id="wasd-list",
                cls=combine_classes(border(), rounded.lg, overflow.hidden, divide.y())
            ),
            id="wasd-list-container"
        )

    @router
    def wasd_action(request, item_id: str = ""):
        """Handle WASD action."""
        # Just return the list unchanged for demo
        return render_wasd_list()

    # =========================================================================
    # Navigation
    # =========================================================================

    # Create navbar
    navbar = create_navbar(
        title="Keyboard Nav Demo",
        nav_items=[
            ("Home", index),
            ("Simple", demo_simple),
            ("Dual Panel", demo_dual),
            ("Modes", demo_modes),
            ("WASD", demo_wasd),
        ],
        home_route=index,
        theme_selector=True
    )

    # Register all routes
    register_routes(app, router)

    # Debug: Print registered routes
    print("\n" + "=" * 70)
    print("Registered Routes:")
    print("=" * 70)
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  {route.path}")

    print("\n" + "=" * 70)
    print("Demo App Ready!")
    print("=" * 70)
    print("\n Library Components:")
    print("  - FocusZone - Focusable container configuration")
    print("  - KeyAction - Declarative keyboard action bindings")
    print("  - KeyboardMode - Mode switching support")
    print("  - ZoneManager - Multi-zone coordination")
    print("  - render_keyboard_system - Complete UI generation")
    print("=" * 70 + "\n")

    return app


if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading

    # Call main to initialize everything and get the app
    app = main()

    def open_browser(url):
        print(f"Opening browser at {url}")
        webbrowser.open(url)

    port = 5033
    host = "0.0.0.0"
    display_host = 'localhost' if host in ['0.0.0.0', '127.0.0.1'] else host

    print(f"Server: http://{display_host}:{port}")
    print("\nAvailable routes:")
    print(f"  http://{display_host}:{port}/              - Homepage with demo overview")
    print(f"  http://{display_host}:{port}/demo_simple   - Simple list navigation")
    print(f"  http://{display_host}:{port}/demo_dual     - Dual panel navigation")
    print(f"  http://{display_host}:{port}/demo_modes    - Mode switching demo")
    print(f"  http://{display_host}:{port}/demo_wasd     - Custom key mappings")
    print("\n" + "=" * 70 + "\n")

    # Open browser after a short delay
    timer = threading.Timer(1.5, lambda: open_browser(f"http://localhost:{port}"))
    timer.daemon = True
    timer.start()

    # Start server
    uvicorn.run(app, host=host, port=port)
