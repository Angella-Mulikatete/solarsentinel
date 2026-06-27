"""
SolarSentinel — Page 2: Inverter Performance Grid
Heatmap of all inverters, efficiency ranking, and drill-down time series.
"""

import dash
from dash import html, dcc, callback, Output, Input
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from data.loader import inverter_summary, load_all_generation

dash.register_page(__name__, path="/inverter-grid", name="Inverter Grid", order=1)

# Pre-load
_inv_summary = inverter_summary()
_gen         = load_all_generation()

# Plot theme
PLOT_BG  = "rgba(0,0,0,0)"
GRID_COL = "rgba(30,58,95,0.4)"
TEXT_COL = "#94a3b8"
FONT_FAM = "Inter, system-ui, sans-serif"
SOLAR    = "#f59e0b"
GREEN    = "#10b981"
BLUE     = "#3b82f6"
RED      = "#ef4444"

BASE_LAYOUT = dict(
    plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
    font=dict(family=FONT_FAM, color=TEXT_COL, size=12),
    margin=dict(l=8, r=8, t=8, b=8),
    xaxis=dict(gridcolor=GRID_COL, zerolinecolor=GRID_COL),
    yaxis=dict(gridcolor=GRID_COL, zerolinecolor=GRID_COL),
)

# Inverter dropdown options
inv_options_p1 = [
    {"label": f"⚡ {r['INV_ID']}", "value": r["SOURCE_KEY"]}
    for _, r in _inv_summary[_inv_summary["PLANT_LABEL"] == "Plant 1"].iterrows()
]
inv_options_p2 = [
    {"label": f"⚡ {r['INV_ID']}", "value": r["SOURCE_KEY"]}
    for _, r in _inv_summary[_inv_summary["PLANT_LABEL"] == "Plant 2"].iterrows()
]
all_inv_options = inv_options_p1 + inv_options_p2

layout = html.Div([
    html.Div(className="page-container", children=[

        html.Div(className="page-header", children=[
            html.H1("⚡ Inverter Performance Grid", className="page-title"),
            html.P(
                "Per-inverter health monitoring · DC→AC efficiency · Underperformer detection",
                className="page-subtitle"
            ),
        ]),

        # Status row
        html.Div(id="inverter-status-row", className="status-row"),

        # Row 1: Efficiency heatmap + Ranking bar
        html.Div(className="chart-grid chart-grid-2", children=[

            html.Div(className="chart-card", children=[
                html.Div(className="chart-card-header", children=[
                    html.Div([
                        html.Div("Inverter Total AC Yield Heatmap", className="chart-title"),
                        html.Div("All inverters across both plants — darker = lower output", className="chart-desc"),
                    ]),
                    html.Span("COMPARATIVE", className="chart-badge badge-solar"),
                ]),
                dcc.Graph(id="inv-heatmap", config={"displayModeBar": False}, style={"height": "340px"}),
            ]),

            html.Div(className="chart-card", children=[
                html.Div(className="chart-card-header", children=[
                    html.Div([
                        html.Div("Inverter Efficiency Ranking", className="chart-title"),
                        html.Div("Average DC→AC conversion efficiency · Red = underperformer", className="chart-desc"),
                    ]),
                    html.Span("RANKING", className="chart-badge badge-green"),
                ]),
                dcc.Graph(id="inv-ranking", config={"displayModeBar": False}, style={"height": "340px"}),
            ]),
        ]),

        # Row 2: Drill-down time series
        html.Div(className="chart-card", style={"marginBottom": "20px"}, children=[
            html.Div(className="chart-card-header", children=[
                html.Div([
                    html.Div("Inverter Deep-Dive: AC Power Time Series", className="chart-title"),
                    html.Div("Select an inverter below to inspect its full output history", className="chart-desc"),
                ]),
                html.Span("DRILL-DOWN", className="chart-badge badge-blue"),
            ]),
            html.Div(className="controls-row", children=[
                html.Span("Select Inverter:", className="control-label"),
                dcc.Dropdown(
                    id="inverter-select",
                    options=all_inv_options,
                    value=all_inv_options[0]["value"] if all_inv_options else None,
                    clearable=False,
                    style={"minWidth": "260px"},
                ),
            ]),
            dcc.Graph(id="inv-timeseries", config={"displayModeBar": False}, style={"height": "280px"}),
        ]),

        # Row 3: Daily yield scatter per inverter
        html.Div(className="chart-card", children=[
            html.Div(className="chart-card-header", children=[
                html.Div([
                    html.Div("Daily Yield Distribution by Inverter", className="chart-title"),
                    html.Div("Box plot showing spread and outliers per inverter", className="chart-desc"),
                ]),
                html.Span("DISTRIBUTION", className="chart-badge badge-purple"),
            ]),
            dcc.Dropdown(
                id="plant-select-inv",
                options=[
                    {"label": "Plant 1", "value": "Plant 1"},
                    {"label": "Plant 2", "value": "Plant 2"},
                ],
                value="Plant 1",
                clearable=False,
                style={"minWidth": "160px", "marginBottom": "12px"},
            ),
            dcc.Graph(id="inv-boxplot", config={"displayModeBar": False}, style={"height": "320px"}),
        ]),
    ]),
])


@callback(
    Output("inverter-status-row", "children"),
    Output("inv-heatmap",         "figure"),
    Output("inv-ranking",         "figure"),
    Input("plant-select-inv",     "value"),   # just to trigger on page load
)
def update_heatmap(_plant):
    inv = _inv_summary.copy()

    # Status pills
    n_total = len(inv)
    avg_eff = inv["AVG_EFFICIENCY"].mean()
    n_fault = int((inv["AVG_EFFICIENCY"] < 85).sum())
    status_pills = [
        html.Div([html.Div(className="pulse-dot"), f"{n_total} Inverters Monitored"], className="status-pill status-online"),
        html.Div(f"⚙️ Avg Efficiency: {avg_eff:.1f}%", className="status-pill status-online"),
        html.Div(f"⚠️ {n_fault} Below 85% Efficiency", className="status-pill " + ("status-warn" if n_fault > 0 else "status-online")),
    ]

    # ── Heatmap ──────────────────────────────────────────────────────────────
    pivot = inv.pivot_table(index="PLANT_LABEL", columns="INV_ID", values="TOTAL_AC_KWH", aggfunc="sum")
    fig_heat = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[
            [0.0,  "#1e1b4b"],
            [0.3,  "#1e3a5f"],
            [0.6,  "#b45309"],
            [1.0,  "#f59e0b"],
        ],
        hovertemplate="Inverter: %{x}<br>Plant: %{y}<br>Total AC: %{z:,.0f} kW<extra></extra>",
        showscale=True,
        colorbar=dict(
            thickness=12,
            tickfont=dict(color=TEXT_COL, size=10),
            outlinecolor="rgba(0,0,0,0)",
        ),
    ))
    fig_heat.update_layout(
        **{k: v for k, v in BASE_LAYOUT.items() if k not in ("xaxis", "yaxis")},
        xaxis=dict(tickangle=-45, tickfont=dict(size=9), gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(tickfont=dict(size=11), gridcolor="rgba(0,0,0,0)"),
        margin=dict(l=70, r=20, t=8, b=90),
    )

    # ── Efficiency ranking bar ────────────────────────────────────────────────
    inv_sorted = inv.sort_values("AVG_EFFICIENCY")
    colors = [
        RED if e < 85 else (SOLAR if e < 93 else GREEN)
        for e in inv_sorted["AVG_EFFICIENCY"]
    ]
    fig_rank = go.Figure(go.Bar(
        x=inv_sorted["INV_ID"],
        y=inv_sorted["AVG_EFFICIENCY"],
        marker_color=colors,
        hovertemplate="Inverter: %{x}<br>Efficiency: %{y:.1f}%<extra></extra>",
    ))
    fig_rank.add_hline(y=90, line_dash="dash", line_color="rgba(245,158,11,0.5)",
                       annotation_text="90% threshold", annotation_font_color=SOLAR)
    fig_rank.update_layout(**BASE_LAYOUT,
        xaxis=dict(tickangle=-45, tickfont=dict(size=9), gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(range=[70, 105], gridcolor=GRID_COL, title="Efficiency (%)"),
        margin=dict(l=50, r=8, t=8, b=80),
    )

    return status_pills, fig_heat, fig_rank


@callback(
    Output("inv-timeseries", "figure"),
    Input("inverter-select", "value"),
)
def update_timeseries(source_key: str):
    if not source_key:
        return go.Figure()

    inv_data = _gen[_gen["SOURCE_KEY"] == source_key].sort_values("DATE_TIME")
    plant_label = inv_data["PLANT_LABEL"].iloc[0] if not inv_data.empty else ""
    inv_id = source_key[-8:]
    color = SOLAR if plant_label == "Plant 1" else BLUE

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=inv_data["DATE_TIME"], y=inv_data["AC_POWER"],
        mode="lines", name="AC Power",
        line=dict(color=color, width=1.5),
        fill="tozeroy",
        fillcolor=f"rgba(245,158,11,0.08)" if plant_label == "Plant 1" else "rgba(59,130,246,0.08)",
        hovertemplate="%{x|%d %b %H:%M}<br><b>AC: %{y:.1f} kW</b><extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=inv_data["DATE_TIME"], y=inv_data["DC_POWER"],
        mode="lines", name="DC Power",
        line=dict(color=GREEN, width=1, dash="dot"),
        hovertemplate="%{x|%d %b %H:%M}<br>DC: %{y:.1f} kW<extra></extra>",
    ))
    fig.update_layout(**BASE_LAYOUT,
        yaxis_title="Power (kW)",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0),
        title=dict(text=f"Inverter {inv_id}  ·  {plant_label}", font=dict(size=13, color="#e8f0fe"), x=0),
    )
    return fig


@callback(
    Output("inv-boxplot", "figure"),
    Input("plant-select-inv", "value"),
)
def update_boxplot(plant_label: str):
    data = _gen[(_gen["PLANT_LABEL"] == plant_label) & (_gen["DAILY_YIELD"] > 0)].copy()
    data["INV_ID"] = data["SOURCE_KEY"].str[-8:]

    color = SOLAR if plant_label == "Plant 1" else BLUE

    fig = go.Figure()
    for inv_id, grp in data.groupby("INV_ID"):
        fig.add_trace(go.Box(
            y=grp["DAILY_YIELD"],
            name=inv_id,
            marker_color=color,
            line_color=color,
            boxmean=True,
            hovertemplate="Inverter: %{x}<br>Daily Yield: %{y:.1f} kWh<extra></extra>",
        ))
    fig.update_layout(**BASE_LAYOUT,
        yaxis_title="Daily Yield (kWh)",
        xaxis=dict(tickangle=-45, tickfont=dict(size=9), gridcolor="rgba(0,0,0,0)"),
        showlegend=False,
        margin=dict(l=50, r=8, t=8, b=80),
    )
    return fig
