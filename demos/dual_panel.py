"""Dual panel navigation demo with zone switching."""

from fasthtml.common import Div, H1, H3, P, Li, Ul, Script, Span
from cjm_fasthtml_app_core.core.routing import APIRouter

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
from cjm_fasthtml_keyboard_navigation.core.navigation import LinearVertical
from cjm_fasthtml_keyboard_navigation.components.system import render_keyboard_system
from cjm_fasthtml_keyboard_navigation.components.hints_modal import render_keyboard_hints_modal

from demos.data import DemoState, DUAL_PANEL_ITEMS
from demos.shared import render_list_item


def setup():
    """Set up the dual panel demo. Returns config dict."""
    state = DemoState(items=list(DUAL_PANEL_ITEMS), queue=[])

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

    actions = (
        KeyAction(key=" ", htmx_trigger="dual-add-btn", zone_ids=("source-panel",),
                  description="Add to queue", hint_group="Queue"),
        KeyAction(key="Delete", htmx_trigger="dual-remove-btn", zone_ids=("queue-panel",),
                  description="Remove from queue", hint_group="Queue"),
        KeyAction(key="ArrowUp", modifiers=frozenset({"shift"}), htmx_trigger="dual-move-up-btn",
                  zone_ids=("queue-panel",), description="Move up in queue", hint_group="Reorder"),
        KeyAction(key="ArrowDown", modifiers=frozenset({"shift"}), htmx_trigger="dual-move-down-btn",
                  zone_ids=("queue-panel",), description="Move down in queue", hint_group="Reorder"),
    )

    manager = ZoneManager(
        zones=(source_zone, queue_zone),
        actions=actions,
        prev_zone_key="ArrowLeft",
        next_zone_key="ArrowRight",
    )

    router = APIRouter(prefix="")

    def render_dual_panels():
        return Div(
            Div(
                Div(
                    H3("Source Items", cls=combine_classes(font_weight.semibold, m.b(2))),
                    Ul(
                        *[render_list_item(item) for item in state.items],
                        id="source-panel",
                        cls=combine_classes(border(), rounded.lg, overflow.hidden, min_h(64)),
                    ),
                    cls=combine_classes(grow(), p(2)),
                ),
                Div(
                    H3("Queue", cls=combine_classes(font_weight.semibold, m.b(2))),
                    Ul(
                        *([render_list_item({"id": item["id"], "name": item["name"]})
                           for item in state.queue] if state.queue else [
                            Li(P("Queue is empty",
                                 cls=combine_classes(text_dui.base_content, font_size.sm)),
                               cls=combine_classes(p(4), text_align.center))
                        ]),
                        id="queue-panel",
                        cls=combine_classes(border(), rounded.lg, overflow.hidden, min_h(64)),
                    ),
                    cls=combine_classes(grow(), p(2)),
                ),
                cls=combine_classes(grid_display, grid_cols(2), gap(4)),
            ),
            id="dual-panels",
        )

    @router
    def dual_add(request, item_id: str = ""):
        if item_id:
            item = next((i for i in state.items if i["id"] == item_id), None)
            if item and item not in state.queue:
                state.queue.append(item)
        return render_dual_panels()

    @router
    def dual_remove(request, item_id: str = ""):
        if item_id:
            state.queue = [i for i in state.queue if i["id"] != item_id]
        return render_dual_panels()

    @router
    def dual_move_up(request, item_id: str = ""):
        if item_id:
            for i, item in enumerate(state.queue):
                if item["id"] == item_id and i > 0:
                    state.queue[i], state.queue[i-1] = state.queue[i-1], state.queue[i]
                    break
        return render_dual_panels()

    @router
    def dual_move_down(request, item_id: str = ""):
        if item_id:
            for i, item in enumerate(state.queue):
                if item["id"] == item_id and i < len(state.queue) - 1:
                    state.queue[i], state.queue[i+1] = state.queue[i+1], state.queue[i]
                    break
        return render_dual_panels()

    def page_content():
        system = render_keyboard_system(
            manager,
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
            show_hints=False,
        )

        # Keyboard hints modal
        hints_modal, hints_trigger, hints_script = render_keyboard_hints_modal(manager)

        return Div(
            # Header with trigger button
            Div(
                Div(
                    H1("Dual Panel Navigation",
                       cls=combine_classes(font_size._2xl, font_weight.bold)),
                    P("Use ←/→ to switch panels, Space to add, Delete to remove, Shift+↑/↓ to reorder.",
                      cls=combine_classes(text_dui.base_content, font_size.sm)),
                ),
                hints_trigger,
                cls=combine_classes(flex_display, items.start, justify.between, m.b(4)),
            ),
            Div(render_dual_panels(), cls=m.t(4)),
            system.script, system.hidden_inputs, system.action_buttons,
            hints_modal,
            hints_script,
            Script("""
                function onSourceFocusChange(item, index, zoneId) {
                    console.log('Source focus:', item?.dataset?.itemId, 'at index', index);
                }
                function onQueueFocusChange(item, index, zoneId) {
                    console.log('Queue focus:', item?.dataset?.itemId, 'at index', index);
                }
            """),
            cls=combine_classes(container, max_w._4xl, m.x.auto, p(6)),
        )

    return {
        "router": router,
        "page_content": page_content,
    }
