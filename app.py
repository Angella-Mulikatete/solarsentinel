"""
SolarSentinel — Main Application Entry Point
Dash multi-page app served by Gunicorn (WSGI).

Run locally:   python app.py
Run with WSGI: gunicorn app:server --workers 2 --threads 4 --bind 0.0.0.0:$PORT
"""

import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

from components.navbar import navbar

# ── Initialise app ───────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description",
         "content": "SolarSentinel — Production-grade solar plant performance dashboard. "
                    "Real telemetry from two Indian PV plants: inverter monitoring, "
                    "weather correlation and yield tracking."},
        {"name": "theme-color", "content": "#080d1a"},
    ],
    title="SolarSentinel | Solar Plant Intelligence",
)

# Gunicorn needs this
server = app.server

# ── Root layout ──────────────────────────────────────────────────────────────
app.layout = html.Div(
    id="root",
    children=[
        # URL tracker (required for multi-page active link styling)
        dcc.Location(id="url", refresh=False),

        # Navigation bar
        navbar(),

        # Page content injected here by Dash Pages
        dash.page_container,
    ],
)


# ── Active nav-link styling ──────────────────────────────────────────────────
@callback(
    Output("nav-overview",  "className"),
    Output("nav-inverters", "className"),
    Output("nav-weather",   "className"),
    Output("nav-yield",     "className"),
    Input("url", "pathname"),
)
def update_active_link(pathname: str):
    base = "nav-link"
    active = "nav-link active"
    mapping = {
        "/":                 [active, base,   base,   base],
        "/inverter-grid":    [base,   active, base,   base],
        "/weather-analysis": [base,   base,   active, base],
        "/yield-tracker":    [base,   base,   base,   active],
    }
    return mapping.get(pathname, [base, base, base, base])


# ── Dev server ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
