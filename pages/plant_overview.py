"""
SolarSentinel — Page 1: Plant Overview
Shows top KPIs, daily generation trend, plant comparison and hourly profile.
"""

import dash
from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from data.loader import (
    get_kpis, daily_generation, load_merged, hourly_profile
)

dash.register_page(__name__, path="/", name="Plant Overview", order=0)

# ── Pre-load data ────────────────────────────────────────────────────────────
_kpis   = get_kpis()
_daily  = daily_generation()
_merged = load_merged()
_hourly = hourly_profile()

# ── Plotly theme helper ──────────────────────────────────────────────────────
PLOT_BG   = "rgba(0,0,0,0)"
PAPER_BG  = "rgba(0,0,0,0)"
GRID_COL  = "rgba(30,58,95,0.4)"
TEXT_COL  = "#94a3b8"
FONT_FAM  = "Inter, system-ui, sans-serif"
SOLAR     = "#f59e0b"
GREEN     = "#10b981"
BLUE      = "#3b82f6"
RED       = "#ef4444"

BASE_LAYOUT = dict(
    plot_bgcolor=PLOT_BG,
    paper_bgcolor=PAPER_BG,
    font=dict(family=FONT_FAM, color=TEXT_COL, size=12),
    margin=dict(l=8, r=8, t=8, b=8),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(30,58,95,0.3)", borderwidth=1),
    xaxis=dict(gridcolor=GRID_COL, zerolinecolor=GRID_COL, tickfont=dict(size=11)),
    yaxis=dict(gridcolor=GRID_COL, zerolinecolor=GRID_COL, tickfont=dict(size=11)),
)


def kpi_card(label: str, value: str, unit: str, icon: str, accent: str = "#f59e0b") -> html.Div:
    return html.Div(
        className="kpi-card",
        style={"--kpi-accent": accent},
        children=[
            html.Div(icon, className="kpi-icon"),
            html.Div(label, className="kpi-label"),
            html.Div(value, className="kpi-value", style={"color": accent}),
            html.Div(unit,  className="kpi-unit"),
        ],
    )


# ── Layout ──────────────────────────────────────────────────────────────────
layout = html.Div([
    html.Div(className="page-container", children=[

        # Page header
        html.Div(className="page-header", children=[
            html.H1("🏭 Plant Operations Overview", className="page-title"),
            html.P(
                "Real-time generation monitoring across both Indian solar PV plants · "
                "15-minute interval telemetry · May–June 2020",
                className="page-subtitle"
            ),
        ]),

        # KPI row
        html.Div(
            className="kpi-grid",
            id="kpi-grid",
            children=[
                kpi_card("Total Energy Generated",   f"{_kpis['total_mwh']:,}",  "MWh",        "⚡", SOLAR),
                kpi_card("Peak Power Output",         f"{_kpis['peak_kw']:,}",   "kW",          "📈", GREEN),
                kpi_card("Active Inverters",          f"{_kpis['n_inverters']}", "units",       "🔧", BLUE),
                kpi_card("Solar Plants Monitored",    f"{_kpis['n_plants']}",    "facilities",  "🏭", "#8b5cf6"),
                kpi_card("Avg DC→AC Efficiency",      f"{_kpis['avg_eff_pct']}", "%",           "⚙️", GREEN),
                kpi_card("Days of Operations Data",   f"{_kpis['n_days']}",      "days",        "📅", "#06b6d4"),
            ],
        ),

        # Controls row
        html.Div(className="controls-row", children=[
            html.Span("Filter Plant:", className="control-label"),
            dcc.Dropdown(
                id="plant-filter",
                options=[
                    {"label": "Both Plants", "value": "both"},
                    {"label": "Plant 1",     "value": "Plant 1"},
                    {"label": "Plant 2",     "value": "Plant 2"},
                ],
                value="both",
                clearable=False,
                style={"minWidth": "180px"},
            ),
        ]),

        # Row 1: Daily generation + plant comparison
        html.Div(className="chart-grid chart-grid-2", children=[

            # Daily AC generation trend
            html.Div(className="chart-card", children=[
                html.Div(className="chart-card-header", children=[
                    html.Div([
                        html.Div("Daily AC Generation Trend", className="chart-title"),
                        html.Div("Total AC output aggregated per day per plant", className="chart-desc"),
                    ]),
                    html.Span("HOURLY TELEMETRY", className="chart-badge badge-solar"),
                ]),
                dcc.Graph(id="daily-gen-chart", config={"displayModeBar": False}, style={"height": "300px"}),
            ]),

            # Irradiance vs Power
            html.Div(className="chart-card", children=[
                html.Div(className="chart-card-header", children=[
                    html.Div([
                        html.Div("Irradiance vs AC Power Output", className="chart-title"),
                        html.Div("Scatter correlation — environmental driver of generation", className="chart-desc"),
                    ]),
                    html.Span("CORRELATION", className="chart-badge badge-green"),
                ]),
                dcc.Graph(id="irr-vs-power-chart", config={"displayModeBar": False}, style={"height": "300px"}),
            ]),
        ]),

        # Row 2: Hourly profile + plant bar comparison
        html.Div(className="chart-grid chart-grid-2", children=[

            # Average hourly profile
            html.Div(className="chart-card", children=[
                html.Div(className="chart-card-header", children=[
                    html.Div([
                        html.Div("Average Generation Profile (Hour of Day)", className="chart-title"),
                        html.Div("Daily solar bell curve — typical production pattern", className="chart-desc"),
                    ]),
                    html.Span("DAILY PATTERN", className="chart-badge badge-blue"),
                ]),
                dcc.Graph(id="hourly-profile-chart", config={"displayModeBar": False}, style={"height": "280px"}),
            ]),

            # Temperature overview
            html.Div(className="chart-card", children=[
                html.Div(className="chart-card-header", children=[
                    html.Div([
                        html.Div("Ambient vs Module Temperature", className="chart-title"),
                        html.Div("Panel heat stress — module temperature consistently higher", className="chart-desc"),
                    ]),
                    html.Span("THERMAL", className="chart-badge badge-purple"),
                ]),
                dcc.Graph(id="temp-chart", config={"displayModeBar": False}, style={"height": "280px"}),
            ]),
        ]),
    ]),
])


# ── Callbacks ────────────────────────────────────────────────────────────────

@callback(
    Output("daily-gen-chart",    "figure"),
    Output("irr-vs-power-chart", "figure"),
    Output("hourly-profile-chart","figure"),
    Output("temp-chart",         "figure"),
    Input("plant-filter",        "value"),
)
def update_charts(plant_filter: str):
    # Filter data
    if plant_filter == "both":
        daily  = _daily.copy()
        merged = _merged.copy()
        hourly = _hourly.copy()
    else:
        daily  = _daily[_daily["PLANT_LABEL"] == plant_filter].copy()
        merged = _merged[_merged["PLANT_LABEL"] == plant_filter].copy()
        hourly = _hourly[_hourly["PLANT_LABEL"] == plant_filter].copy()

    colors = {
        "Plant 1": SOLAR,
        "Plant 2": BLUE,
    }

    # ── Chart 1: Daily generation ────────────────────────────────────────────
    fig1 = go.Figure()
    for plant, grp in daily.groupby("PLANT_LABEL"):
        fig1.add_trace(go.Scatter(
            x=grp["DATE"], y=(grp["TOTAL_AC_KWH"] / 4 / 1000),  # MWh
            name=plant,
            mode="lines",
            line=dict(color=colors.get(plant, SOLAR), width=2.5),
            fill="tozeroy",
            fillcolor=f"rgba({','.join(str(int(c*255)) for c in px.colors.hex_to_rgb(colors.get(plant, SOLAR)))},0.12)" if plant == "Plant 1" else f"rgba(59,130,246,0.08)",
            hovertemplate="%{x|%d %b}<br><b>%{y:.2f} MWh</b><extra>" + plant + "</extra>",
        ))
    fig1.update_layout(**BASE_LAYOUT,
        xaxis_title=None, yaxis_title="MWh",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
    )
    fig1.update_xaxes(showgrid=True)
    fig1.update_yaxes(showgrid=True)

    # ── Chart 2: Irradiance vs Power ─────────────────────────────────────────
    fig2 = go.Figure()
    sample = merged.sample(min(2000, len(merged)), random_state=42) if len(merged) > 2000 else merged
    for plant, grp in sample.groupby("PLANT_LABEL"):
        fig2.add_trace(go.Scatter(
            x=grp["IRRADIATION"], y=grp["TOTAL_AC_POWER"],
            mode="markers",
            name=plant,
            marker=dict(
                color=colors.get(plant, SOLAR),
                size=4, opacity=0.5,
                line=dict(width=0),
            ),
            hovertemplate="Irradiation: %{x:.3f}<br>AC Power: %{y:.1f} kW<extra>" + plant + "</extra>",
        ))
    fig2.update_layout(**BASE_LAYOUT,
        xaxis_title="Irradiation (W/m²)", yaxis_title="Total AC Power (kW)",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
    )

    # ── Chart 3: Hourly profile ──────────────────────────────────────────────
    fig3 = go.Figure()
    for plant, grp in hourly.groupby("PLANT_LABEL"):
        fig3.add_trace(go.Bar(
            x=grp["HOUR"], y=grp["AVG_AC_POWER"],
            name=plant,
            marker_color=colors.get(plant, SOLAR),
            opacity=0.85,
            hovertemplate="Hour %{x}:00<br>Avg AC: %{y:.1f} kW<extra>" + plant + "</extra>",
        ))
    fig3.update_layout(**BASE_LAYOUT,
        xaxis_title="Hour of Day", yaxis_title="Avg AC Power (kW)",
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0),
    )
    fig3.update_xaxes(tickvals=list(range(0, 24, 2)))

    # ── Chart 4: Temperature ─────────────────────────────────────────────────
    fig4 = go.Figure()
    if not merged.empty:
        sample_temp = merged.sample(min(1500, len(merged)), random_state=1) if len(merged) > 1500 else merged
        for plant, grp in sample_temp.groupby("PLANT_LABEL"):
            grp_sorted = grp.sort_values("DATE_TIME").tail(500)
            fig4.add_trace(go.Scatter(
                x=grp_sorted["DATE_TIME"], y=grp_sorted["AMBIENT_TEMPERATURE"],
                name=f"{plant} Ambient",
                mode="lines",
                line=dict(color=colors.get(plant, SOLAR), width=1.5, dash="dot"),
            ))
            fig4.add_trace(go.Scatter(
                x=grp_sorted["DATE_TIME"], y=grp_sorted["MODULE_TEMPERATURE"],
                name=f"{plant} Module",
                mode="lines",
                line=dict(color=RED if plant == "Plant 1" else "#8b5cf6", width=1.5),
            ))
    fig4.update_layout(**BASE_LAYOUT,
        yaxis_title="Temperature (°C)",
        xaxis_title=None,
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0, font=dict(size=10)),
    )

    return fig1, fig2, fig3, fig4
