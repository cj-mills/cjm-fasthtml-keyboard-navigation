"""Dual card-stack demo: shared factory across zones + G4 hint-modal patterns.

Demonstrates the patterns introduced for G4 (Keyboard-hints hierarchical-zone
rendering):

- **Shared factory pattern**: a single factory `_nav_factory(zone_id)` is invoked
  TWICE (once per zone) producing identical `hint_group` + `description` strings
  per zone. Without G4's zone-aware grouping in the hints modal, those rows
  would collapse into a single "Navigation" header with duplicates — exactly
  the segment-align symptom this work was designed to fix.
- **FocusZone.label**: zones get human-readable labels ("Source Panel" /
  "Target Panel") that appear in hints-modal section headers
  ("Source Panel — Navigation", etc.) instead of raw zone IDs.
- **Mode-conditional chips**: an "Edit Mode" with mode-restricted actions
  whose rows display a small chip indicating the mode they fire in.
- **`KeyAction.documentation_only`**: appears in the hints modal but fires no
  handler — used for documenting client-side-only keyboard interactions
  (e.g., search shortcuts handled by a separate JS event listener).
- **Optimal-space modal layout**: the hints modal grows its `max_w` and
  auto-distributes content across CSS columns at desktop widths.
"""

from fasthtml.common import Div, H1, H3, P, Li, Ul, Script, APIRouter, Span

from cjm_fasthtml_daisyui.utilities.semantic_colors import text_dui, ring_dui, bg_dui
from cjm_fasthtml_tailwind.utilities.spacing import p, m
from cjm_fasthtml_tailwind.utilities.sizing import container, max_w, min_h
from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight, text_align
from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import (
    flex_display, items, gap, grow, grid_display, grid_cols, justify
)
from cjm_fasthtml_tailwind.utilities.borders import border, rounded
from cjm_fasthtml_tailwind.utilities.layout import overflow
from cjm_fasthtml_tailwind.utilities.effects import ring, inset_ring
from cjm_fasthtml_tailwind.core.base import combine_classes

from cjm_fasthtml_keyboard_navigation.core.focus_zone import FocusZone
from cjm_fasthtml_keyboard_navigation.core.actions import KeyAction
from cjm_fasthtml_keyboard_navigation.core.manager import ZoneManager
from cjm_fasthtml_keyboard_navigation.core.modes import KeyboardMode
from cjm_fasthtml_keyboard_navigation.core.navigation import LinearVertical
from cjm_fasthtml_keyboard_navigation.components.system import render_keyboard_system
from cjm_fasthtml_keyboard_navigation.components.hints_modal import render_keyboard_hints_modal

from demos.data import DemoState, DUAL_PANEL_ITEMS
from demos.shared import render_list_item


def setup():
    """Set up the dual card-stack demo. Returns config dict."""
    state = DemoState(items=list(DUAL_PANEL_ITEMS), queue=list(DUAL_PANEL_ITEMS))

    # FocusZones with `label` set — these labels are used by the hints modal
    # as the prefix in section headers ("Source Panel — Navigation", etc.).
    # Without `label`, the modal would fall back to the raw zone `id`.
    source_zone = FocusZone(
        id="dcs-source",
        label="Source Panel",
        item_selector="li[data-item-id]",
        navigation=LinearVertical(),
        zone_focus_classes=(str(ring(2)), str(ring_dui.primary), str(inset_ring(2))),
        item_focus_classes=(str(bg_dui.primary.opacity(10)), str(ring(1)), str(ring_dui.primary)),
        on_focus_change="onDCSSourceFocus",
    )

    target_zone = FocusZone(
        id="dcs-target",
        label="Target Panel",
        item_selector="li[data-item-id]",
        navigation=LinearVertical(),
        zone_focus_classes=(str(ring(2)), str(ring_dui.secondary), str(inset_ring(2))),
        item_focus_classes=(str(bg_dui.secondary.opacity(10)), str(ring(1)), str(ring_dui.secondary)),
        on_focus_change="onDCSTargetFocus",
    )

    # Edit mode — demonstrates mode chips on mode-restricted actions in the
    # hints modal. Actions with `mode_names=("edit",)` get a "[edit]" chip;
    # actions with `not_modes=("edit",)` get a "[default]" chip.
    edit_mode = KeyboardMode(
        name="edit",
        indicator_text="Edit Mode",
    )

    def _nav_factory(zone_id: str) -> tuple:
        """Shared factory: emits identical hint_group + description per zone.

        This is the segment-align pattern. With zone-aware grouping, each zone's
        emissions land under their own scoped section in the hints modal
        instead of collapsing into a single header with duplicate rows.
        """
        return (
            KeyAction(key="ArrowUp", htmx_trigger=f"{zone_id}-prev", zone_ids=(zone_id,),
                      not_modes=("edit",),
                      description="Previous item", hint_group="Navigation"),
            KeyAction(key="ArrowDown", htmx_trigger=f"{zone_id}-next", zone_ids=(zone_id,),
                      not_modes=("edit",),
                      description="Next item", hint_group="Navigation"),
            KeyAction(key="Home", js_callback=f"{zone_id}_first", zone_ids=(zone_id,),
                      not_modes=("edit",),
                      description="First item", hint_group="Navigation"),
            KeyAction(key="End", js_callback=f"{zone_id}_last", zone_ids=(zone_id,),
                      not_modes=("edit",),
                      description="Last item", hint_group="Navigation"),
            KeyAction(key="[", js_callback=f"{zone_id}_narrower", zone_ids=(zone_id,),
                      description="Narrower", hint_group="View"),
            KeyAction(key="]", js_callback=f"{zone_id}_wider", zone_ids=(zone_id,),
                      description="Wider", hint_group="View"),
        )

    actions = (
        # SHARED FACTORY invoked twice — exactly the pattern that produced
        # duplicate rows in the pre-G4 hints modal. With G4, each invocation's
        # output lands in its own zone-scoped section.
        *_nav_factory("dcs-source"),
        *_nav_factory("dcs-target"),

        # Mode-restricted Edit actions — render with mode chip in the hints modal
        KeyAction(key="e", htmx_trigger="dcs-enter-edit", zone_ids=("dcs-source",),
                  mode_enter="edit", not_modes=("edit",),
                  description="Enter edit mode", hint_group="Editing"),
        KeyAction(key="Enter", htmx_trigger="dcs-commit-edit", zone_ids=("dcs-source",),
                  mode_names=("edit",), mode_exit=True,
                  description="Commit edit", hint_group="Editing"),
        KeyAction(key="Escape", mode_exit=True, zone_ids=("dcs-source",),
                  mode_names=("edit",),
                  description="Cancel edit", hint_group="Editing"),

        # Documentation-only KeyActions — appear in hints but fire NO handler.
        # Use case: keys handled by a separate client-side JS event listener
        # where the keyboard-navigation library shouldn't suppress the event.
        # Here we document hypothetical search-related keys that a real app
        # might bind via its own JS, while still surfacing them in the modal.
        KeyAction.documentation_only(
            key="/",
            description="Focus search",
            hint_group="Help",
        ),
        KeyAction.documentation_only(
            key="?",
            description="Toggle this help",
            hint_group="Help",
        ),
    )

    manager = ZoneManager(
        zones=(source_zone, target_zone),
        actions=actions,
        modes=(edit_mode,),
        prev_zone_key="ArrowLeft",
        next_zone_key="ArrowRight",
    )

    router = APIRouter(prefix="")

    def render_panels():
        return Div(
            Div(
                H3("Source Panel", cls=combine_classes(font_weight.semibold, m.b(2))),
                Ul(
                    *[render_list_item(item) for item in state.items],
                    id="dcs-source",
                    cls=combine_classes(border(), rounded.lg, overflow.hidden, min_h(64)),
                ),
                cls=combine_classes(grow(), p(2)),
            ),
            Div(
                H3("Target Panel", cls=combine_classes(font_weight.semibold, m.b(2))),
                Ul(
                    *[render_list_item(item) for item in state.queue],
                    id="dcs-target",
                    cls=combine_classes(border(), rounded.lg, overflow.hidden, min_h(64)),
                ),
                cls=combine_classes(grow(), p(2)),
            ),
            cls=combine_classes(grid_display, grid_cols(2), gap(4)),
            id="dcs-panels",
        )

    # Minimal handlers — the demo focuses on the hints modal layout, not
    # on full app behavior. Each handler is a no-op that re-renders the panels.
    @router
    def dcs_source_prev(request): return render_panels()
    @router
    def dcs_source_next(request): return render_panels()
    @router
    def dcs_target_prev(request): return render_panels()
    @router
    def dcs_target_next(request): return render_panels()
    @router
    def dcs_enter_edit(request): return render_panels()
    @router
    def dcs_commit_edit(request): return render_panels()

    def page_content():
        system = render_keyboard_system(
            manager,
            url_map={
                "dcs-source-prev":    dcs_source_prev.to(),
                "dcs-source-next":    dcs_source_next.to(),
                "dcs-target-prev":    dcs_target_prev.to(),
                "dcs-target-next":    dcs_target_next.to(),
                "dcs-enter-edit":     dcs_enter_edit.to(),
                "dcs-commit-edit":    dcs_commit_edit.to(),
            },
            target_map={
                "dcs-source-prev":    "#dcs-panels",
                "dcs-source-next":    "#dcs-panels",
                "dcs-target-prev":    "#dcs-panels",
                "dcs-target-next":    "#dcs-panels",
                "dcs-enter-edit":     "#dcs-panels",
                "dcs-commit-edit":    "#dcs-panels",
            },
            show_hints=False,
        )

        # Keyboard hints modal — exercises all G4 patterns
        hints_modal, hints_trigger, hints_script = render_keyboard_hints_modal(manager)

        return Div(
            # Header with explanation + trigger button
            Div(
                Div(
                    H1("Dual Card-Stack — G4 Hints Patterns",
                       cls=combine_classes(font_size._2xl, font_weight.bold)),
                    P(
                        "Two zones, shared keyboard factory. Press ? to open the hints modal. "
                        "Use ←/→ to switch panels, ↑/↓ to navigate. "
                        "Press E to enter Edit Mode (mode chip will appear on mode-restricted hints).",
                        cls=combine_classes(text_dui.base_content, font_size.sm),
                    ),
                ),
                hints_trigger,
                cls=combine_classes(flex_display, items.start, justify.between, m.b(4)),
            ),
            Div(render_panels(), cls=m.t(4)),

            # Inline note explaining what to look for in the hints modal
            Div(
                P("What to verify in the hints modal:",
                  cls=combine_classes(font_weight.semibold, font_size.sm, m.t(6), m.b(2))),
                Ul(
                    Li("Each zone has its OWN \"Navigation\" / \"View\" section header (\"Source Panel — Navigation\", \"Target Panel — Navigation\")."),
                    Li("\"Previous item\" / \"Next item\" appear once per zone — not duplicated under one header."),
                    Li("Mode-restricted actions show a chip: [default] on Navigation actions, [edit] on Edit Mode actions."),
                    Li("Documentation-only keys (/ and ?) appear in hints but DO nothing when pressed."),
                    Li("At wider viewports the modal grows and content auto-distributes into 2–3 columns."),
                    cls=combine_classes(font_size.sm, text_dui.base_content),
                ),
                cls=combine_classes(p(4), bg_dui.base_200, rounded.lg, m.t(4)),
            ),

            system.script, system.hidden_inputs, system.action_buttons,
            hints_modal,
            hints_script,
            Script("""
                function onDCSSourceFocus(item, index, zoneId) {
                    console.log('Source focus:', item?.dataset?.itemId, 'at index', index);
                }
                function onDCSTargetFocus(item, index, zoneId) {
                    console.log('Target focus:', item?.dataset?.itemId, 'at index', index);
                }
            """),
            cls=combine_classes(container, max_w._4xl, m.x.auto, p(6)),
        )

    return {
        "router": router,
        "page_content": page_content,
    }
