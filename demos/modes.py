"""Mode switching demo — navigation mode and split mode.

This demo reproduces the Escape key bug where pressing Escape exits the JS
mode state but doesn't trigger the HTMX request to re-render the card.

Key pattern (matching cjm-transcript-segmentation):
- split_mode has exit_key="" (empty — no built-in exit key)
- KeyAction(key="Escape", htmx_trigger=..., mode_exit=True) handles exit
- The exit_split route re-renders segments from the server
- A Cancel button provides the working workaround for comparison
"""

from fasthtml.common import Div, H1, P, Span, Button, Script
from cjm_fasthtml_app_core.core.routing import APIRouter

from cjm_fasthtml_daisyui.components.actions.button import btn, btn_sizes, btn_styles
from cjm_fasthtml_daisyui.components.data_display.badge import badge, badge_colors
from cjm_fasthtml_daisyui.utilities.semantic_colors import (
    text_dui, ring_dui, bg_dui, border_dui
)
from cjm_fasthtml_tailwind.utilities.spacing import p, m
from cjm_fasthtml_tailwind.utilities.sizing import container, max_w
from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight, font_family
from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import (
    flex_display, flex_direction, flex_wrap, items, gap, justify
)
from cjm_fasthtml_tailwind.utilities.borders import border
from cjm_fasthtml_tailwind.utilities.transitions_and_animation import transition, animate
from cjm_fasthtml_tailwind.utilities.effects import ring, shadow
from cjm_fasthtml_tailwind.core.base import combine_classes

from cjm_fasthtml_daisyui.components.data_display.card import card

from cjm_fasthtml_keyboard_navigation.core.focus_zone import FocusZone
from cjm_fasthtml_keyboard_navigation.core.actions import KeyAction
from cjm_fasthtml_keyboard_navigation.core.modes import KeyboardMode
from cjm_fasthtml_keyboard_navigation.core.manager import ZoneManager
from cjm_fasthtml_keyboard_navigation.core.navigation import LinearVertical, ScrollOnly
from cjm_fasthtml_keyboard_navigation.components.system import render_keyboard_system
from cjm_fasthtml_keyboard_navigation.components.hints_modal import render_keyboard_hints_modal

from demos.data import MODE_SEGMENTS

# Hidden input ID for tracking focused segment
SEGMENT_ID_INPUT = "segment-list-segment-id"


def setup():
    """Set up the mode switching demo. Returns config dict."""
    state = {
        "segments": [dict(s) for s in MODE_SEGMENTS],
        "active_segment": 0,
        "mode": "navigation",
        "caret_position": 0,
    }

    zone = FocusZone(
        id="segment-list",
        item_selector="div[data-segment-id]",
        navigation=LinearVertical(),
        data_attributes=("segment-id",),
        zone_focus_classes=(str(ring(2)), str(ring_dui.primary)),
        item_focus_classes=(str(border_dui.primary), str(bg_dui.primary.opacity(5)), str(shadow.md)),
    )

    # exit_key="" — mode does NOT handle Escape itself.
    # exit_on_zone_change=False — prevents HTMX settle from exiting mode.
    # This matches the cjm-transcript-segmentation pattern.
    split_mode = KeyboardMode(
        name="split",
        enter_key="",
        exit_key="",
        exit_on_zone_change=False,
        navigation_override=ScrollOnly(),
        on_enter="enterSplitMode",
        on_exit="exitSplitMode",
        indicator_text="Split Mode",
        zone_ids=("segment-list",),
    )

    seg_zone_ids = ("segment-list",)

    actions = (
        # Enter split mode (Enter or Space when NOT in split mode)
        KeyAction(
            key="Enter",
            htmx_trigger="mode-enter-split-btn",
            zone_ids=seg_zone_ids,
            mode_enter="split",
            not_modes=("split",),
            description="Enter split mode",
            hint_group="Segmentation",
        ),
        KeyAction(
            key=" ",
            htmx_trigger="mode-enter-split-btn",
            zone_ids=seg_zone_ids,
            mode_enter="split",
            not_modes=("split",),
            description="Enter split mode",
            hint_group="Segmentation",
            show_in_hints=False,
        ),

        # Execute split (Enter when IN split mode)
        KeyAction(
            key="Enter",
            htmx_trigger="mode-split-btn",
            zone_ids=seg_zone_ids,
            mode_exit=True,
            mode_names=("split",),
            description="Split at caret",
            hint_group="Split Mode",
        ),

        # Exit split mode (Escape when IN split mode) — THE KEY ACTION
        # This is the pattern that triggers the bug:
        # The early Escape handler in js_keyboard_handler() intercepts this
        # and calls exitMode() before this KeyAction's htmx_trigger fires.
        KeyAction(
            key="Escape",
            htmx_trigger="mode-exit-split-btn",
            zone_ids=seg_zone_ids,
            mode_exit=True,
            mode_names=("split",),
            description="Exit split mode",
            hint_group="Split Mode",
        ),

        # Merge with previous (Backspace when NOT in split mode)
        KeyAction(
            key="Backspace",
            htmx_trigger="mode-merge-btn",
            mode_names=("navigation",),
            description="Merge with previous",
            hint_group="Editing",
        ),
    )

    manager = ZoneManager(
        zones=(zone,),
        modes=(split_mode,),
        actions=actions,
        on_mode_change="onModeChange",
    )

    router = APIRouter(prefix="")

    def _render_segment_card(segment, index, is_split_mode=False, exit_split_url=""):
        """Render a segment card with visual distinction between modes."""
        caret_cls = combine_classes(text_dui.error, font_weight.bold, animate.pulse)

        content = segment["text"]
        is_active = index == state["active_segment"]

        if is_active and is_split_mode:
            # Split mode: show word tokens with caret and Cancel button
            words = content.split(" ")
            caret_pos = state["caret_position"]
            word_spans = []
            for i, word in enumerate(words):
                if i == caret_pos:
                    word_spans.append(Span("|", cls=caret_cls))
                word_spans.append(Span(
                    word + " ",
                    cls=combine_classes(
                        p.x(1), p.y('0.5'),
                        bg_dui.warning.opacity(20),
                        border(1), border_dui.warning,
                    ),
                ))
            if caret_pos >= len(words):
                word_spans.append(Span("|", cls=caret_cls))

            content_div = Div(
                *word_spans,
                cls=combine_classes(flex_display, flex_wrap.wrap, gap(1), font_size.lg),
            )

            # Cancel button — this works because it directly posts via HTMX
            cancel_btn = Button(
                "Cancel",
                cls=combine_classes(btn, btn_styles.ghost, btn_sizes.sm),
                hx_post=exit_split_url,
                hx_target="#segment-container",
                hx_swap="outerHTML",
                onclick="if(window.kbNav)window.kbNav.exitMode()",
            )

            return Div(
                Div(
                    Span(f"#{index + 1}", cls=combine_classes(
                        font_family.mono, text_dui.base_content, font_size.sm)),
                    Span("SPLIT MODE", cls=combine_classes(
                        badge, badge_colors.warning, font_size.xs, m.l(2))),
                    cancel_btn,
                    cls=combine_classes(flex_display, items.center, gap(2), m.b(2)),
                ),
                content_div,
                cls=combine_classes(
                    card, p(4), border(2), transition.all,
                    border_dui.warning, bg_dui.warning.opacity(5),
                ),
                **{"data-segment-id": segment["id"]},
            )
        else:
            # Navigation mode: plain text
            return Div(
                Div(
                    Span(f"#{index + 1}", cls=combine_classes(
                        font_family.mono, text_dui.base_content, font_size.sm)),
                ),
                Div(content, cls=font_size.lg),
                cls=combine_classes(
                    card, p(4), border(2), transition.all,
                    border_dui.base_300,
                ),
                **{"data-segment-id": segment["id"]},
            )

    def render_segments(is_split_mode=False, exit_split_url=""):
        """Render all segment cards."""
        return Div(
            Div(
                *[_render_segment_card(seg, i, is_split_mode=is_split_mode,
                                       exit_split_url=exit_split_url)
                  for i, seg in enumerate(state["segments"])],
                id="segment-list",
                cls=combine_classes(flex_display, flex_direction.col, gap(4)),
            ),
            id="segment-container",
        )

    # Store exit_split URL for use in render functions (set after route creation)
    _exit_split_url = [""]

    @router
    def mode_enter_split(request, segment_id: str = ""):
        """Enter split mode — re-render with split mode visuals."""
        # Update active segment from keyboard focus
        if segment_id:
            for i, seg in enumerate(state["segments"]):
                if seg["id"] == segment_id:
                    state["active_segment"] = i
                    break
        state["mode"] = "split"
        state["caret_position"] = 0
        return render_segments(is_split_mode=True, exit_split_url=_exit_split_url[0])

    @router
    def mode_exit_split(request):
        """Exit split mode — re-render without split mode visuals.

        This is the route that Escape should trigger via htmx_trigger.
        If this route fires, the segments re-render in navigation mode.
        If only exitMode() fires (the bug), segments stay in split mode visually.
        """
        state["mode"] = "navigation"
        return render_segments(is_split_mode=False)

    @router
    def mode_merge(request, segment_id: str = ""):
        segments = state["segments"]
        for i, seg in enumerate(segments):
            if seg["id"] == segment_id and i > 0:
                segments[i-1]["text"] = segments[i-1]["text"] + " " + seg["text"]
                segments.pop(i)
                state["active_segment"] = max(0, i - 1)
                break
        return render_segments(is_split_mode=False)

    @router
    def mode_split(request, segment_id: str = ""):
        """Execute split at caret (simplified — just exits split mode)."""
        state["mode"] = "navigation"
        return render_segments(is_split_mode=False)

    # Set the exit_split URL now that routes exist
    _exit_split_url[0] = mode_exit_split.to()

    # Include map: pass focused segment-id hidden input with HTMX requests
    _include_selector = f"#{SEGMENT_ID_INPUT}"

    def page_content():
        system = render_keyboard_system(
            manager,
            url_map={
                "mode-enter-split-btn": mode_enter_split.to(),
                "mode-exit-split-btn": mode_exit_split.to(),
                "mode-merge-btn": mode_merge.to(),
                "mode-split-btn": mode_split.to(),
            },
            target_map={
                "mode-enter-split-btn": "#segment-container",
                "mode-exit-split-btn": "#segment-container",
                "mode-merge-btn": "#segment-container",
                "mode-split-btn": "#segment-container",
            },
            swap_map={
                "mode-enter-split-btn": "outerHTML",
                "mode-exit-split-btn": "outerHTML",
                "mode-merge-btn": "outerHTML",
                "mode-split-btn": "outerHTML",
            },
            include_map={
                "mode-enter-split-btn": _include_selector,
                "mode-exit-split-btn": _include_selector,
                "mode-merge-btn": _include_selector,
                "mode-split-btn": _include_selector,
            },
            show_hints=False,
        )

        hints_modal, hints_trigger, hints_script = render_keyboard_hints_modal(manager)

        return Div(
            Div(
                Div(
                    H1("Mode Switching",
                       cls=combine_classes(font_size._2xl, font_weight.bold)),
                    P("Press Enter/Space to enter Split mode. Escape should exit and re-render from server. Press ? for the keyboard shortcuts.",
                      cls=combine_classes(text_dui.base_content, font_size.sm)),
                ),
                hints_trigger,
                cls=combine_classes(flex_display, items.start, justify.between, m.b(4)),
            ),
            # Mode indicator
            Div(
                Div(
                    Span("JS Mode: ", cls=font_weight.semibold),
                    Span(
                        state["mode"].title(),
                        id="mode-indicator",
                        cls=combine_classes(
                            badge,
                            badge_colors.primary if state["mode"] == "navigation" else badge_colors.warning,
                        ),
                    ),
                    cls=combine_classes(flex_display, items.center, gap(2)),
                ),
                Div(
                    Span("Server Render: ", cls=font_weight.semibold),
                    Span(
                        "Check card visuals — split mode has yellow borders + token spans",
                        cls=combine_classes(font_size.xs, text_dui.base_content),
                    ),
                ),
                cls=combine_classes(m.b(4), p(3), bg_dui.base_200, font_size.sm),
            ),
            # Bug explanation
            Div(
                P("Bug test: Enter split mode (Enter), then press Escape.",
                  cls=font_weight.semibold),
                P("Expected: JS mode indicator resets AND cards re-render (yellow → gray borders).",
                  cls=font_size.sm),
                P("Bug: JS mode resets but cards stay in split mode (yellow borders persist).",
                  cls=combine_classes(font_size.sm, text_dui.error)),
                P("Workaround: Click the Cancel button (uses direct HTMX post).",
                  cls=combine_classes(font_size.sm, text_dui.success)),
                cls=combine_classes(m.b(4), p(3), bg_dui.warning.opacity(10), font_size.sm),
            ),
            Div(render_segments(is_split_mode=False), cls=m.t(4)),
            system.script, system.hidden_inputs, system.action_buttons,
            hints_modal,
            hints_script,
            Script("""
                function enterSplitMode(modeName, zoneId) {
                    console.log('[MODE] Entered split mode (JS callback)');
                    document.getElementById('mode-indicator').textContent = 'Split';
                    document.getElementById('mode-indicator').className = 'badge badge-warning';
                }
                function exitSplitMode(modeName, zoneId) {
                    console.log('[MODE] Exited split mode (JS callback)');
                    document.getElementById('mode-indicator').textContent = 'Navigation';
                    document.getElementById('mode-indicator').className = 'badge badge-primary';
                }
                function onModeChange(newMode, oldMode) {
                    console.log('[MODE] Mode changed from', oldMode, 'to', newMode);
                }
            """),
            cls=combine_classes(container, max_w._3xl, m.x.auto, p(6)),
        )

    return {
        "router": router,
        "page_content": page_content,
    }
