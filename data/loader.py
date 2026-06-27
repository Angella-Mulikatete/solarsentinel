"""
SolarSentinel — Data Loader
Loads, cleans and merges the 4 CSV files from both plants.
Returns ready-to-use DataFrames for each dashboard page.
"""

import os
import pandas as pd
import numpy as np

# ── Paths ────────────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__))

P1_GEN   = os.path.join(DATA_DIR, "Plant_1_Generation_Data.csv")
P1_WX    = os.path.join(DATA_DIR, "Plant_1_Weather_Sensor_Data.csv")
P2_GEN   = os.path.join(DATA_DIR, "Plant_2_Generation_Data.csv")
P2_WX    = os.path.join(DATA_DIR, "Plant_2_Weather_Sensor_Data.csv")


# ── Raw loaders ──────────────────────────────────────────────────────────────

def _load_generation(path: str, plant_label: str) -> pd.DataFrame:
    """Load a generation CSV, parse timestamps, add plant label."""
    df = pd.read_csv(path)
    # Format: "15-05-2020 00:00"
    df["DATE_TIME"] = pd.to_datetime(df["DATE_TIME"], format="%d-%m-%Y %H:%M", errors="coerce")
    df["PLANT_LABEL"] = plant_label
    df = df.dropna(subset=["DATE_TIME"])
    return df


def _load_weather(path: str, plant_label: str) -> pd.DataFrame:
    """Load a weather CSV, parse timestamps, add plant label."""
    df = pd.read_csv(path)
    # Format: "2020-05-15 00:00:00"
    df["DATE_TIME"] = pd.to_datetime(df["DATE_TIME"], errors="coerce")
    df["PLANT_LABEL"] = plant_label
    df = df.dropna(subset=["DATE_TIME"])
    return df


# ── Public loaders ───────────────────────────────────────────────────────────

def load_all_generation() -> pd.DataFrame:
    """Combined generation data for both plants."""
    p1 = _load_generation(P1_GEN, "Plant 1")
    p2 = _load_generation(P2_GEN, "Plant 2")
    df = pd.concat([p1, p2], ignore_index=True)
    df = df.sort_values("DATE_TIME").reset_index(drop=True)

    # Derived columns
    df["DATE"]        = df["DATE_TIME"].dt.date
    df["HOUR"]        = df["DATE_TIME"].dt.hour
    df["EFFICIENCY"]  = np.where(
        df["DC_POWER"] > 0,
        (df["AC_POWER"] / df["DC_POWER"] * 100).clip(0, 105),
        0
    )
    return df


def load_all_weather() -> pd.DataFrame:
    """Combined weather data for both plants."""
    w1 = _load_weather(P1_WX, "Plant 1")
    w2 = _load_weather(P2_WX, "Plant 2")
    df = pd.concat([w1, w2], ignore_index=True)
    df = df.sort_values("DATE_TIME").reset_index(drop=True)
    df["DATE"] = df["DATE_TIME"].dt.date
    df["HOUR"] = df["DATE_TIME"].dt.hour
    return df


def load_merged(plant_label: str | None = None) -> pd.DataFrame:
    """
    Merge generation + weather on DATE_TIME (rounded to 15-min) and plant.
    Optionally filter by plant_label ('Plant 1' or 'Plant 2').
    """
    gen = load_all_generation()
    wx  = load_all_weather()

    # Round weather timestamps to 15-min to match generation intervals
    wx["DATE_TIME"] = wx["DATE_TIME"].dt.floor("15min")
    gen["DATE_TIME"] = gen["DATE_TIME"].dt.floor("15min")

    # Aggregate gen to plant level (sum across inverters) for merging with weather
    gen_plant = (
        gen.groupby(["DATE_TIME", "PLANT_ID", "PLANT_LABEL"], as_index=False)
        .agg(
            TOTAL_AC_POWER   =("AC_POWER",    "sum"),
            TOTAL_DC_POWER   =("DC_POWER",    "sum"),
            AVG_DAILY_YIELD  =("DAILY_YIELD", "mean"),
            TOTAL_DAILY_YIELD=("DAILY_YIELD", "sum"),
            N_INVERTERS      =("SOURCE_KEY",  "nunique"),
        )
    )

    wx_agg = (
        wx.groupby(["DATE_TIME", "PLANT_ID", "PLANT_LABEL"], as_index=False)
        .agg(
            AMBIENT_TEMPERATURE=("AMBIENT_TEMPERATURE", "mean"),
            MODULE_TEMPERATURE =("MODULE_TEMPERATURE",  "mean"),
            IRRADIATION        =("IRRADIATION",         "mean"),
        )
    )

    merged = pd.merge(gen_plant, wx_agg, on=["DATE_TIME", "PLANT_ID", "PLANT_LABEL"], how="inner")
    merged["DATE"] = merged["DATE_TIME"].dt.date
    merged["HOUR"] = merged["DATE_TIME"].dt.hour

    if plant_label:
        merged = merged[merged["PLANT_LABEL"] == plant_label]

    return merged.sort_values("DATE_TIME").reset_index(drop=True)


# ── Pre-computed aggregates ──────────────────────────────────────────────────

def daily_generation(plant_label: str | None = None) -> pd.DataFrame:
    """Daily totals per plant."""
    gen = load_all_generation()
    if plant_label:
        gen = gen[gen["PLANT_LABEL"] == plant_label]

    daily = (
        gen.groupby(["DATE", "PLANT_LABEL"], as_index=False)
        .agg(
            TOTAL_AC_KWH =("AC_POWER",    "sum"),
            TOTAL_DC_KWH =("DC_POWER",    "sum"),
            PEAK_AC_KW   =("AC_POWER",    "max"),
            DAILY_YIELD  =("DAILY_YIELD", "max"),
        )
    )
    daily["DATE"] = pd.to_datetime(daily["DATE"])
    return daily.sort_values("DATE")


def inverter_summary() -> pd.DataFrame:
    """Per-inverter total yield and average efficiency."""
    gen = load_all_generation()
    daytime = gen[gen["AC_POWER"] > 0]

    inv = (
        gen.groupby(["SOURCE_KEY", "PLANT_LABEL", "PLANT_ID"], as_index=False)
        .agg(
            TOTAL_AC_KWH  =("AC_POWER",   "sum"),
            TOTAL_DC_KWH  =("DC_POWER",   "sum"),
            MAX_DAILY_YIELD=("DAILY_YIELD","max"),
            N_READINGS    =("AC_POWER",   "count"),
        )
    )
    eff = (
        daytime.groupby("SOURCE_KEY", as_index=False)
        .agg(AVG_EFFICIENCY=("EFFICIENCY", "mean"))
    )
    inv = inv.merge(eff, on="SOURCE_KEY", how="left")
    inv["AVG_EFFICIENCY"] = inv["AVG_EFFICIENCY"].fillna(0)

    # Short inverter ID (last 8 chars) for display
    inv["INV_ID"] = inv["SOURCE_KEY"].str[-8:]
    return inv


def hourly_profile(plant_label: str | None = None) -> pd.DataFrame:
    """Average AC power by hour-of-day across all days."""
    gen = load_all_generation()
    if plant_label:
        gen = gen[gen["PLANT_LABEL"] == plant_label]

    hourly = (
        gen.groupby(["HOUR", "PLANT_LABEL"], as_index=False)
        .agg(AVG_AC_POWER=("AC_POWER", "mean"))
    )
    return hourly


# ── KPI helpers ──────────────────────────────────────────────────────────────

def get_kpis() -> dict:
    """Top-level KPI numbers for the overview page."""
    gen = load_all_generation()
    daily = daily_generation()

    total_kwh = gen["AC_POWER"].sum() / 4  # 15-min intervals → hours
    peak_kw   = gen["AC_POWER"].max()
    n_inverters = gen["SOURCE_KEY"].nunique()
    n_plants    = gen["PLANT_LABEL"].nunique()
    avg_eff     = gen[gen["DC_POWER"] > 0]["EFFICIENCY"].mean()
    n_days      = gen["DATE"].nunique()

    return {
        "total_mwh"   : round(total_kwh / 1000, 1),
        "peak_kw"     : round(peak_kw, 1),
        "n_inverters" : int(n_inverters),
        "n_plants"    : int(n_plants),
        "avg_eff_pct" : round(avg_eff, 1),
        "n_days"      : int(n_days),
    }
