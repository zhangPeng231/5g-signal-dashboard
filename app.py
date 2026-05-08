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
    - Signal quality analysis with multiple chart types
    - 3D column visualization with download rate as height

Author: AI-Assisted Development
Contest: besa-2026/code-with-ai-contest
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
# Custom CSS for Better Styling
# ==========================================
st.markdown("""
<style>
    /* Metric cards styling */
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        color: #888 !important;
    }
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1a1a2e;
    }
    /* Better tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #0e1117;
        border-radius: 8px 8px 0 0;
        padding: 10px 24px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #262730 !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# Sidebar Filters
# ==========================================

def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Render sidebar filter controls and return filtered DataFrame.

    Args:
        df: Original unfiltered DataFrame.

    Returns:
        Filtered DataFrame based on user selections.
    """
    st.sidebar.header("🔧 Filter Controls")
    st.sidebar.markdown("---")

    # Band filter with icons
    available_bands = sorted(df['Band'].unique().tolist())
    selected_bands = st.sidebar.multiselect(
        "📶 Frequency Band",
        options=available_bands,
        default=available_bands,
        help="Filter by 5G NR frequency bands"
    )

    # RSRP range slider
    min_rsrp = float(df['RSRP_dBm'].min())
    max_rsrp = float(df['RSRP_dBm'].max())
    rsrp_range = st.sidebar.slider(
        "📡 RSRP Range (dBm)",
        min_value=min_rsrp,
        max_value=max_rsrp,
        value=(min_rsrp, max_rsrp),
        step=1.0,
        help="Reference Signal Received Power range"
    )

    # Terminal type filter
    available_types = sorted(df['TerminalType'].unique().tolist())
    selected_types = st.sidebar.multiselect(
        "📱 Terminal Type",
        options=available_types,
        default=available_types,
        help="Filter by device type"
    )

    # SINR range slider
    min_sinr = float(df['SINR_dB'].min())
    max_sinr = float(df['SINR_dB'].max())
    sinr_range = st.sidebar.slider(
        "📊 SINR Range (dB)",
        min_value=min_sinr,
        max_value=max_sinr,
        value=(min_sinr, max_sinr),
        step=1.0,
        help="Signal-to-Interference-plus-Noise Ratio"
    )

    # Download speed slider
    min_dl = float(df['Download_Mbps'].min())
    max_dl = float(df['Download_Mbps'].max())
    dl_range = st.sidebar.slider(
        "⬇️ Download Speed (Mbps)",
        min_value=min_dl,
        max_value=max_dl,
        value=(min_dl, max_dl),
        step=10.0,
        help="Filter by download speed range"
    )

    # Apply all filters
    filtered_df = df[
        (df['Band'].isin(selected_bands)) &
        (df['RSRP_dBm'] >= rsrp_range[0]) &
        (df['RSRP_dBm'] <= rsrp_range[1]) &
        (df['TerminalType'].isin(selected_types)) &
        (df['SINR_dB'] >= sinr_range[0]) &
        (df['SINR_dB'] <= sinr_range[1]) &
        (df['Download_Mbps'] >= dl_range[0]) &
        (df['Download_Mbps'] <= dl_range[1])
    ].copy()

    # Filter summary with progress bar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 Filter Summary")
    ratio = len(filtered_df) / len(df) if len(df) > 0 else 0
    st.sidebar.progress(ratio, text=f"**{len(filtered_df)}** / {len(df)} records ({ratio*100:.1f}%)")

    return filtered_df


# ==========================================
# Statistics Panel with HTML Cards
# ==========================================

def render_statistics(df: pd.DataFrame) -> None:
    """
    Render key statistics summary cards with enhanced styling.

    Args:
        df: Filtered DataFrame.
    """
    # Calculate statistics
    total = len(df)
    avg_rsrp = df['RSRP_dBm'].mean()
    avg_sinr = df['SINR_dB'].mean()
    avg_dl = df['Download_Mbps'].mean()
    max_dl = df['Download_Mbps'].max()
    unique_cells = df['CellID'].nunique()

    # Color code the RSRP metric
    if avg_rsrp > -90:
        rsrp_color = "#00C853"
    elif avg_rsrp > -100:
        rsrp_color = "#AEEA00"
    elif avg_rsrp > -110:
        rsrp_color = "#FFD600"
    else:
        rsrp_color = "#FF1744"

    cols = st.columns(6)
    metrics = [
        ("📊 Total Points", f"{total}", "#2196F3"),
        ("📡 Avg RSRP", f"{avg_rsrp:.1f} dBm", rsrp_color),
        ("📈 Avg SINR", f"{avg_sinr:.1f} dB", "#00BCD4"),
        ("⬇️ Avg Download", f"{avg_dl:.0f} Mbps", "#9C27B0"),
        ("🚀 Max Download", f"{max_dl:.0f} Mbps", "#FF9800"),
        ("🏠 Unique Cells", f"{unique_cells}", "#795548"),
    ]

    for col, (label, value, color) in zip(cols, metrics):
        with col:
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, {color}22, {color}11);
                    border-left: 4px solid {color};
                    border-radius: 8px;
                    padding: 12px 16px;
                    margin-bottom: 8px;
                ">
                    <p style="margin:0; font-size:0.75rem; color:#888; font-weight:600;">{label}</p>
                    <p style="margin:0; font-size:1.4rem; font-weight:700; color:{color};">{value}</p>
                </div>
            """, unsafe_allow_html=True)


# ==========================================
# Map Visualization with Tabs
# ==========================================

def render_map_section(df: pd.DataFrame) -> None:
    """
    Render map section with 2D/3D tab switching.

    Args:
        df: Prepared DataFrame with 'color' column.
    """
    tab1, tab2 = st.tabs(["📍 2D Signal Map", "🗺️ 3D Download Rate View"])

    with tab1:
        render_2d_map(df)

    with tab2:
        render_3d_map(df)


def render_2d_map(df: pd.DataFrame) -> None:
    """
    Render an interactive 2D scatter map using PyDeck.

    Args:
        df: Prepared DataFrame with 'color' column.
    """
    col_left, col_right = st.columns([3, 1])

    with col_left:
        # Create PyDeck HeatmapLayer + ScatterplotLayer
        scatter_layer = pdk.Layer(
            'ScatterplotLayer',
            data=df,
            get_position=['Longitude', 'Latitude'],
            get_color='color',
            get_radius=90,
            radius_min_pixels=3,
            radius_max_pixels=35,
            pickable=True,
            opacity=0.85,
        )

        tooltip = {
            "html": (
                "<div style='font-family: Arial; padding: 4px;'>"
                "<b style='color:#FFD600;'>📡 Cell {CellID}</b><br/>"
                "<b>Band:</b> {Band}<br/>"
                "<b>RSRP:</b> {RSRP_dBm} dBm<br/>"
                "<b>SINR:</b> {SINR_dB} dB<br/>"
                "<b>Type:</b> {TerminalType}<br/>"
                "<b>Download:</b> {Download_Mbps} Mbps<br/>"
                "<b>Quality:</b> {rsrp_category}"
                "</div>"
            ),
            "style": {
                "backgroundColor": "#1a1a2e",
                "color": "#ffffff",
                "borderRadius": "8px",
                "padding": "10px",
                "border": "1px solid #333"
            }
        }

        view_state = pdk.ViewState(
            latitude=df['Latitude'].mean(),
            longitude=df['Longitude'].mean(),
            zoom=12,
            pitch=0,
            bearing=0
        )

        r = pdk.Deck(
            layers=[scatter_layer],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style='mapbox://styles/mapbox/dark-v10'
        )
        st.pydeck_chart(r)

    with col_right:
        st.markdown("### Signal Quality")
        quality_counts = df['rsrp_category'].value_counts()
        quality_colors = {
            'Excellent (>-90dBm)': '#00C853',
            'Good (-100 to -90dBm)': '#AEEA00',
            'Fair (-110 to -100dBm)': '#FFD600',
            'Poor (<=-110dBm)': '#FF1744'
        }

        fig_pie = go.Figure(data=[go.Pie(
            labels=quality_counts.index,
            values=quality_counts.values,
            hole=0.55,
            marker_colors=[quality_colors.get(q, '#888') for q in quality_counts.index],
            textinfo='percent',
            textfont_size=10,
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Ratio: %{percent}<extra></extra>'
        )])

        fig_pie.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05,
                font=dict(size=9, color='#ccc'),
                bgcolor='rgba(0,0,0,0)'
            ),
            annotations=[dict(text=f'<b>{len(df)}</b><br>points', x=0.5, y=0.5,
                            font_size=14, showarrow=False, font_color='#fff')]
        )

        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})


def render_3d_map(df: pd.DataFrame) -> None:
    """
    Render an interactive 3D column map using PyDeck.

    Args:
        df: Prepared DataFrame with 'color' column.
    """
    st.markdown("*3D columns show download rate as height, colored by RSRP signal strength*")

    df = df.copy()
    df['height'] = df['Download_Mbps'] * 12

    column_layer = pdk.Layer(
        'ColumnLayer',
        data=df,
        get_position=['Longitude', 'Latitude'],
        get_elevation='height',
        elevation_scale=1,
        radius=55,
        get_fill_color='color',
        pickable=True,
        auto_highlight=True,
        extruded=True,
    )

    tooltip = {
        "html": (
            "<div style='font-family: Arial;'>"
            "<b style='color:#FFD600;'>📡 Cell {CellID}</b><br/>"
            "<b>Band:</b> {Band} | <b>RSRP:</b> {RSRP_dBm} dBm<br/>"
            "<b>Download:</b> {Download_Mbps} Mbps"
            "</div>"
        ),
        "style": {
            "backgroundColor": "#1a1a2e",
            "color": "#ffffff",
            "borderRadius": "8px",
            "padding": "10px"
        }
    }

    view_state = pdk.ViewState(
        latitude=df['Latitude'].mean(),
        longitude=df['Longitude'].mean(),
        zoom=12,
        pitch=55,
        bearing=-10
    )

    r = pdk.Deck(
        layers=[column_layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style='mapbox://styles/mapbox/dark-v10'
    )
    st.pydeck_chart(r)


# ==========================================
# Signal Quality Analysis Charts
# ==========================================

def render_signal_quality_analysis(df: pd.DataFrame) -> None:
    """
    Render signal quality analysis charts.

    Args:
        df: Filtered DataFrame for visualization.
    """
    st.markdown("---")
    st.subheader("📊 Signal Quality Analysis")

    col1, col2 = st.columns(2)

    # Chart 1: RSRP Distribution by Band (grouped histogram)
    with col1:
        st.markdown("**📡 RSRP Distribution by Frequency Band**")
        fig_rsrp = px.histogram(
            df,
            x='RSRP_dBm',
            color='Band',
            nbins=25,
            labels={'RSRP_dBm': 'RSRP (dBm)', 'count': 'Count'},
            color_discrete_sequence=['#00BCD4', '#FF9800', '#E91E63'],
            opacity=0.8,
            barmode='group'
        )
        fig_rsrp.update_layout(
            height=340,
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=-0.2,
                       title_text='Band', font=dict(color='#ccc')),
            xaxis=dict(gridcolor='#333', tickfont=dict(color='#aaa'),
                      titlefont=dict(color='#ccc')),
            yaxis=dict(gridcolor='#333', tickfont=dict(color='#aaa'),
                      titlefont=dict(color='#ccc')),
        )
        st.plotly_chart(fig_rsrp, use_container_width=True, config={'displayModeBar': False})

    # Chart 2: RSRP vs SINR Scatter (colored by Band)
    with col2:
        st.markdown("**📈 RSRP vs SINR Correlation**")
        fig_scatter = px.scatter(
            df,
            x='RSRP_dBm',
            y='SINR_dB',
            color='Band',
            size='Download_Mbps',
            size_max=15,
            labels={'RSRP_dBm': 'RSRP (dBm)', 'SINR_dB': 'SINR (dB)'},
            color_discrete_sequence=['#00BCD4', '#FF9800', '#E91E63'],
            opacity=0.7,
            hover_data=['CellID', 'TerminalType', 'Download_Mbps']
        )
        fig_scatter.update_layout(
            height=340,
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=-0.2,
                       title_text='Band', font=dict(color='#ccc')),
            xaxis=dict(gridcolor='#333', tickfont=dict(color='#aaa'),
                      titlefont=dict(color='#ccc')),
            yaxis=dict(gridcolor='#333', tickfont=dict(color='#aaa'),
                      titlefont=dict(color='#ccc')),
        )
        st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})

    col3, col4 = st.columns(2)

    # Chart 3: Download Rate Distribution (violin plot)
    with col3:
        st.markdown("**⬇️ Download Rate Distribution by Band**")
        fig_violin = px.violin(
            df,
            x='Band',
            y='Download_Mbps',
            color='Band',
            box=True,
            points=False,
            labels={'Download_Mbps': 'Download Rate (Mbps)'},
            color_discrete_sequence=['#00BCD4', '#FF9800', '#E91E63'],
        )
        fig_violin.update_layout(
            height=340,
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis=dict(gridcolor='#333', tickfont=dict(color='#aaa'),
                      titlefont=dict(color='#ccc')),
            yaxis=dict(gridcolor='#333', tickfont=dict(color='#aaa'),
                      titlefont=dict(color='#ccc')),
        )
        st.plotly_chart(fig_violin, use_container_width=True, config={'displayModeBar': False})

    # Chart 4: Terminal Type Performance Radar-style Bar
    with col4:
        st.markdown("**📱 Terminal Performance Overview**")
        terminal_stats = df.groupby('TerminalType').agg({
            'RSRP_dBm': 'mean',
            'SINR_dB': 'mean',
            'Download_Mbps': 'mean'
        }).round(1).reset_index()

        fig_term = go.Figure()

        colors = ['#00BCD4', '#FF9800', '#E91E63']
        for i, col in enumerate(['RSRP_dBm', 'SINR_dB', 'Download_Mbps']):
            fig_term.add_trace(go.Bar(
                name=col,
                x=terminal_stats['TerminalType'],
                y=terminal_stats[col],
                marker_color=colors[i],
                opacity=0.85,
                text=terminal_stats[col],
                textposition='outside',
                textfont=dict(size=10)
            ))

        fig_term.update_layout(
            height=340,
            barmode='group',
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=-0.25,
                       title_text='', font=dict(color='#ccc')),
            xaxis=dict(gridcolor='#333', tickfont=dict(color='#aaa'),
                      titlefont=dict(color='#ccc')),
            yaxis=dict(gridcolor='#333', tickfont=dict(color='#aaa'),
                      titlefont=dict(color='#ccc'), title='Value'),
        )
        st.plotly_chart(fig_term, use_container_width=True, config={'displayModeBar': False})


# ==========================================
# Band Analysis Section
# ==========================================

def render_band_analysis(df: pd.DataFrame) -> None:
    """
    Render band comparison analysis.

    Args:
        df: Filtered DataFrame.
    """
    st.markdown("---")
    st.subheader("📶 Frequency Band Comparison")

    # Create band summary table
    band_summary = df.groupby('Band').agg({
        'RSRP_dBm': ['mean', 'min', 'max'],
        'SINR_dB': ['mean', 'min', 'max'],
        'Download_Mbps': ['mean', 'min', 'max'],
        'CellID': 'count'
    }).round(1)

    band_summary.columns = ['Avg RSRP', 'Min RSRP', 'Max RSRP',
                            'Avg SINR', 'Min SINR', 'Max SINR',
                            'Avg Download', 'Min Download', 'Max Download',
                            'Count']
    band_summary = band_summary.reset_index()

    # Use columns to show table and chart side by side
    col_table, col_chart = st.columns([3, 2])

    with col_table:
        st.markdown("**Band Statistics Summary**")
        st.dataframe(
            band_summary,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Band': st.column_config.TextColumn('Band', width='small'),
                'Count': st.column_config.NumberColumn('Points', width='small'),
                'Avg RSRP': st.column_config.NumberColumn('Avg RSRP (dBm)', format='%.1f'),
                'Avg SINR': st.column_config.NumberColumn('Avg SINR (dB)', format='%.1f'),
                'Avg Download': st.column_config.NumberColumn('Avg DL (Mbps)', format='%.0f'),
            }
        )

    with col_chart:
        st.markdown("**Band Usage Distribution**")
        band_counts = df['Band'].value_counts().sort_index()

        fig_band = go.Figure(data=[go.Pie(
            labels=band_counts.index,
            values=band_counts.values,
            hole=0.4,
            marker_colors=['#00BCD4', '#FF9800', '#E91E63'],
            textinfo='label+percent',
            textfont_size=12,
            hovertemplate='<b>%{label}</b><br>Points: %{value}<br>Ratio: %{percent}<extra></extra>'
        )])

        fig_band.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            annotations=[dict(text='Bands', x=0.5, y=0.5,
                            font_size=14, showarrow=False, font_color='#fff')]
        )
        st.plotly_chart(fig_band, use_container_width=True, config={'displayModeBar': False})


# ==========================================
# Data Table Section
# ==========================================

def render_data_table(df: pd.DataFrame) -> None:
    """
    Render an enhanced data table with conditional styling.

    Args:
        df: Filtered DataFrame.
    """
    st.markdown("---")
    with st.expander("📋 View Detailed Data Table"):
        # Show sorted dataframe
        display_df = df[[
            'CellID', 'Band', 'Latitude', 'Longitude',
            'RSRP_dBm', 'SINR_dB', 'TerminalType', 'Download_Mbps', 'rsrp_category'
        ]].sort_values('RSRP_dBm', ascending=False)

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'CellID': st.column_config.NumberColumn('Cell ID', width='small'),
                'Band': st.column_config.TextColumn('Band', width='small'),
                'RSRP_dBm': st.column_config.NumberColumn('RSRP (dBm)', format='%.1f'),
                'SINR_dB': st.column_config.NumberColumn('SINR (dB)', format='%.1f'),
                'Download_Mbps': st.column_config.NumberColumn('Download (Mbps)', format='%.1f'),
                'rsrp_category': st.column_config.TextColumn('Quality'),
            }
        )

        # Export option
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name='filtered_5g_data.csv',
            mime='text/csv',
        )


# ==========================================
# Main Application
# ==========================================

def main() -> None:
    """
    Main entry point for the 5G Signal Visualization Dashboard.
    """
    # Title with custom styling
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 20px 0;">
            <h1 style="margin:0; font-size: 2.2rem; color: #00BCD4;">📡 5G Signal Visualization Dashboard</h1>
            <p style="margin:8px 0 0 0; color: #888; font-size: 0.95rem;">
                Interactive analysis of 5G drive test measurements | 
                <b style="color:#FF9800;">Code with AI</b> Contest
            </p>
        </div>
    """, unsafe_allow_html=True)
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

    # Map section with 2D/3D tabs
    render_map_section(display_df)

    # Signal quality analysis charts
    render_signal_quality_analysis(display_df)

    # Band comparison analysis
    render_band_analysis(display_df)

    # Data table with export
    render_data_table(display_df)

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #555; font-size: 0.8rem; padding: 10px 0;">
            🚀 Built with <b>Streamlit</b> + <b>PyDeck</b> + <b>Plotly</b> | 
            Contest: <a href="https://github.com/besa-2026/code-with-ai-contest" style="color:#00BCD4;">besa-2026/code-with-ai-contest</a> | 
            Data: Simulated 5G Drive Test Measurements
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
