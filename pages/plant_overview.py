"""
SolarSentinel — Page 1: Plant Overview
Shows top KPIs, daily generation trend, plant comparison and hourly profile.
"""

import dash
from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
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

# ── Plotly theme ─────────────────────────────────────────────────────────────
PLOT_BG  = "rgba(0,0,0,0)"
GRID_COL = "rgba(30,58,95,0.4)"
TEXT_COL = "#94a3b8"
FONT_FAM = "Inter, system-ui, sans-serif"
SOLAR    = "#f59e0b"
GREEN    = "#10b981"
BLUE     = "#3b82f6"
RED      = "#ef4444"

BASE_LAYOUT = dict(
    plot_bgcolor=PLOT_BG,
    paper_bgcolor=PLOT_BG,
    font=dict(family=FONT_FAM, color=TEXT_COL, size=12),
    margin=dict(l=8, r=8, t=8, b=8),
    xaxis=dict(gridcolor=GRID_COL, zerolinecolor=GRID_COL, tickfont=dict(size=11)),
    yaxis=dict(gridcolor=GRID_COL, zerolinecolor=GRID_COL, tickfont=dict(size=11)),
)
LEGEND_TOP = dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(30,58,95,0.3)", borderwidth=1,
                  orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0)

# Hard-coded fill colours (avoids any hex conversion math)
FILL_COLORS = {
    "Plant 1": "rgba(245,158,11,0.12)",
    "Plant 2": "rgba(59,130,246,0.08)",
}


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
                kpi_card("Total Energy Generated",  f"{_kpis['total_mwh']:,}",   "MWh",       "⚡", SOLAR),
                kpi_card("Peak Power Output",        f"{_kpis['peak_kw']:,}",     "kW",        "📈", GREEN),
                kpi_card("Active Inverters",         f"{_kpis['n_inverters']}",   "units",     "🔧", BLUE),
                kpi_card("Solar Plants Monitored",   f"{_kpis['n_plants']}",      "facilities","🏭", "#8b5cf6"),
                kpi_card("Avg DC→AC Efficiency",     f"{_kpis['avg_eff_pct']}",   "%",         "⚙️", GREEN),
                kpi_card("Days of Operations Data",  f"{_kpis['n_days']}",        "days",      "📅", "#06b6d4"),
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

        # Row 1: Daily generation + Irradiance scatter
        html.Div(className="chart-grid chart-grid-2", children=[

            html.Div(className="chart-card", children=[
                html.Div(className="chart-card-header", children=[
                    html.Div([
                        html.Div("Daily AC Generation Trend", className="chart-title"),
                        html.Div("Total AC output aggregated per day per plant", className="chart-desc"),
                    ]),
                    html.Span("DAILY TREND", className="chart-badge badge-solar"),
                ]),
                dcc.Graph(id="daily-gen-chart", config={"displayModeBar": False}, style={"height": "300px"}),
            ]),

            html.Div(className="chart-card", children=[
                html.Div(className="chart-card-header", children=[
                    html.Div([
                        html.Div("Irradiance vs AC Power Output", className="chart-title"),
                        html.Div("Scatter correlation — solar resource driving generation", className="chart-desc"),
                    ]),
                    html.Span("CORRELATION", className="chart-badge badge-green"),
                ]),
                dcc.Graph(id="irr-vs-power-chart", config={"displayModeBar": False}, style={"height": "300px"}),
            ]),
        ]),

        # Row 2: Hourly profile + Temperature
        html.Div(className="chart-grid chart-grid-2", children=[

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

            html.Div(className="chart-card", children=[
                html.Div(className="chart-card-header", children=[
                    html.Div([
                        html.Div("Ambient vs Module Temperature", className="chart-title"),
                        html.Div("Panel heat stress — module temp consistently higher than ambient", className="chart-desc"),
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
    Output("daily-gen-chart",     "figure"),
    Output("irr-vs-power-chart",  "figure"),
    Output("hourly-profile-chart","figure"),
    Output("temp-chart",          "figure"),
    Input("plant-filter",         "value"),
)
def update_charts(plant_filter: str):
    if plant_filter == "both":
        daily  = _daily.copy()
        merged = _merged.copy()
        hourly = _hourly.copy()
    else:
        daily  = _daily[_daily["PLANT_LABEL"] == plant_filter].copy()
        merged = _merged[_merged["PLANT_LABEL"] == plant_filter].copy()
        hourly = _hourly[_hourly["PLANT_LABEL"] == plant_filter].copy()

    line_colors = {"Plant 1": SOLAR, "Plant 2": BLUE}

    # ── Chart 1: Daily generation trend ──────────────────────────────────────
    fig1 = go.Figure()
    for plant, grp in daily.groupby("PLANT_LABEL"):
        fig1.add_trace(go.Scatter(
            x=grp["DATE"],
            y=(grp["TOTAL_AC_KWH"] / 4 / 1000),   # kW readings × 15-min → MWh
            name=plant,
            mode="lines",
            line=dict(color=line_colors.get(plant, SOLAR), width=2.5),
            fill="tozeroy",
            fillcolor=FILL_COLORS.get(plant, "rgba(245,158,11,0.12)"),
            hovertemplate="%{x|%d %b}<br><b>%{y:.2f} MWh</b><extra>" + plant + "</extra>",
        ))
    fig1.update_layout(
        **BASE_LAYOUT,
        xaxis_title=None,
        yaxis_title="Daily Output (MWh)",
        legend=LEGEND_TOP,
    )

    # ── Chart 2: Irradiance vs Power scatter ─────────────────────────────────
    fig2 = go.Figure()
    if not merged.empty:
        sample = merged[merged["IRRADIATION"] > 0].sample(
            min(2000, len(merged[merged["IRRADIATION"] > 0])), random_state=42
        ) if len(merged[merged["IRRADIATION"] > 0]) > 2000 else merged[merged["IRRADIATION"] > 0]

        for plant, grp in sample.groupby("PLANT_LABEL"):
            fig2.add_trace(go.Scatter(
                x=grp["IRRADIATION"],
                y=grp["TOTAL_AC_POWER"],
                mode="markers",
                name=plant,
                marker=dict(color=line_colors.get(plant, SOLAR), size=4, opacity=0.5, line=dict(width=0)),
                hovertemplate="Irradiation: %{x:.4f}<br>AC Power: %{y:.1f} kW<extra>" + plant + "</extra>",
            ))
    fig2.update_layout(
        **BASE_LAYOUT,
        xaxis_title="Irradiation (W/m²)",
        yaxis_title="Total AC Power (kW)",
        legend=LEGEND_TOP,
    )

    # ── Chart 3: Average hourly profile ──────────────────────────────────────
    fig3 = go.Figure()
    for plant, grp in hourly.groupby("PLANT_LABEL"):
        fig3.add_trace(go.Bar(
            x=grp["HOUR"],
            y=grp["AVG_AC_POWER"],
            name=plant,
            marker_color=line_colors.get(plant, SOLAR),
            opacity=0.85,
            hovertemplate="Hour %{x}:00<br>Avg AC: %{y:.1f} kW<extra>" + plant + "</extra>",
        ))
    fig3.update_layout(
        **BASE_LAYOUT,
        xaxis_title="Hour of Day",
        yaxis_title="Avg AC Power (kW)",
        barmode="group",
        legend=LEGEND_TOP,
    )
    fig3.update_xaxes(tickvals=list(range(0, 24, 2)))

    # ── Chart 4: Ambient vs Module Temperature ────────────────────────────────
    fig4 = go.Figure()
    if not merged.empty:
        # Use last 500 rows per plant for a readable time window
        for plant, grp in merged.groupby("PLANT_LABEL"):
            grp_sorted = grp.sort_values("DATE_TIME").tail(500)
            fig4.add_trace(go.Scatter(
                x=grp_sorted["DATE_TIME"],
                y=grp_sorted["AMBIENT_TEMPERATURE"],
                name=f"{plant} Ambient",
                mode="lines",
                line=dict(color=line_colors.get(plant, SOLAR), width=1.5, dash="dot"),
                hovertemplate="%{x|%d %b %H:%M}<br>Ambient: %{y:.1f}°C<extra>" + plant + "</extra>",
            ))
            fig4.add_trace(go.Scatter(
                x=grp_sorted["DATE_TIME"],
                y=grp_sorted["MODULE_TEMPERATURE"],
                name=f"{plant} Module",
                mode="lines",
                line=dict(color=RED if plant == "Plant 1" else "#8b5cf6", width=1.5),
                hovertemplate="%{x|%d %b %H:%M}<br>Module: %{y:.1f}°C<extra>" + plant + "</extra>",
            ))
    fig4.update_layout(
        **BASE_LAYOUT,
        yaxis_title="Temperature (°C)",
        xaxis_title=None,
        legend={**LEGEND_TOP, "font": dict(size=10)},
    )

    return fig1, fig2, fig3, fig4
