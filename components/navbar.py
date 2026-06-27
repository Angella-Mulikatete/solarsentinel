"""SolarSentinel — Top Navigation Bar Component"""

from dash import html, dcc


def navbar():
    return html.Header(
        className="navbar",
        children=[
            # Brand
            html.A(
                href="/",
                className="navbar-brand",
                children=[
                    html.Div("☀️", className="navbar-logo"),
                    html.Div([
                        html.Div("SolarSentinel", className="navbar-title"),
                        html.Div("SOLAR PLANT INTELLIGENCE · INDIA · 2020", className="navbar-subtitle"),
                    ]),
                ],
            ),

            # Navigation links
            html.Nav(
                className="navbar-links",
                children=[
                    dcc.Link("🏭 Overview",   href="/",                className="nav-link", id="nav-overview"),
                    dcc.Link("⚡ Inverters",   href="/inverter-grid",   className="nav-link", id="nav-inverters"),
                    dcc.Link("🌤️ Weather",    href="/weather-analysis", className="nav-link", id="nav-weather"),
                    dcc.Link("📈 Yield",       href="/yield-tracker",   className="nav-link", id="nav-yield"),
                ],
            ),

            # Live indicator
            html.Div(
                className="nav-live",
                children=[
                    html.Div(className="pulse-dot"),
                    "REAL DATA · 34 DAYS",
                ],
            ),
        ],
    )
