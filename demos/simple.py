"""Simple single-zone list navigation demo."""

from fasthtml.common import Div, H1, P, Ul, APIRouter

from cjm_fasthtml_daisyui.utilities.semantic_colors import text_dui, ring_dui, bg_dui
from cjm_fasthtml_tailwind.utilities.spacing import p, m
from cjm_fasthtml_tailwind.utilities.sizing import container, max_w
from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight
from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import flex_display, items, justify
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

from demos.data import DemoState, SIMPLE_LIST_ITEMS
from demos.shared import render_list_item


def setup():
    """Set up the simple list demo. Returns config dict."""
    state = DemoState(items=list(SIMPLE_LIST_ITEMS))

    zone = FocusZone(
        id="simple-list",
        item_selector="li[data-item-id]",
        navigation=LinearVertical(),
        data_attributes=("item-id",),
        zone_focus_classes=(str(ring(2)), str(ring_dui.primary), str(inset_ring(2))),
        item_focus_classes=(str(bg_dui.primary.opacity(20)), str(ring(2)), str(ring_dui.primary)),
    )

    actions = (
        KeyAction(key=" ", htmx_trigger="simple-toggle-btn",
                  description="Toggle selection", hint_group="Selection"),
        KeyAction(key="Enter", htmx_trigger="simple-toggle-btn",
                  description="Toggle selection", hint_group="Selection", show_in_hints=False),
        KeyAction(key="Delete", htmx_trigger="simple-delete-btn",
                  description="Remove item", hint_group="Actions"),
        KeyAction(key="a", modifiers=frozenset({"ctrl"}), htmx_trigger="simple-select-all-btn",
                  description="Select all", hint_group="Selection"),
    )

    manager = ZoneManager(zones=(zone,), actions=actions)

    router = APIRouter(prefix="")

    def render_simple_list():
        return Div(
            Ul(
                *[render_list_item(item, item["id"] in state.selected_indices)
                  for item in state.items],
                id="simple-list",
                cls=combine_classes(border(), rounded.lg, overflow.hidden),
            ),
            id="simple-list-container",
        )

    @router
    def simple_toggle(request, item_id: str = ""):
        if item_id:
            if item_id in state.selected_indices:
                state.selected_indices.discard(item_id)
            else:
                state.selected_indices.add(item_id)
        return render_simple_list()

    @router
    def simple_delete(request, item_id: str = ""):
        if item_id:
            state.items = [i for i in state.items if i["id"] != item_id]
            state.selected_indices.discard(item_id)
        return render_simple_list()

    @router
    def simple_select_all(request):
        if len(state.selected_indices) == len(state.items):
            state.selected_indices.clear()
        else:
            state.selected_indices = {i["id"] for i in state.items}
        return render_simple_list()

    def page_content():
        system = render_keyboard_system(
            manager,
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
            show_hints=False,
        )

        hints_modal, hints_trigger, hints_script = render_keyboard_hints_modal(manager)

        return Div(
            Div(
                Div(
                    H1("Simple List Navigation",
                       cls=combine_classes(font_size._2xl, font_weight.bold)),
                    P("Use arrow keys to navigate, Space to select, Delete to remove. Press ? for the keyboard shortcuts.",
                      cls=combine_classes(text_dui.base_content, font_size.sm)),
                ),
                hints_trigger,
                cls=combine_classes(flex_display, items.start, justify.between, m.b(4)),
            ),
            Div(render_simple_list(), cls=m.t(4)),
            system.script, system.hidden_inputs, system.action_buttons,
            hints_modal,
            hints_script,
            cls=combine_classes(container, max_w._2xl, m.x.auto, p(6)),
        )

    return {
        "router": router,
        "page_content": page_content,
    }
