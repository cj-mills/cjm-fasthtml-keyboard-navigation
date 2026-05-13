"""Hierarchical keyboard systems demo — parent with two child systems."""

from fasthtml.common import Div, H1, H3, P, Span, Ul, Script, Button
from cjm_fasthtml_app_core.core.routing import APIRouter

from cjm_fasthtml_daisyui.components.actions.button import btn, btn_styles, btn_sizes
from cjm_fasthtml_daisyui.components.data_display.badge import badge, badge_colors
from cjm_fasthtml_daisyui.utilities.semantic_colors import (
    text_dui, ring_dui, bg_dui, border_dui
)
from cjm_fasthtml_tailwind.utilities.spacing import p, m
from cjm_fasthtml_tailwind.utilities.sizing import container, max_w
from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight, font_family
from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import grid_display, grid_cols, gap, flex_display, items, justify
from cjm_fasthtml_tailwind.utilities.borders import border, rounded
from cjm_fasthtml_tailwind.utilities.layout import overflow
from cjm_fasthtml_tailwind.utilities.transitions_and_animation import transition, duration
from cjm_fasthtml_tailwind.utilities.effects import ring, inset_ring
from cjm_fasthtml_tailwind.core.base import combine_classes

from cjm_fasthtml_keyboard_navigation.core.focus_zone import FocusZone
from cjm_fasthtml_keyboard_navigation.core.actions import KeyAction
from cjm_fasthtml_keyboard_navigation.core.manager import ZoneManager
from cjm_fasthtml_keyboard_navigation.core.navigation import LinearVertical, ScrollOnly
from cjm_fasthtml_keyboard_navigation.components.system import render_keyboard_system
from cjm_fasthtml_keyboard_navigation.components.hints_modal import render_keyboard_hints_modal

from demos.data import DemoState, CHILD_A_ITEMS, CHILD_B_ITEMS
from demos.shared import render_list_item


def setup():
    """Set up the hierarchy demo. Returns config dict."""
    child_a_state = DemoState(items=list(CHILD_A_ITEMS))
    child_b_state = DemoState(items=list(CHILD_B_ITEMS))

    # --- Child A ---
    child_a_zone = FocusZone(
        id="child-a-list",
        item_selector="li[data-item-id]",
        navigation=LinearVertical(),
        data_attributes=("item-id",),
        zone_focus_classes=(str(ring(2)), str(ring_dui.primary), str(inset_ring(2))),
        item_focus_classes=(str(bg_dui.primary.opacity(20)), str(ring(1)), str(ring_dui.primary)),
    )
    child_a_actions = (
        KeyAction(key=" ", htmx_trigger="child-a-toggle-btn",
                  description="Toggle selection", hint_group="Selection"),
        KeyAction(key="Enter", htmx_trigger="child-a-toggle-btn",
                  description="Toggle selection", hint_group="Selection", show_in_hints=False),
    )
    child_a_manager = ZoneManager(
        zones=(child_a_zone,), actions=child_a_actions, system_id="child-a",
        label="Alpha List (Child A)",
    )

    # --- Child B ---
    child_b_zone = FocusZone(
        id="child-b-list",
        item_selector="li[data-item-id]",
        navigation=LinearVertical(),
        data_attributes=("item-id",),
        zone_focus_classes=(str(ring(2)), str(ring_dui.secondary), str(inset_ring(2))),
        item_focus_classes=(str(bg_dui.secondary.opacity(20)), str(ring(1)), str(ring_dui.secondary)),
    )
    child_b_actions = (
        KeyAction(key=" ", htmx_trigger="child-b-toggle-btn",
                  description="Toggle selection", hint_group="Selection"),
        KeyAction(key="Enter", htmx_trigger="child-b-toggle-btn",
                  description="Toggle selection", hint_group="Selection", show_in_hints=False),
    )
    child_b_manager = ZoneManager(
        zones=(child_b_zone,), actions=child_b_actions, system_id="child-b",
        label="Beta List (Child B)",
    )

    # --- Parent ---
    # Each ghost zone declares which child it activates via activate_child_id.
    # The library-baked Enter/Space dispatch (manager.activate_keys = ("Enter", " ")
    # by default) reads these fields and calls coord.setActiveChild on press —
    # no consumer KeyAction needed. The "Activate panel" hint row is surfaced
    # in the modal via derive_hierarchy_hints. Status-text updates run via the
    # children's onActivate callbacks (see hierarchy_js below).
    ghost_zone_a = FocusZone(
        id="ghost-a", item_selector=None, navigation=ScrollOnly(),
        zone_focus_classes=(str(ring(2)), str(ring_dui.primary)),
        activate_child_id="child-a",
    )
    ghost_zone_b = FocusZone(
        id="ghost-b", item_selector=None, navigation=ScrollOnly(),
        zone_focus_classes=(str(ring(2)), str(ring_dui.secondary)),
        activate_child_id="child-b",
    )
    parent_manager = ZoneManager(
        zones=(ghost_zone_a, ghost_zone_b),
        system_id="hierarchy-parent",
        prev_zone_key="ArrowLeft",
        next_zone_key="ArrowRight",
        label="Parent (Areas)",
    )

    router = APIRouter(prefix="")

    def render_child_a_list():
        return Div(
            Ul(
                *[render_list_item(item, item["id"] in child_a_state.selected_indices)
                  for item in child_a_state.items],
                id="child-a-list",
                cls=combine_classes(border(), rounded.lg, overflow.hidden),
            ),
            id="child-a-container",
        )

    def render_child_b_list():
        return Div(
            Ul(
                *[render_list_item(item, item["id"] in child_b_state.selected_indices)
                  for item in child_b_state.items],
                id="child-b-list",
                cls=combine_classes(border(), rounded.lg, overflow.hidden),
            ),
            id="child-b-container",
        )

    @router
    def child_a_toggle(request, item_id: str = ""):
        if item_id:
            if item_id in child_a_state.selected_indices:
                child_a_state.selected_indices.discard(item_id)
            else:
                child_a_state.selected_indices.add(item_id)
        return render_child_a_list()

    @router
    def child_b_toggle(request, item_id: str = ""):
        if item_id:
            if item_id in child_b_state.selected_indices:
                child_b_state.selected_indices.discard(item_id)
            else:
                child_b_state.selected_indices.add(item_id)
        return render_child_b_list()

    hierarchy_js = Script("""
    (function() {
        const coord = window.kbCoordinator;

        coord.setParent('child-a', 'hierarchy-parent');
        coord.setParent('child-b', 'hierarchy-parent');

        // Child-activation is now library-baked via FocusZone.activate_child_id
        // on each ghost zone. The Enter/Space dispatcher calls coord.setActiveChild
        // directly — no consumer-defined window callback needed. The status text
        // and zone-ring side-effects flow through the child systems' onActivate /
        // onDeactivate hooks below.
        const childLabels = { 'child-a': 'Child A (Alpha list)', 'child-b': 'Child B (Beta list)' };

        function updateStatus(text) {
            const el = document.getElementById('hierarchy-status');
            if (el) el.textContent = text;
        }

        // --- Pause/Resume toggle ---
        window.togglePauseParent = function() {
            const btn = document.getElementById('pause-toggle-btn');
            const panels = document.getElementById('hierarchy-panels');
            if (coord.isPaused('hierarchy-parent')) {
                coord.resume('hierarchy-parent');
                btn.textContent = 'Pause Keyboard';
                btn.classList.remove('btn-warning');
                btn.classList.add('btn-outline');
                if (panels) panels.classList.remove('opacity-50');
                updateStatus('Resumed — keyboard active');
            } else {
                coord.pause('hierarchy-parent');
                btn.textContent = 'Resume Keyboard';
                btn.classList.remove('btn-outline');
                btn.classList.add('btn-warning');
                if (panels) panels.classList.add('opacity-50');
                updateStatus('PAUSED — keyboard events blocked');
            }
        };

        const childASys = coord._systems['child-a'];
        const childBSys = coord._systems['child-b'];

        if (childASys) {
            childASys.onActivate = function() {
                const el = document.getElementById('ghost-a');
                if (el) { el.classList.add('ring-2', 'ring-primary'); }
                updateStatus(childLabels['child-a'] + ' — press Escape to return');
            };
            childASys.onDeactivate = function() {
                const el = document.getElementById('ghost-a');
                if (el) { el.classList.remove('ring-2', 'ring-primary'); }
                updateStatus('Parent (navigating between areas)');
            };
        }

        if (childBSys) {
            childBSys.onActivate = function() {
                const el = document.getElementById('ghost-b');
                if (el) { el.classList.add('ring-2', 'ring-secondary'); }
                updateStatus(childLabels['child-b'] + ' — press Escape to return');
            };
            childBSys.onDeactivate = function() {
                const el = document.getElementById('ghost-b');
                if (el) { el.classList.remove('ring-2', 'ring-secondary'); }
                updateStatus('Parent (navigating between areas)');
            };
        }

        updateStatus('Parent (navigating between areas) — use ←/→ then Enter');
    })();
    """)

    def page_content():
        parent_system = render_keyboard_system(
            parent_manager, url_map={}, target_map={}, show_hints=False,
        )
        child_a_system = render_keyboard_system(
            child_a_manager,
            url_map={"child-a-toggle-btn": child_a_toggle.to()},
            target_map={"child-a-toggle-btn": "#child-a-container"},
            show_hints=False,
        )
        child_b_system = render_keyboard_system(
            child_b_manager,
            url_map={"child-b-toggle-btn": child_b_toggle.to()},
            target_map={"child-b-toggle-btn": "#child-b-container"},
            show_hints=False,
        )

        # Hints modal: hierarchical rendering via child_managers.
        # Parent at top (area-level navigation), then each child as a labeled
        # section showing its own keys. The bespoke Instructions panel below
        # still explains the parent/child coordination semantics (when child
        # is active vs. parent is active) — content the modal can't capture.
        hints_modal, hints_trigger, hints_script = render_keyboard_hints_modal(
            parent_manager,
            child_managers=(child_a_manager, child_b_manager),
        )

        return Div(
            Div(
                Div(
                    H1("Hierarchical Systems",
                       cls=combine_classes(font_size._2xl, font_weight.bold)),
                    P("Parent with two child systems. Escape deactivates child, Enter activates. Press ? for parent-level shortcuts.",
                      cls=combine_classes(text_dui.base_content, font_size.sm)),
                ),
                hints_trigger,
                cls=combine_classes(flex_display, items.start, justify.between, m.b(4)),
            ),
            # Instructions
            Div(
                Div(Span("←/→", cls=combine_classes(badge, badge_colors.accent, m.r(2))),
                    Span("Navigate between areas (at parent level)"), cls=m.b(1)),
                Div(Span("Enter/Space", cls=combine_classes(badge, badge_colors.primary, m.r(2))),
                    Span("Activate highlighted area"), cls=m.b(1)),
                Div(Span("Escape", cls=combine_classes(badge, badge_colors.warning, m.r(2))),
                    Span("Deactivate child, return to parent"), cls=m.b(1)),
                Div(Span("↑/↓", cls=combine_classes(badge, badge_colors.info, m.r(2))),
                    Span("Navigate items (when child is active)"), cls=m.b(1)),
                Div(Span("Space", cls=combine_classes(badge, badge_colors.success, m.r(2))),
                    Span("Toggle selection (when child is active)")),
                cls=combine_classes(m.b(4), p(4), bg_dui.base_200, rounded.lg, font_size.sm),
            ),
            # Status + Pause toggle
            Div(
                Div(
                    Span("Active: ", cls=font_weight.semibold),
                    Span("Parent (navigating between areas)", id="hierarchy-status"),
                    cls=combine_classes(font_size.sm, font_family.mono),
                ),
                Button(
                    "Pause Keyboard",
                    id="pause-toggle-btn",
                    onclick="togglePauseParent()",
                    cls=combine_classes(btn, btn_styles.outline, btn_sizes.sm),
                ),
                cls=combine_classes(
                    p(3), m.b(4), rounded.lg, bg_dui.base_200,
                    flex_display, items.center, justify.between,
                ),
            ),
            # Two child panels
            Div(
                Div(
                    H3("Alpha List", cls=combine_classes(font_weight.semibold, m.b(2), text_dui.primary)),
                    render_child_a_list(),
                    id="ghost-a",
                    cls=combine_classes(p(4), rounded.lg, border(), border_dui.base_300, transition.all),
                ),
                Div(
                    H3("Beta List", cls=combine_classes(font_weight.semibold, m.b(2), text_dui.secondary)),
                    render_child_b_list(),
                    id="ghost-b",
                    cls=combine_classes(p(4), rounded.lg, border(), border_dui.base_300, transition.all),
                ),
                id="hierarchy-panels",
                cls=combine_classes(grid_display, grid_cols(2), gap(4), m.b(4), transition.opacity, duration(300)),
            ),
            # All keyboard systems
            parent_system.script, parent_system.hidden_inputs, parent_system.action_buttons,
            child_a_system.script, child_a_system.hidden_inputs, child_a_system.action_buttons,
            child_b_system.script, child_b_system.hidden_inputs, child_b_system.action_buttons,
            hierarchy_js,
            hints_modal,
            hints_script,
            cls=combine_classes(container, max_w._4xl, m.x.auto, p(6)),
        )

    return {
        "router": router,
        "page_content": page_content,
    }
