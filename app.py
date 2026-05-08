#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5G Signal Visualization Dashboard
==================================
An interactive Streamlit web application for visualizing 5G signal measurement data.
Part of the "Code with AI" contest - creating a data dashboard using AI assistance.

Features:
    - Interactive 2D/3D signal strength maps with color-coded RSRP values
    - Real-time sidebar filters for Band and RSRP range selection
    - Data overview charts (Band distribution, Terminal type distribution)
    - 3D column visualization with download rate as height

Author: AI-Assisted Development
Contest: besa-2026/code-with-ai-contest
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

from utils import load_data, get_rsrp_color, get_rsrp_category, prepare_map_data

# ==========================================
# Page Configuration
# ==========================================
st.set_page_config(
    page_title="5G Signal Visualization Dashboard",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# Sidebar Filters
# ==========================================

def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Render sidebar filter controls and return filtered DataFrame.

    Filters include:
        - Multi-select for Band (n28, n41, n78)
        - Range slider for RSRP values
        - Multi-select for Terminal Type
        - Range slider for SINR values

    Args:
        df: Original unfiltered DataFrame.

    Returns:
        Filtered DataFrame based on user selections.
    """
    st.sidebar.header("📊 Filter Controls")
    st.sidebar.markdown("---")

    # Band filter
    available_bands = sorted(df['Band'].unique().tolist())
    selected_bands = st.sidebar.multiselect(
        "Select Frequency Band",
        options=available_bands,
        default=available_bands,
        help="Choose which 5G frequency bands to display"
    )

    st.sidebar.markdown("---")

    # RSRP range slider
    min_rsrp = float(df['RSRP_dBm'].min())
    max_rsrp = float(df['RSRP_dBm'].max())
    rsrp_range = st.sidebar.slider(
        "RSRP Range (dBm)",
        min_value=min_rsrp,
        max_value=max_rsrp,
        value=(min_rsrp, max_rsrp),
        step=1.0,
        help="Filter signal points by RSRP strength range"
    )

    st.sidebar.markdown("---")

    # Terminal type filter
    available_types = sorted(df['TerminalType'].unique().tolist())
    selected_types = st.sidebar.multiselect(
        "Select Terminal Type",
        options=available_types,
        default=available_types,
        help="Choose which terminal device types to display"
    )

    st.sidebar.markdown("---")

    # SINR range slider
    min_sinr = float(df['SINR_dB'].min())
    max_sinr = float(df['SINR_dB'].max())
    sinr_range = st.sidebar.slider(
        "SINR Range (dB)",
        min_value=min_sinr,
        max_value=max_sinr,
        value=(min_sinr, max_sinr),
        step=1.0,
        help="Filter by Signal-to-Interference-plus-Noise Ratio"
    )

    # Apply all filters
    filtered_df = df[
        (df['Band'].isin(selected_bands)) &
        (df['RSRP_dBm'] >= rsrp_range[0]) &
        (df['RSRP_dBm'] <= rsrp_range[1]) &
        (df['TerminalType'].isin(selected_types)) &
        (df['SINR_dB'] >= sinr_range[0]) &
        (df['SINR_dB'] <= sinr_range[1])
    ].copy()

    # Display filter summary
    st.sidebar.markdown("### Filter Summary")
    st.sidebar.info(
        f"**Showing:** {len(filtered_df)} / {len(df)} records\n\n"
        f"**Bands:** {', '.join(selected_bands)}\n\n"
        f"**RSRP:** {rsrp_range[0]:.1f} to {rsrp_range[1]:.1f} dBm\n\n"
        f"**Types:** {', '.join(selected_types)}"
    )

    return filtered_df


# ==========================================
# 2D Map Visualization
# ==========================================

def render_2d_map(df: pd.DataFrame) -> None:
    """
    Render an interactive 2D scatter map using PyDeck.

    Points are color-coded by RSRP signal strength:
        - Green: Excellent signal (>-90dBm)
        - Yellow-Green: Good signal (-90 to -100dBm)
        - Orange: Fair signal (-100 to -110dBm)
        - Red: Poor signal (<=-110dBm)

    Args:
        df: Prepared DataFrame with 'color' column.
    """
    st.subheader("📍 2D Signal Strength Map")

    # Create PyDeck layer
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=df,
        get_position=['Longitude', 'Latitude'],
        get_color='color',
        get_radius=80,
        radius_min_pixels=4,
        radius_max_pixels=30,
        pickable=True,
        opacity=0.8,
    )

    # Tooltip configuration
    tooltip = {
        "html": (
            "<b>Cell ID:</b> {CellID}<br/>"
            "<b>Band:</b> {Band}<br/>"
            "<b>RSRP:</b> {RSRP_dBm} dBm<br/>"
            "<b>SINR:</b> {SINR_dB} dB<br/>"
            "<b>Type:</b> {TerminalType}<br/>"
            "<b>Download:</b> {Download_Mbps} Mbps"
        ),
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }

    # Calculate viewport center
    mid_lat = df['Latitude'].mean()
    mid_lon = df['Longitude'].mean()

    view_state = pdk.ViewState(
        latitude=mid_lat,
        longitude=mid_lon,
        zoom=12,
        pitch=0,
        bearing=0
    )

    # Render the map
    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style='mapbox://styles/mapbox/light-v10'
    )
    st.pydeck_chart(r)


# ==========================================
# 3D Map Visualization
# ==========================================

def render_3d_map(df: pd.DataFrame) -> None:
    """
    Render an interactive 3D column map using PyDeck.

    Signal points are displayed as 3D columns where:
        - Column base position is at the GPS coordinate
        - Column height represents download rate (Download_Mbps)
        - Column color represents RSRP signal strength

    Args:
        df: Prepared DataFrame with 'color' column.
    """
    st.subheader("🗺️ 3D Download Rate Visualization")
    st.markdown("*3D columns show download rate as height, colored by signal strength*")

    # Scale height for better visualization (cap at reasonable values)
    df = df.copy()
    df['height'] = df['Download_Mbps'] * 15  # Scale factor for visibility

    # Create 3D Column layer
    column_layer = pdk.Layer(
        'ColumnLayer',
        data=df,
        get_position=['Longitude', 'Latitude'],
        get_elevation='height',
        elevation_scale=1,
        radius=60,
        get_fill_color='color',
        pickable=True,
        auto_highlight=True,
        extruded=True,
    )

    # Tooltip configuration
    tooltip = {
        "html": (
            "<b>Cell ID:</b> {CellID}<br/>"
            "<b>Band:</b> {Band}<br/>"
            "<b>RSRP:</b> {RSRP_dBm} dBm<br/>"
            "<b>Download:</b> {Download_Mbps} Mbps"
        ),
        "style": {"backgroundColor": "darkslateblue", "color": "white"}
    }

    # Calculate viewport center
    mid_lat = df['Latitude'].mean()
    mid_lon = df['Longitude'].mean()

    view_state = pdk.ViewState(
        latitude=mid_lat,
        longitude=mid_lon,
        zoom=12,
        pitch=50,   # Tilt for 3D perspective
        bearing=0
    )

    # Render the 3D map
    r = pdk.Deck(
        layers=[column_layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style='mapbox://styles/mapbox/dark-v10'
    )
    st.pydeck_chart(r)


# ==========================================
# Data Overview Charts
# ==========================================

def render_data_charts(df: pd.DataFrame) -> None:
    """
    Render overview charts including:
        - Band distribution bar chart
        - Terminal type distribution pie chart
        - RSRP distribution histogram
        - Download rate by Band box plot

    Args:
        df: Filtered DataFrame for visualization.
    """
    st.markdown("---")
    st.subheader("📊 Data Overview")

    # Create two columns for charts
    col1, col2 = st.columns(2)

    # Chart 1: Band distribution (bar chart)
    with col1:
        st.markdown("**Base Station Count by Frequency Band**")
        band_counts = df['Band'].value_counts().sort_index()
        fig_band = px.bar(
            x=band_counts.index,
            y=band_counts.values,
            labels={'x': 'Frequency Band', 'y': 'Count'},
            color=band_counts.index,
            color_discrete_sequence=px.colors.qualitative.Set2,
            text=band_counts.values
        )
        fig_band.update_layout(
            showlegend=False,
            height=350,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig_band, use_container_width=True)

    # Chart 2: Terminal type distribution (pie chart)
    with col2:
        st.markdown("**Terminal Type Distribution**")
        type_counts = df['TerminalType'].value_counts()
        fig_type = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            color=type_counts.index,
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.4
        )
        fig_type.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=30, b=20),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2)
        )
        st.plotly_chart(fig_type, use_container_width=True)

    # Second row of charts
    col3, col4 = st.columns(2)

    # Chart 3: RSRP distribution histogram
    with col3:
        st.markdown("**RSRP Signal Strength Distribution**")
        fig_rsrp = px.histogram(
            df,
            x='RSRP_dBm',
            color='rsrp_category',
            nbins=30,
            labels={'RSRP_dBm': 'RSRP (dBm)', 'count': 'Count'},
            color_discrete_map={
                'Excellent (>-90dBm)': '#00C800',
                'Good (-100 to -90dBm)': '#80C800',
                'Fair (-110 to -100dBm)': '#FFA500',
                'Poor (<=-110dBm)': '#FF0000'
            }
        )
        fig_rsrp.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=30, b=20),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3,
                       title_text='Signal Quality')
        )
        st.plotly_chart(fig_rsrp, use_container_width=True)

    # Chart 4: Download rate by Band (box plot)
    with col4:
        st.markdown("**Download Rate by Frequency Band**")
        fig_download = px.box(
            df,
            x='Band',
            y='Download_Mbps',
            color='Band',
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={'Download_Mbps': 'Download Rate (Mbps)', 'Band': 'Frequency Band'}
        )
        fig_download.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=30, b=20),
            showlegend=False
        )
        st.plotly_chart(fig_download, use_container_width=True)


# ==========================================
# Statistics Panel
# ==========================================

def render_statistics(df: pd.DataFrame) -> None:
    """
    Render key statistics summary cards at the top of the dashboard.

    Args:
        df: Filtered DataFrame.
    """
    st.subheader("📈 Key Metrics")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Points", len(df))

    with col2:
        avg_rsrp = df['RSRP_dBm'].mean()
        st.metric("Avg RSRP", f"{avg_rsrp:.1f} dBm")

    with col3:
        avg_sinr = df['SINR_dB'].mean()
        st.metric("Avg SINR", f"{avg_sinr:.1f} dB")

    with col4:
        avg_download = df['Download_Mbps'].mean()
        st.metric("Avg Download", f"{avg_download:.1f} Mbps")

    with col5:
        unique_bands = df['Band'].nunique()
        st.metric("Bands Used", unique_bands)


# ==========================================
# Legend Component
# ==========================================

def render_legend() -> None:
    """
    Render a color legend explaining the RSRP color coding scheme.
    """
    st.markdown("---")
    st.subheader("🎨 Legend")

    legend_cols = st.columns(4)
    with legend_cols[0]:
        st.markdown("🟢 **Green**: Excellent (>-90dBm)")
    with legend_cols[1]:
        st.markdown("🫒 **Yellow-Green**: Good (-90 to -100dBm)")
    with legend_cols[2]:
        st.markdown("🟠 **Orange**: Fair (-100 to -110dBm)")
    with legend_cols[3]:
        st.markdown("🔴 **Red**: Poor (<=-110dBm)")


# ==========================================
# Data Table
# ==========================================

def render_data_table(df: pd.DataFrame) -> None:
    """
    Render an expandable data table showing filtered results.

    Args:
        df: Filtered DataFrame.
    """
    st.markdown("---")
    with st.expander("📋 View Filtered Data Table"):
        st.dataframe(
            df[[
                'CellID', 'Band', 'Latitude', 'Longitude',
                'RSRP_dBm', 'SINR_dB', 'TerminalType', 'Download_Mbps'
            ]].sort_values('RSRP_dBm', ascending=False),
            use_container_width=True,
            hide_index=True
        )


# ==========================================
# Main Application
# ==========================================

def main() -> None:
    """
    Main entry point for the 5G Signal Visualization Dashboard.

    Orchestrates the complete application flow:
        1. Load data from CSV
        2. Render sidebar filters
        3. Display statistics
        4. Show 2D signal map
        5. Show 3D download rate visualization
        6. Render data overview charts
        7. Show legend and data table
    """
    # Title
    st.title("📡 5G Signal Visualization Dashboard")
    st.markdown(
        "Welcome to the **'Code with AI' Geek Exploration Challenge**! "
        "This interactive dashboard visualizes 5G signal measurement data."
    )
    st.markdown("---")

    # Load data
    try:
        df = load_data("data/signal_samples.csv")
    except FileNotFoundError:
        st.error("❌ Data file not found. Please ensure `data/signal_samples.csv` exists.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.stop()

    # Sidebar filters
    filtered_df = render_sidebar_filters(df)

    # Check if any data remains after filtering
    if len(filtered_df) == 0:
        st.warning("⚠️ No data points match the current filter criteria. Please adjust your filters.")
        st.stop()

    # Prepare data with colors
    display_df = prepare_map_data(filtered_df)

    # Statistics panel
    render_statistics(display_df)

    st.markdown("---")

    # 2D Map
    render_2d_map(display_df)

    st.markdown("---")

    # 3D Map
    render_3d_map(display_df)

    # Data overview charts
    render_data_charts(display_df)

    # Legend
    render_legend()

    # Data table
    render_data_table(display_df)

    # Footer
    st.markdown("---")
    st.caption(
        "🚀 Built with Streamlit + PyDeck + Plotly | "
        "Contest: besa-2026/code-with-ai-contest | "
        "Data: Simulated 5G Drive Test Measurements"
    )


if __name__ == "__main__":
    main()
