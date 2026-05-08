#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility Functions for 5G Signal Visualization Dashboard
========================================================
Core utility functions separated from Streamlit UI code for testability.

This module contains pure Python functions for:
    - Data loading and validation
    - RSRP color mapping
    - Data preparation for visualization
"""

import pandas as pd


def load_data(filepath: str) -> pd.DataFrame:
    """
    Load 5G signal measurement data from a CSV file.

    Args:
        filepath: Path to the CSV file containing signal data.

    Returns:
        DataFrame with columns: Latitude, Longitude, CellID, Band,
        RSRP_dBm, SINR_dB, TerminalType, Download_Mbps

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If required columns are missing from the data.
    """
    df = pd.read_csv(filepath)
    # Validate expected columns exist
    expected_cols = ['Latitude', 'Longitude', 'CellID', 'Band',
                     'RSRP_dBm', 'SINR_dB', 'TerminalType', 'Download_Mbps']
    missing = [col for col in expected_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")
    return df


def get_rsrp_color(rsrp: float) -> list:
    """
    Convert RSRP value to RGB color for map visualization.

    Color coding scheme:
        - RSRP > -90 dBm      : Green [0, 200, 0] (Excellent signal)
        - -90 >= RSRP > -100  : Yellow-Green [128, 200, 0] (Good signal)
        - -100 >= RSRP > -110 : Orange [255, 165, 0] (Fair signal)
        - RSRP <= -110 dBm   : Red [255, 0, 0] (Poor signal)

    Args:
        rsrp: Signal strength in dBm.

    Returns:
        List of [R, G, B] integer values (0-255).
    """
    if rsrp > -90:
        return [0, 200, 0]      # Green - Excellent
    elif rsrp > -100:
        return [128, 200, 0]    # Yellow-Green - Good
    elif rsrp > -110:
        return [255, 165, 0]    # Orange - Fair
    else:
        return [255, 0, 0]      # Red - Poor


def get_rsrp_category(rsrp: float) -> str:
    """
    Classify RSRP value into signal quality category.

    Args:
        rsrp: Signal strength in dBm.

    Returns:
        Human-readable signal quality string.
    """
    if rsrp > -90:
        return "Excellent (>-90dBm)"
    elif rsrp > -100:
        return "Good (-100 to -90dBm)"
    elif rsrp > -110:
        return "Fair (-110 to -100dBm)"
    else:
        return "Poor (<=-110dBm)"


def prepare_map_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare data for map visualization by adding color and category columns.

    Args:
        df: Raw signal DataFrame.

    Returns:
        DataFrame with additional 'color' and 'rsrp_category' columns.
    """
    df = df.copy()
    df['color'] = df['RSRP_dBm'].apply(get_rsrp_color)
    df['rsrp_category'] = df['RSRP_dBm'].apply(get_rsrp_category)
    return df
