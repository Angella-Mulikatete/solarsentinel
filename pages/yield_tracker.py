"""
SolarSentinel — Page 4: Yield & Efficiency Tracker
Cumulative yield, DC→AC efficiency trends, and production summary table.
"""

import dash
from dash import html, dcc, callback, Output, Input, dash_table
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from data.loader import load_all_generation, daily_generation, inverter_summary

dash.register_page(__name__, path="/yield-tracker", name="Yield Tracker", order=3)

_gen     = load_all_generation()
_daily   = daily_generation()
_inv_sum = inverter_summary()

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

# Pre-compute cumulative yield per plant
_daily_sorted = _daily.copy()
_daily_sorted["DATE"] = pd.to_datetime(_daily_sorted["DATE"])
_daily_sorted = _daily_sorted.sort_values(["PLANT_LABEL", "DATE"])
_daily_sorted["CUM_MWH"] = _daily_sorted.groupby("PLANT_LABEL")["TOTAL_AC_KWH"].cumsum() / 4 / 1000

# Summary table data
_table_data = (
    _inv_sum[["INV_ID", "PLANT_LABEL", "TOTAL_AC_KWH", "AVG_EFFICIENCY", "MAX_DAILY_YIELD"]]
    .assign(
        TOTAL_MWH=lambda d: (d["TOTAL_AC_KWH"] / 4 / 1000).round(2),
        AVG_EFF=lambda d: d["AVG_EFFICIENCY"].round(1),
        MAX_DAILY_KWH=lambda d: d["MAX_DAILY_YIELD"].round(1),
    )
    .drop(columns=["TOTAL_AC_KWH", "AVG_EFFICIENCY", "MAX_DAILY_YIELD"])
    .rename(columns={
        "INV_ID":        "Inverter",
        "PLANT_LABEL":   "Plant",
        "TOTAL_MWH":     "Total MWh",
        "AVG_EFF":       "Avg Eff (%)",
        "MAX_DAILY_KWH": "Peak Day (kWh)",
    })
    .sort_values(["Plant", "Total MWh"], ascending=[True, False])
    .to_dict("records")
)

layout = html.Div([
    html.Div(className="page-container", children=[

        html.Div(className="page-header", children=[
            html.H1("📈 Yield & Efficiency Tracker", className="page-title"),
            html.P(
                "Cumulative energy production, DC→AC conversion losses and per-inverter production summary",
                className="page-subtitle"
            ),
        ]),

        # Row 1: Cumulative yield + daily efficiency
        html.Div(className="chart-grid chart-grid-2", children=[

            html.Div(className="chart-card", children=[
                html.Div(className="chart-card-header", children=[
                    html.Div([
                        html.Div("Cumulative Energy Yield (MWh)", className="chart-title"),
                        html.Div("Running total of AC energy produced — both plants", className="chart-desc"),
                    ]),
                    html.Span("CUMULATIVE", className="chart-badge badge-solar"),
                ]),
                dcc.Graph(id="cum-yield-chart", config={"displayModeBar": False}, style={"height": "300px"}),
            ]),

            html.Div(className="chart-card", children=[
                html.Div(className="chart-card-header", children=[
                    html.Div([
                        html.Div("DC→AC Conversion Efficiency Over Time", className="chart-title"),
                        html.Div("Plant-level daily average efficiency — losses and anomalies visible", className="chart-desc"),
                    ]),
                    html.Span("EFFICIENCY", className="chart-badge badge-green"),
                ]),
                dcc.Graph(id="eff-chart", config={"displayModeBar": False}, style={"height": "300px"}),
            ]),
        ]),

        # Row 2: DC vs AC gap + peak production heatmap
        html.Div(className="chart-grid chart-grid-2", children=[

            html.Div(className="chart-card", children=[
                html.Div(className="chart-card-header", children=[
                    html.Div([
                        html.Div("Daily DC vs AC Output (Plant 1)", className="chart-title"),
                        html.Div("Gap between DC generated and AC delivered = conversion losses", className="chart-desc"),
                    ]),
                    html.Span("LOSSES", className="chart-badge badge-red"),
                ]),
                dcc.Graph(id="dc-ac-chart", config={"displayModeBar": False}, style={"height": "300px"}),
            ]),

            html.Div(className="chart-card", children=[
                html.Div(className="chart-card-header", children=[
                    html.Div([
                        html.Div("Peak Production Hour Heatmap", className="chart-title"),
                        html.Div("Hour of day × week · brightest = highest output hours", className="chart-desc"),
                    ]),
                    html.Span("HEATMAP", className="chart-badge badge-purple"),
                ]),
                dcc.Graph(id="peak-hour-heatmap", config={"displayModeBar": False}, style={"height": "300px"}),
            ]),
        ]),

        # Row 3: Full-width inverter summary table
        html.Div(className="chart-card", children=[
            html.Div(className="chart-card-header", children=[
                html.Div([
                    html.Div("Inverter Production Summary Table", className="chart-title"),
                    html.Div("Sortable · all inverters ranked by total energy output", className="chart-desc"),
                ]),
                html.Span("SUMMARY", className="chart-badge badge-blue"),
            ]),
            dash_table.DataTable(
                id="inv-summary-table",
                data=_table_data,
                columns=[{"name": c, "id": c} for c in ["Inverter", "Plant", "Total MWh", "Avg Eff (%)", "Peak Day (kWh)"]],
                sort_action="native",
                filter_action="native",
                page_size=15,
                style_table={"overflowX": "auto"},
                style_header={
                    "backgroundColor": "#111d35",
                    "color": "#94a3b8",
                    "fontWeight": "600",
                    "fontSize": "0.72rem",
                    "textTransform": "uppercase",
                    "letterSpacing": "1px",
                    "border": "1px solid #1e3a5f",
                    "fontFamily": "Space Mono, monospace",
                    "padding": "10px 12px",
                },
                style_cell={
                    "backgroundColor": "#0d1628",
                    "color": "#e8f0fe",
                    "border": "1px solid rgba(30,58,95,0.5)",
                    "fontSize": "0.85rem",
                    "padding": "10px 12px",
                    "fontFamily": "Inter, sans-serif",
                },
                style_data_conditional=[
                    {
                        "if": {"filter_query": "{Avg Eff (%)} < 85", "column_id": "Avg Eff (%)"},
                        "color": "#ef4444",
                        "fontWeight": "700",
                    },
                    {
                        "if": {"filter_query": "{Avg Eff (%)} >= 93", "column_id": "Avg Eff (%)"},
                        "color": "#10b981",
                        "fontWeight": "700",
                    },
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "#111d35",
                    },
                ],
            ),
        ]),
    ]),
])


@callback(
    Output("cum-yield-chart",  "figure"),
    Output("eff-chart",        "figure"),
    Output("dc-ac-chart",      "figure"),
    Output("peak-hour-heatmap","figure"),
    Input("cum-yield-chart",   "id"),   # fires on page load
)
def build_charts(_):
    colors = {"Plant 1": SOLAR, "Plant 2": BLUE}

    # ── Cumulative yield ──────────────────────────────────────────────────────
    fig1 = go.Figure()
    for plant, grp in _daily_sorted.groupby("PLANT_LABEL"):
        fig1.add_trace(go.Scatter(
            x=grp["DATE"], y=grp["CUM_MWH"],
            name=plant, mode="lines",
            line=dict(color=colors.get(plant, SOLAR), width=2.5),
            fill="tozeroy",
            fillcolor="rgba(245,158,11,0.08)" if plant == "Plant 1" else "rgba(59,130,246,0.08)",
            hovertemplate="%{x|%d %b}<br>Cumulative: %{y:.1f} MWh<extra>" + plant + "</extra>",
        ))
    fig1.update_layout(**BASE_LAYOUT, margin=dict(l=8, r=8, t=8, b=8),
        yaxis_title="Cumulative MWh",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0),
    )
    fig1.update_xaxes(gridcolor=GRID_COL, zerolinecolor=GRID_COL)
    fig1.update_yaxes(gridcolor=GRID_COL, zerolinecolor=GRID_COL)

    # ── Daily efficiency ──────────────────────────────────────────────────────
    gen_daytime = _gen[_gen["DC_POWER"] > 0].copy()
    daily_eff = gen_daytime.groupby(["DATE", "PLANT_LABEL"], as_index=False).agg(
        AVG_EFF=("EFFICIENCY", "mean")
    )
    daily_eff["DATE"] = pd.to_datetime(daily_eff["DATE"])
    fig2 = go.Figure()
    for plant, grp in daily_eff.groupby("PLANT_LABEL"):
        fig2.add_trace(go.Scatter(
            x=grp["DATE"], y=grp["AVG_EFF"],
            name=plant, mode="lines+markers",
            line=dict(color=colors.get(plant, SOLAR), width=2),
            marker=dict(size=4),
            hovertemplate="%{x|%d %b}<br>Efficiency: %{y:.1f}%<extra>" + plant + "</extra>",
        ))
    fig2.add_hline(y=90, line_dash="dash", line_color="rgba(245,158,11,0.4)",
                   annotation_text="90% baseline", annotation_font_color=SOLAR)
    fig2.update_layout(**BASE_LAYOUT, margin=dict(l=8, r=8, t=8, b=8),
        yaxis_title="Avg Efficiency (%)",
        yaxis_range=[80, 102],
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0),
    )
    fig2.update_xaxes(gridcolor=GRID_COL, zerolinecolor=GRID_COL)
    fig2.update_yaxes(gridcolor=GRID_COL, zerolinecolor=GRID_COL, range=[80, 102])

    # ── DC vs AC (Plant 1) ────────────────────────────────────────────────────
    p1_daily = _daily[_daily["PLANT_LABEL"] == "Plant 1"].copy()
    p1_daily["DATE"] = pd.to_datetime(p1_daily["DATE"])
    p1_daily["DC_MWH"] = p1_daily["TOTAL_DC_KWH"] / 4 / 1000
    p1_daily["AC_MWH"] = p1_daily["TOTAL_AC_KWH"] / 4 / 1000
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=p1_daily["DATE"], y=p1_daily["DC_MWH"],
        name="DC Generated", marker_color=RED, opacity=0.7,
    ))
    fig3.add_trace(go.Bar(
        x=p1_daily["DATE"], y=p1_daily["AC_MWH"],
        name="AC Delivered", marker_color=GREEN, opacity=0.85,
    ))
    fig3.update_layout(**BASE_LAYOUT, margin=dict(l=8, r=8, t=8, b=8),
        yaxis_title="Energy (MWh)", barmode="overlay",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0),
    )
    fig3.update_xaxes(gridcolor=GRID_COL, zerolinecolor=GRID_COL)
    fig3.update_yaxes(gridcolor=GRID_COL, zerolinecolor=GRID_COL)

    # ── Peak hour heatmap ─────────────────────────────────────────────────────
    gen_h = _gen[_gen["AC_POWER"] > 0].copy()
    gen_h["WEEKDAY"] = gen_h["DATE_TIME"].dt.day_name()
    pivot = gen_h.groupby(["HOUR", "WEEKDAY"])["AC_POWER"].mean().unstack(fill_value=0)
    weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    pivot = pivot.reindex(columns=[w for w in weekday_order if w in pivot.columns])

    fig4 = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=[f"{h:02d}:00" for h in pivot.index.tolist()],
        colorscale=[
            [0.0, "#080d1a"],
            [0.3, "#1e3a5f"],
            [0.7, "#b45309"],
            [1.0, "#fde68a"],
        ],
        hovertemplate="Day: %{x}<br>Hour: %{y}<br>Avg AC: %{z:.1f} kW<extra></extra>",
        showscale=True,
        colorbar=dict(thickness=12, tickfont=dict(color=TEXT_COL, size=10), outlinecolor="rgba(0,0,0,0)"),
    ))
    fig4.update_layout(**BASE_LAYOUT, margin=dict(l=60, r=20, t=8, b=30))
    fig4.update_xaxes(tickfont=dict(size=11), gridcolor="rgba(0,0,0,0)")
    fig4.update_yaxes(autorange="reversed", tickfont=dict(size=10), gridcolor="rgba(0,0,0,0)")

    return fig1, fig2, fig3, fig4
