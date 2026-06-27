"""
SolarSentinel — Page 3: Weather Impact Analysis
Correlates environmental conditions with solar power output.
"""

import dash
from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
import pandas as pd

from data.loader import load_merged, load_all_weather

dash.register_page(__name__, path="/weather-analysis", name="Weather Analysis", order=2)

_merged  = load_merged()
_weather = load_all_weather()

PLOT_BG  = "rgba(0,0,0,0)"
GRID_COL = "rgba(30,58,95,0.4)"
TEXT_COL = "#94a3b8"
FONT_FAM = "Inter, system-ui, sans-serif"
SOLAR    = "#f59e0b"
GREEN    = "#10b981"
BLUE     = "#3b82f6"
RED      = "#ef4444"
PURPLE   = "#8b5cf6"

BASE_LAYOUT = dict(
    plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
    font=dict(family=FONT_FAM, color=TEXT_COL, size=12),
)

layout = html.Div([
    html.Div(className="page-container", children=[

        html.Div(className="page-header", children=[
            html.H1("🌤️ Weather Impact Analysis", className="page-title"),
            html.P(
                "Environmental drivers of solar generation · Irradiance, temperature and performance ratio",
                className="page-subtitle"
            ),
        ]),

        # Controls
        html.Div(className="controls-row", children=[
            html.Span("Plant:", className="control-label"),
            dcc.Dropdown(
                id="wx-plant-filter",
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

        # Row 1: Irradiation over time + scatter
        html.Div(className="chart-grid chart-grid-2", children=[

            html.Div(className="chart-card", children=[
                html.Div(className="chart-card-header", children=[
                    html.Div([
                        html.Div("Solar Irradiation Over Time", className="chart-title"),
                        html.Div("Raw irradiance sensor readings across the 34-day period", className="chart-desc"),
                    ]),
                    html.Span("SENSOR DATA", className="chart-badge badge-solar"),
                ]),
                dcc.Graph(id="irr-time-chart", config={"displayModeBar": False}, style={"height": "300px"}),
            ]),

            html.Div(className="chart-card", children=[
                html.Div(className="chart-card-header", children=[
                    html.Div([
                        html.Div("Module Temp vs Irradiation", className="chart-title"),
                        html.Div("Panel heating effect — higher irradiance drives module temperature up", className="chart-desc"),
                    ]),
                    html.Span("THERMAL RESPONSE", className="chart-badge badge-red"),
                ]),
                dcc.Graph(id="temp-irr-scatter", config={"displayModeBar": False}, style={"height": "300px"}),
            ]),
        ]),

        # Row 2: Performance ratio + daily irradiation bar
        html.Div(className="chart-grid chart-grid-2", children=[

            html.Div(className="chart-card", children=[
                html.Div(className="chart-card-header", children=[
                    html.Div([
                        html.Div("Performance Ratio Over Time", className="chart-title"),
                        html.Div("AC Power ÷ Irradiation × 1000 — efficiency under actual conditions", className="chart-desc"),
                    ]),
                    html.Span("KPI", className="chart-badge badge-green"),
                ]),
                dcc.Graph(id="perf-ratio-chart", config={"displayModeBar": False}, style={"height": "300px"}),
            ]),

            html.Div(className="chart-card", children=[
                html.Div(className="chart-card-header", children=[
                    html.Div([
                        html.Div("Daily Peak Irradiation", className="chart-title"),
                        html.Div("Maximum irradiance reached each day — cloud cover impact visible", className="chart-desc"),
                    ]),
                    html.Span("DAILY PEAK", className="chart-badge badge-blue"),
                ]),
                dcc.Graph(id="daily-irr-bar", config={"displayModeBar": False}, style={"height": "300px"}),
            ]),
        ]),

        # Row 3: Full-width irradiance heatmap (hour × day)
        html.Div(className="chart-card", children=[
            html.Div(className="chart-card-header", children=[
                html.Div([
                    html.Div("Irradiation Heatmap: Hour of Day × Date", className="chart-title"),
                    html.Div("Solar resource availability across every hour of every day — cloud patterns visible", className="chart-desc"),
                ]),
                html.Span("CALENDAR VIEW", className="chart-badge badge-purple"),
            ]),
            dcc.Graph(id="irr-heatmap", config={"displayModeBar": False}, style={"height": "320px"}),
        ]),
    ]),
])


@callback(
    Output("irr-time-chart",  "figure"),
    Output("temp-irr-scatter","figure"),
    Output("perf-ratio-chart","figure"),
    Output("daily-irr-bar",   "figure"),
    Output("irr-heatmap",     "figure"),
    Input("wx-plant-filter",  "value"),
)
def update_wx_charts(plant_filter: str):
    if plant_filter == "both":
        merged  = _merged.copy()
        weather = _weather.copy()
    else:
        merged  = _merged[_merged["PLANT_LABEL"] == plant_filter].copy()
        weather = _weather[_weather["PLANT_LABEL"] == plant_filter].copy()

    colors = {"Plant 1": SOLAR, "Plant 2": BLUE}

    # ── Irradiation over time ─────────────────────────────────────────────────
    fig1 = go.Figure()
    for plant, grp in weather.groupby("PLANT_LABEL"):
        grp_day = grp[grp["IRRADIATION"] > 0].sort_values("DATE_TIME")
        if len(grp_day) > 3000:
            grp_day = grp_day.sample(3000, random_state=42).sort_values("DATE_TIME")
        fig1.add_trace(go.Scatter(
            x=grp_day["DATE_TIME"], y=grp_day["IRRADIATION"],
            mode="lines", name=plant,
            line=dict(color=colors.get(plant, SOLAR), width=1.2),
            opacity=0.8,
            hovertemplate="%{x|%d %b %H:%M}<br>Irradiation: %{y:.4f} W/m²<extra>" + plant + "</extra>",
        ))
    fig1.update_layout(**BASE_LAYOUT, margin=dict(l=8, r=8, t=8, b=8),
        yaxis_title="Irradiation (W/m²)",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0),
    )
    fig1.update_xaxes(gridcolor=GRID_COL, zerolinecolor=GRID_COL)
    fig1.update_yaxes(gridcolor=GRID_COL, zerolinecolor=GRID_COL)

    # ── Module temp vs Irradiation scatter ────────────────────────────────────
    fig2 = go.Figure()
    sample_wx = weather[weather["IRRADIATION"] > 0].sample(
        min(2000, len(weather[weather["IRRADIATION"] > 0])), random_state=42
    ) if len(weather[weather["IRRADIATION"] > 0]) > 2000 else weather[weather["IRRADIATION"] > 0]
    for plant, grp in sample_wx.groupby("PLANT_LABEL"):
        fig2.add_trace(go.Scatter(
            x=grp["IRRADIATION"], y=grp["MODULE_TEMPERATURE"],
            mode="markers", name=plant,
            marker=dict(color=colors.get(plant, SOLAR), size=4, opacity=0.5),
            hovertemplate="Irradiation: %{x:.4f}<br>Module Temp: %{y:.1f}°C<extra>" + plant + "</extra>",
        ))
    fig2.update_layout(**BASE_LAYOUT, margin=dict(l=8, r=8, t=8, b=8),
        xaxis_title="Irradiation (W/m²)", yaxis_title="Module Temperature (°C)",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0),
    )
    fig2.update_xaxes(gridcolor=GRID_COL, zerolinecolor=GRID_COL)
    fig2.update_yaxes(gridcolor=GRID_COL, zerolinecolor=GRID_COL)

    # ── Performance ratio ─────────────────────────────────────────────────────
    fig3 = go.Figure()
    if not merged.empty:
        pr = merged[merged["IRRADIATION"] > 0.01].copy()
        pr["PERF_RATIO"] = pr["TOTAL_AC_POWER"] / (pr["IRRADIATION"] * 1000 + 1e-9)
        pr_daily = pr.groupby(["DATE", "PLANT_LABEL"], as_index=False).agg(
            AVG_PR=("PERF_RATIO", "median")
        )
        pr_daily["DATE"] = pd.to_datetime(pr_daily["DATE"])
        for plant, grp in pr_daily.groupby("PLANT_LABEL"):
            fig3.add_trace(go.Scatter(
                x=grp["DATE"], y=grp["AVG_PR"],
                mode="lines+markers", name=plant,
                line=dict(color=colors.get(plant, SOLAR), width=2),
                marker=dict(size=5),
                hovertemplate="%{x|%d %b}<br>Perf Ratio: %{y:.3f}<extra>" + plant + "</extra>",
            ))
    fig3.update_layout(**BASE_LAYOUT, margin=dict(l=8, r=8, t=8, b=8),
        yaxis_title="Performance Ratio",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0),
    )
    fig3.update_xaxes(gridcolor=GRID_COL, zerolinecolor=GRID_COL)
    fig3.update_yaxes(gridcolor=GRID_COL, zerolinecolor=GRID_COL)

    # ── Daily peak irradiation ────────────────────────────────────────────────
    fig4 = go.Figure()
    daily_irr = weather.groupby(["DATE", "PLANT_LABEL"], as_index=False).agg(
        PEAK_IRR=("IRRADIATION", "max")
    )
    daily_irr["DATE"] = pd.to_datetime(daily_irr["DATE"])
    for plant, grp in daily_irr.groupby("PLANT_LABEL"):
        fig4.add_trace(go.Bar(
            x=grp["DATE"], y=grp["PEAK_IRR"],
            name=plant, marker_color=colors.get(plant, SOLAR), opacity=0.8,
            hovertemplate="%{x|%d %b}<br>Peak Irr: %{y:.4f} W/m²<extra>" + plant + "</extra>",
        ))
    fig4.update_layout(**BASE_LAYOUT, margin=dict(l=8, r=8, t=8, b=8),
        yaxis_title="Peak Irradiation (W/m²)", barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0),
    )
    fig4.update_xaxes(gridcolor=GRID_COL, zerolinecolor=GRID_COL)
    fig4.update_yaxes(gridcolor=GRID_COL, zerolinecolor=GRID_COL)

    # ── Irradiation heatmap ───────────────────────────────────────────────────
    wx_day = weather[weather["IRRADIATION"] > 0].copy()
    wx_day["DATE_STR"] = wx_day["DATE_TIME"].dt.strftime("%d %b")
    pivot = wx_day.groupby(["HOUR", "DATE_STR"])["IRRADIATION"].mean().unstack(fill_value=0)
    fig5 = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=[f"{h:02d}:00" for h in pivot.index.tolist()],
        colorscale=[
            [0.0, "#080d1a"],
            [0.2, "#1e3a5f"],
            [0.5, "#b45309"],
            [0.8, "#f59e0b"],
            [1.0, "#fde68a"],
        ],
        hovertemplate="Date: %{x}<br>Hour: %{y}<br>Irradiation: %{z:.4f}<extra></extra>",
        showscale=True,
        colorbar=dict(thickness=12, tickfont=dict(color=TEXT_COL, size=10), outlinecolor="rgba(0,0,0,0)"),
    ))
    fig5.update_layout(**BASE_LAYOUT, margin=dict(l=60, r=20, t=8, b=80))
    fig5.update_xaxes(tickangle=-45, tickfont=dict(size=9), gridcolor="rgba(0,0,0,0)")
    fig5.update_yaxes(autorange="reversed", tickfont=dict(size=10), gridcolor="rgba(0,0,0,0)")

    return fig1, fig2, fig3, fig4, fig5
