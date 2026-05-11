"""Custom WASD key mapping demo."""

from fasthtml.common import Div, H1, H3, P, Span, Ul, APIRouter

from cjm_fasthtml_daisyui.components.data_display.badge import badge, badge_colors
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
from cjm_fasthtml_keyboard_navigation.core.key_mapping import WASD_KEYS
from cjm_fasthtml_keyboard_navigation.components.system import render_keyboard_system
from cjm_fasthtml_keyboard_navigation.components.hints_modal import render_keyboard_hints_modal

from demos.data import DemoState, WASD_ITEMS
from demos.shared import render_list_item


def setup():
    """Set up the WASD demo. Returns config dict."""
    state = DemoState(items=list(WASD_ITEMS))

    zone = FocusZone(
        id="wasd-list",
        item_selector="li[data-item-id]",
        navigation=LinearVertical(),
        data_attributes=("item-id",),
        zone_focus_classes=(str(ring(2)), str(ring_dui.accent), str(inset_ring(2))),
        item_focus_classes=(str(bg_dui.accent.opacity(20)), str(ring(2)), str(ring_dui.accent)),
    )

    actions = (
        KeyAction(key="f", htmx_trigger="wasd-action-btn",
                  description="Interact", hint_group="Actions"),
    )

    manager = ZoneManager(
        zones=(zone,),
        actions=actions,
        key_mapping=WASD_KEYS,
    )

    router = APIRouter(prefix="")

    def render_wasd_list():
        return Div(
            Ul(
                *[render_list_item(item, item["id"] in state.selected_indices)
                  for item in state.items],
                id="wasd-list",
                cls=combine_classes(border(), rounded.lg, overflow.hidden),
            ),
            id="wasd-list-container",
        )

    @router
    def wasd_action(request, item_id: str = ""):
        if item_id:
            if item_id in state.selected_indices:
                state.selected_indices.discard(item_id)
            else:
                state.selected_indices.add(item_id)
        return render_wasd_list()

    def page_content():
        system = render_keyboard_system(
            manager,
            url_map={"wasd-action-btn": wasd_action.to()},
            target_map={"wasd-action-btn": "#wasd-list-container"},
            show_hints=False,
        )

        hints_modal, hints_trigger, hints_script = render_keyboard_hints_modal(manager)

        return Div(
            Div(
                Div(
                    H1("Custom Key Mappings",
                       cls=combine_classes(font_size._2xl, font_weight.bold)),
                    P("Use W/S to navigate up/down, F to interact. Press ? for the keyboard shortcuts.",
                      cls=combine_classes(text_dui.base_content, font_size.sm)),
                ),
                hints_trigger,
                cls=combine_classes(flex_display, items.start, justify.between, m.b(4)),
            ),
            Div(
                H3("Active Mapping: WASD", cls=combine_classes(font_weight.semibold, m.b(2))),
                Div(
                    Span("W = Up", cls=combine_classes(badge, badge_colors.accent, m.r(2))),
                    Span("S = Down", cls=combine_classes(badge, badge_colors.accent, m.r(2))),
                    Span("A = Left", cls=combine_classes(badge, badge_colors.accent, m.r(2))),
                    Span("D = Right", cls=combine_classes(badge, badge_colors.accent)),
                ),
                cls=combine_classes(m.b(4), p(4), bg_dui.base_200, rounded.lg),
            ),
            Div(render_wasd_list(), cls=m.t(4)),
            system.script, system.hidden_inputs, system.action_buttons,
            hints_modal,
            hints_script,
            cls=combine_classes(container, max_w._2xl, m.x.auto, p(6)),
        )

    return {
        "router": router,
        "page_content": page_content,
    }
