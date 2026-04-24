"""Demo application for cjm-fasthtml-keyboard-navigation library.

Showcases the keyboard navigation framework with multiple demo configurations.
Each demo is a self-contained module in the demos/ package.

1. Simple List — Single zone with arrow key navigation and selection
2. Dual Panel — Two zones with panel switching and cross-panel actions
3. Mode Switching — Navigation mode and split mode with Enter/Escape
4. Custom Key Mappings — WASD keys for navigation
5. Hierarchical Systems — Parent-child keyboard coordination

Run with: python demo_app.py
"""


def main():
    """Initialize keyboard navigation demos and start the server."""
    from fasthtml.common import fast_app, Div, H1, H2, P, Span, A, APIRouter

    from cjm_fasthtml_daisyui.core.resources import get_daisyui_headers
    from cjm_fasthtml_daisyui.core.testing import create_theme_persistence_script
    from cjm_fasthtml_daisyui.components.actions.button import btn, btn_colors
    from cjm_fasthtml_daisyui.components.data_display.badge import badge, badge_colors
    from cjm_fasthtml_daisyui.components.data_display.card import card, card_body
    from cjm_fasthtml_daisyui.utilities.semantic_colors import bg_dui, text_dui

    from cjm_fasthtml_tailwind.utilities.spacing import p, m
    from cjm_fasthtml_tailwind.utilities.sizing import container, max_w
    from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight, text_align, font_family
    from cjm_fasthtml_tailwind.utilities.flexbox_and_grid import (
        flex_display, items, gap, grid_display, grid_cols
    )
    from cjm_fasthtml_tailwind.core.base import combine_classes

    from cjm_fasthtml_lucide_icons.factory import lucide_icon

    from cjm_fasthtml_design_system.icons import icons

    from cjm_fasthtml_app_core.components.navbar import create_navbar
    from cjm_fasthtml_app_core.core.routing import register_routes
    from cjm_fasthtml_app_core.core.htmx import handle_htmx_request
    from cjm_fasthtml_app_core.core.layout import wrap_with_layout

    import demos.simple as simple_demo
    import demos.dual_panel as dual_panel_demo
    import demos.modes as modes_demo
    import demos.wasd as wasd_demo
    import demos.hierarchy as hierarchy_demo

    print("\n" + "=" * 70)
    print("Initializing cjm-fasthtml-keyboard-navigation Demo")
    print("=" * 70)

    APP_ID = "kbnav"

    app, rt = fast_app(
        pico=False,
        hdrs=[*get_daisyui_headers(), create_theme_persistence_script()],
        title="Keyboard Navigation Demo",
        htmlkw={'data-theme': 'light'},
        session_cookie=f'session_{APP_ID}_',
        secret_key=f'{APP_ID}-demo-secret',
    )

    router = APIRouter(prefix="")

    # -------------------------------------------------------------------------
    # Set up demos
    # -------------------------------------------------------------------------
    simple = simple_demo.setup()
    dual_panel = dual_panel_demo.setup()
    modes = modes_demo.setup()
    wasd = wasd_demo.setup()
    hierarchy = hierarchy_demo.setup()

    print("  Set up 5 demo configurations:")
    print("    - Simple list (single zone, arrow keys)")
    print("    - Dual panel (two zones, panel switching)")
    print("    - Mode switching (navigation/split modes)")
    print("    - Custom keys (WASD mapping)")
    print("    - Hierarchy (parent-child coordination)")

    # -------------------------------------------------------------------------
    # Homepage
    # -------------------------------------------------------------------------
    def _demo_card(title, description, badges, href, btn_cls):
        """Render a demo card for the homepage."""
        return Div(
            Div(
                H2(title, cls=combine_classes(font_size.xl, font_weight.semibold, m.b(2))),
                P(description, cls=combine_classes(text_dui.base_content, m.b(4))),
                Div(
                    *[Span(
                        *(parts if isinstance(parts := badge_content, list) else [badge_content]),
                        cls=combine_classes(badge, color, m.r(2), flex_display, items.center),
                    ) for badge_content, color in badges],
                    cls=combine_classes(flex_display, items.center, m.b(4)),
                ),
                A(
                    Span("Try Demo", cls=m.r(1)),
                    lucide_icon("arrow-right", size=icons.text_button),
                    href=href,
                    cls=combine_classes(btn_cls, flex_display, items.center),
                ),
                cls=card_body,
            ),
            cls=combine_classes(card, bg_dui.base_200),
        )

    @router
    def index(request):
        """Homepage with demo overview."""

        def home_content():
            return Div(
                H1("Keyboard Navigation Demo",
                   cls=combine_classes(font_size._4xl, font_weight.bold, m.b(4))),
                P("A declarative keyboard navigation framework for FastHTML applications.",
                  cls=combine_classes(font_size.lg, text_dui.base_content, m.b(8))),

                # Demo cards
                Div(
                    _demo_card(
                        "Simple List",
                        "Single zone with arrow key navigation and selection.",
                        badges=[
                            ([lucide_icon("arrow-down-up", size=icons.dense_inline), Span("Navigate", cls=m.l(1))],
                             badge_colors.primary),
                            ([Span("Space", cls=combine_classes(font_family.mono, font_weight.bold)),
                              Span("Select", cls=m.l(1))],
                             badge_colors.secondary),
                        ],
                        href=demo_simple.to(),
                        btn_cls=combine_classes(btn, btn_colors.primary),
                    ),
                    _demo_card(
                        "Dual Panel",
                        "Two zones with panel switching and cross-panel actions.",
                        badges=[
                            ([lucide_icon("arrow-left-right", size=icons.dense_inline), Span("Switch", cls=m.l(1))],
                             badge_colors.primary),
                            ([lucide_icon("arrow-big-up", size=icons.dense_inline), lucide_icon("arrow-down-up", size=icons.dense_inline),
                              Span("Reorder", cls=m.l(1))],
                             badge_colors.secondary),
                        ],
                        href=demo_dual.to(),
                        btn_cls=combine_classes(btn, btn_colors.secondary),
                    ),
                    _demo_card(
                        "Mode Switching",
                        "Navigation mode → Split mode with Enter/Escape.",
                        badges=[
                            ([lucide_icon("corner-down-left", size=icons.dense_inline), lucide_icon("move-right", size=icons.dense_inline),
                              Span("Split", cls=m.l(1))],
                             badge_colors.primary),
                            ([lucide_icon("x", size=icons.dense_inline), lucide_icon("move-right", size=icons.dense_inline),
                              Span("Exit", cls=m.l(1))],
                             badge_colors.secondary),
                        ],
                        href=demo_modes.to(),
                        btn_cls=combine_classes(btn, btn_colors.accent),
                    ),
                    _demo_card(
                        "Custom Key Mappings",
                        "WASD, Vim, or custom key mappings for navigation.",
                        badges=[
                            ("WASD", badge_colors.primary),
                            ("Vim (hjkl)", badge_colors.secondary),
                        ],
                        href=demo_wasd.to(),
                        btn_cls=combine_classes(btn, btn_colors.info),
                    ),
                    _demo_card(
                        "Hierarchical Systems",
                        "Parent-child keyboard coordination with Escape/Enter activation.",
                        badges=[
                            ([lucide_icon("layers", size=icons.dense_inline), Span("Hierarchy", cls=m.l(1))],
                             badge_colors.primary),
                            ([Span("Esc", cls=combine_classes(font_family.mono, font_weight.bold)),
                              Span("Deactivate", cls=m.l(1))],
                             badge_colors.warning),
                        ],
                        href=demo_hierarchy.to(),
                        btn_cls=combine_classes(btn, btn_colors.warning),
                    ),
                    cls=combine_classes(grid_display, grid_cols(1), grid_cols(2).md, gap(6), m.b(8)),
                ),

                # Features list
                Div(
                    H2("Features", cls=combine_classes(font_size._2xl, font_weight.bold, m.b(4))),
                    Div(
                        *[Div(
                            lucide_icon("check", size=icons.status_inline, cls=str(text_dui.success)),
                            Span(feature, cls=m.l(2)),
                            cls=combine_classes(flex_display, items.center, m.b(2)),
                        ) for feature in [
                            "Multi-zone focus management",
                            "Declarative action bindings",
                            "Mode system with transitions",
                            "HTMX + JS callback support",
                            "Custom key mappings (WASD, Vim, etc.)",
                            "Hierarchical keyboard systems with coordinator",
                            "State persistence support",
                            "Keyboard hints UI",
                            "Grid navigation ready",
                        ]],
                        cls=combine_classes(text_align.left, max_w.md, m.x.auto),
                    ),
                    cls=m.b(8),
                ),

                cls=combine_classes(container, max_w._6xl, m.x.auto, p(8), text_align.center),
            )

        return handle_htmx_request(
            request, home_content,
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar),
        )

    # -------------------------------------------------------------------------
    # Page routes
    # -------------------------------------------------------------------------
    @router
    def demo_simple(request):
        return handle_htmx_request(
            request, simple["page_content"],
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar),
        )

    @router
    def demo_dual(request):
        return handle_htmx_request(
            request, dual_panel["page_content"],
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar),
        )

    @router
    def demo_modes(request):
        return handle_htmx_request(
            request, modes["page_content"],
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar),
        )

    @router
    def demo_wasd(request):
        return handle_htmx_request(
            request, wasd["page_content"],
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar),
        )

    @router
    def demo_hierarchy(request):
        return handle_htmx_request(
            request, hierarchy["page_content"],
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar),
        )

    # -------------------------------------------------------------------------
    # Navbar & route registration
    # -------------------------------------------------------------------------
    navbar = create_navbar(
        title="Keyboard Nav Demo",
        nav_items=[
            ("Home", index),
            ("Simple", demo_simple),
            ("Dual Panel", demo_dual),
            ("Modes", demo_modes),
            ("WASD", demo_wasd),
            ("Hierarchy", demo_hierarchy),
        ],
        home_route=index,
        theme_selector=True,
    )

    register_routes(
        app, router,
        simple["router"], dual_panel["router"], modes["router"],
        wasd["router"], hierarchy["router"],
    )

    # Debug output
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

    app = main()

    port = 5033
    host = "0.0.0.0"
    display_host = 'localhost' if host in ['0.0.0.0', '127.0.0.1'] else host

    print(f"Server: http://{display_host}:{port}")
    print(f"\n  http://{display_host}:{port}/              — Homepage")
    print(f"  http://{display_host}:{port}/demo_simple    — Simple list")
    print(f"  http://{display_host}:{port}/demo_dual      — Dual panel")
    print(f"  http://{display_host}:{port}/demo_modes     — Mode switching")
    print(f"  http://{display_host}:{port}/demo_wasd      — WASD keys")
    print(f"  http://{display_host}:{port}/demo_hierarchy  — Hierarchical systems")
    print()

    timer = threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{port}"))
    timer.daemon = True
    timer.start()

    uvicorn.run(app, host=host, port=port)
