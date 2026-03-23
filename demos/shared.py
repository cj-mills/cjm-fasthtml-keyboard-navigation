"""Shared rendering utilities for keyboard navigation demos."""

from fasthtml.common import Div, Li, Span

from cjm_fasthtml_daisyui.utilities.semantic_colors import bg_dui, text_dui, border_dui
from cjm_fasthtml_tailwind.utilities.spacing import p
from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight, font_family
from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import flex_display, items, gap, grow
from cjm_fasthtml_tailwind.utilities.borders import border
from cjm_fasthtml_tailwind.utilities.interactivity import cursor
from cjm_fasthtml_tailwind.utilities.transitions_and_animation import transition, animate
from cjm_fasthtml_tailwind.utilities.effects import shadow
from cjm_fasthtml_tailwind.core.base import combine_classes

from cjm_fasthtml_daisyui.components.data_display.card import card

from cjm_fasthtml_lucide_icons.factory import lucide_icon


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
    caret_cls = combine_classes(text_dui.error, font_weight.bold, animate.pulse)

    content = segment["text"]
    if is_active and mode == "split":
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
        ),
        Div(
            *content if isinstance(content, list) else [content],
            cls=combine_classes(font_size.lg)
        ),
        cls=combine_classes(
            card, p(4), border(2), transition.all,
            border_dui.base_300,
            combine_classes(border_dui.primary, bg_dui.primary.opacity(5), shadow.md) if is_active else "",
        ),
        **{"data-segment-id": segment["id"]}
    )
