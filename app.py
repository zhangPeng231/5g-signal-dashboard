#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5G 信号可视化看板
==================
基于 Streamlit + PyDeck + Plotly 的交互式 5G 路测数据可视化应用。
"Code with AI" 极客探索赛参赛作品。

功能特性：
    - 交互式 2D/3D 信号强度地图（RSRP 四色编码）
    - 左侧边栏实时联动筛选器
    - 信号质量多维度分析图表
    - 3D 柱状图（高度随下载速率变化）
    - 数据导出功能

作者：AI 辅助开发
比赛：besa-2026/code-with-ai-contest
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go

from utils import load_data, get_rsrp_color, get_rsrp_category, prepare_map_data

# ==========================================
# 页面配置
# ==========================================
st.set_page_config(
    page_title="5G 信号可视化看板",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 自定义 CSS 样式 - 科技蓝风格
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* 主标题样式 */
    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* 卡片阴影效果 */
    .stMetric {
        background: linear-gradient(145deg, #1e1e2f, #252540) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }
    
    /* 指标数值 */
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* 指标标签 */
    div[data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        color: #8892b0 !important;
        font-weight: 500 !important;
    }
    
    /* 侧边栏 */
    .css-1d391kg, section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    
    /* 按钮样式 */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Tab 样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(30, 30, 47, 0.5);
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        color: #8892b0;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
    }
    
    /* 表格样式 */
    .dataframe {
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    
    /* 分割线 */
    hr {
        border-color: rgba(102, 126, 234, 0.2) !important;
        margin: 2rem 0 !important;
    }
    
    /* 展开器 */
    .streamlit-expanderHeader {
        background: linear-gradient(145deg, #1e1e2f, #252540) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 侧边栏筛选器
# ==========================================

def render_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    渲染侧边栏筛选控件，返回筛选后的 DataFrame。
    
    包含以下筛选器：
        - 频段多选框 (Band)
        - RSRP 范围滑动条
        - 终端类型多选框
        - SINR 范围滑动条
        - 下载速率范围滑动条
    
    参数:
        df: 原始未筛选的 DataFrame。
    
    返回:
        根据用户选择筛选后的 DataFrame。
    """
    st.sidebar.markdown("""
        <div style="text-align: center; padding: 10px 0;">
            <h2 style="margin:0; color: #667eea; font-size: 1.3rem;">🔧 筛选控制台</h2>
            <p style="margin:4px 0 0 0; color: #8892b0; font-size: 0.75rem;">实时联动筛选数据</p>
        </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")

    # 频段筛选
    available_bands = sorted(df['Band'].unique().tolist())
    selected_bands = st.sidebar.multiselect(
        "📶 频段 (Band)",
        options=available_bands,
        default=available_bands,
        help="选择要显示的 5G 频段"
    )

    # RSRP 范围
    min_rsrp = float(df['RSRP_dBm'].min())
    max_rsrp = float(df['RSRP_dBm'].max())
    rsrp_range = st.sidebar.slider(
        "📡 RSRP 范围 (dBm)",
        min_value=min_rsrp,
        max_value=max_rsrp,
        value=(min_rsrp, max_rsrp),
        step=1.0,
        help="参考信号接收功率范围"
    )

    # 终端类型
    available_types = sorted(df['TerminalType'].unique().tolist())
    selected_types = st.sidebar.multiselect(
        "📱 终端类型",
        options=available_types,
        default=available_types,
        help="选择终端设备类型"
    )

    # SINR 范围
    min_sinr = float(df['SINR_dB'].min())
    max_sinr = float(df['SINR_dB'].max())
    sinr_range = st.sidebar.slider(
        "📊 SINR 范围 (dB)",
        min_value=min_sinr,
        max_value=max_sinr,
        value=(min_sinr, max_sinr),
        step=1.0,
        help="信噪比范围"
    )

    # 下载速率范围
    min_dl = float(df['Download_Mbps'].min())
    max_dl = float(df['Download_Mbps'].max())
    dl_range = st.sidebar.slider(
        "⬇️ 下载速率 (Mbps)",
        min_value=min_dl,
        max_value=max_dl,
        value=(min_dl, max_dl),
        step=10.0,
        help="下载速率范围筛选"
    )

    # 应用所有筛选条件
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

    # 筛选摘要
    st.sidebar.markdown("---")
    ratio = len(filtered_df) / len(df) if len(df) > 0 else 0
    st.sidebar.markdown(f"""
        <div style="
            background: linear-gradient(145deg, #1e1e2f, #252540);
            border-radius: 12px;
            padding: 16px;
            border: 1px solid rgba(102, 126, 234, 0.3);
        ">
            <p style="margin:0 0 8px 0; color:#8892b0; font-size:0.8rem; font-weight:600;">📋 筛选结果</p>
            <p style="margin:0; font-size:1.2rem; font-weight:700; color:#667eea;">
                {len(filtered_df)} <span style="color:#8892b0; font-size:0.85rem;">/ {len(df)} 条</span>
            </p>
            <div style="margin-top:8px; background:#1a1a2e; border-radius:6px; height:6px;">
                <div style="width:{ratio*100}%; background:linear-gradient(90deg, #667eea, #764ba2); 
                            height:100%; border-radius:6px; transition:width 0.3s;"></div>
            </div>
            <p style="margin:4px 0 0 0; color:#8892b0; font-size:0.7rem; text-align:right;">{ratio*100:.1f}%</p>
        </div>
    """, unsafe_allow_html=True)

    return filtered_df


# ==========================================
# 统计指标面板
# ==========================================

def render_statistics(df: pd.DataFrame) -> None:
    """
    渲染顶部统计指标卡片。
    
    参数:
        df: 筛选后的 DataFrame。
    """
    avg_rsrp = df['RSRP_dBm'].mean()
    avg_sinr = df['SINR_dB'].mean()
    avg_dl = df['Download_Mbps'].mean()
    max_dl = df['Download_Mbps'].max()
    unique_cells = df['CellID'].nunique()

    # RSRP 颜色编码
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
        ("📊 数据点数", f"{len(df)}", "#667eea"),
        ("📡 平均 RSRP", f"{avg_rsrp:.1f} dBm", rsrp_color),
        ("📈 平均 SINR", f"{avg_sinr:.1f} dB", "#00BCD4"),
        ("⬇️ 平均下载", f"{avg_dl:.0f} Mbps", "#9C27B0"),
        ("🚀 最高下载", f"{max_dl:.0f} Mbps", "#FF9800"),
        ("🏠 小区数量", f"{unique_cells}", "#795548"),
    ]

    for col, (label, value, color) in zip(cols, metrics):
        with col:
            st.markdown(f"""
                <div style="
                    background: linear-gradient(145deg, #1e1e2f, #252540);
                    border-radius: 12px;
                    padding: 14px;
                    border-left: 4px solid {color};
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                    transition: transform 0.2s;
                " onmouseover="this.style.transform='translateY(-2px)'" 
                   onmouseout="this.style.transform='translateY(0)'">
                    <p style="margin:0 0 4px 0; font-size:0.7rem; color:#8892b0; font-weight:500;">{label}</p>
                    <p style="margin:0; font-size:1.3rem; font-weight:700; color:{color};">{value}</p>
                </div>
            """, unsafe_allow_html=True)


# ==========================================
# 地图可视化（2D/3D 标签页）
# ==========================================

def render_map_section(df: pd.DataFrame) -> None:
    """
    渲染地图区域，支持 2D/3D 标签页切换。
    
    参数:
        df: 带颜色列的 DataFrame。
    """
    tab1, tab2 = st.tabs(["📍 2D 信号地图", "🗺️ 3D 速率视图"])

    with tab1:
        render_2d_map(df)
    with tab2:
        render_3d_map(df)


def render_2d_map(df: pd.DataFrame) -> None:
    """
    渲染 2D 散点地图 + 信号质量饼图。
    
    参数:
        df: 带颜色列的 DataFrame。
    """
    col_left, col_right = st.columns([3, 1])

    with col_left:
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
                "<div style='font-family:Inter,system-ui;padding:8px 12px;'>"
                "<b style='color:#667eea;font-size:1.1em;'>📡 Cell {CellID}</b><br/>"
                "<hr style='border-color:#333;margin:4px 0;'/>"
                "<b>频段:</b> {Band}<br/>"
                "<b>RSRP:</b> {RSRP_dBm} dBm<br/>"
                "<b>SINR:</b> {SINR_dB} dB<br/>"
                "<b>终端:</b> {TerminalType}<br/>"
                "<b>下载:</b> {Download_Mbps} Mbps"
                "</div>"
            ),
            "style": {
                "backgroundColor": "#0f172a",
                "color": "#e2e8f0",
                "borderRadius": "10px",
                "padding": "0",
                "border": "1px solid rgba(102,126,234,0.3)",
                "fontSize": "13px"
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
        st.markdown("**信号质量分布**")
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
            hovertemplate='<b>%{label}</b><br>数量: %{value}<br>占比: %{percent}<extra></extra>'
        )])

        fig_pie.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(
                orientation="v", yanchor="middle", y=0.5,
                xanchor="left", x=1.02,
                font=dict(size=9, color='#94a3b8'),
                bgcolor='rgba(0,0,0,0)'
            ),
            annotations=[dict(
                text=f'<b>{len(df)}</b><br>个点',
                x=0.5, y=0.5, font_size=14,
                showarrow=False, font_color='#e2e8f0'
            )]
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})


def render_3d_map(df: pd.DataFrame) -> None:
    """
    渲染 3D 柱状图地图。
    
    参数:
        df: 带颜色列的 DataFrame。
    """
    st.markdown("<p style='color:#8892b0;font-size:0.85rem;'>3D 柱子高度代表下载速率，颜色代表信号强度</p>",
                unsafe_allow_html=True)

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
            "<div style='font-family:system-ui;padding:8px;'>"
            "<b style='color:#667eea;'>📡 Cell {CellID}</b><br/>"
            "<b>频段:</b> {Band} | <b>RSRP:</b> {RSRP_dBm} dBm<br/>"
            "<b>下载:</b> {Download_Mbps} Mbps"
            "</div>"
        ),
        "style": {
            "backgroundColor": "#0f172a",
            "color": "#e2e8f0",
            "borderRadius": "10px",
            "border": "1px solid rgba(102,126,234,0.3)"
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
# 信号质量分析图表
# ==========================================

def render_signal_quality_analysis(df: pd.DataFrame) -> None:
    """
    渲染信号质量分析图表区域。
    
    参数:
        df: 筛选后的 DataFrame。
    """
    st.markdown("---")
    st.markdown("<h3 style='color:#e2e8f0;'>📊 信号质量深度分析</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<p style='color:#8892b0;font-size:0.9rem;'>📡 各频段 RSRP 分布</p>", unsafe_allow_html=True)
        fig_rsrp = px.histogram(
            df, x='RSRP_dBm', color='Band', nbins=25,
            labels={'RSRP_dBm': 'RSRP (dBm)', 'count': '数量'},
            color_discrete_sequence=['#667eea', '#f093fb', '#4facfe'],
            opacity=0.8, barmode='group'
        )
        fig_rsrp.update_layout(
            height=340,
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=-0.2,
                       title_text='频段', font=dict(color='#94a3b8')),
            xaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8'),
                      titlefont=dict(color='#e2e8f0')),
            yaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8'),
                      titlefont=dict(color='#e2e8f0')),
        )
        st.plotly_chart(fig_rsrp, use_container_width=True, config={'displayModeBar': False})

    with col2:
        st.markdown("<p style='color:#8892b0;font-size:0.9rem;'>📈 RSRP 与 SINR 相关性分析</p>", unsafe_allow_html=True)
        fig_scatter = px.scatter(
            df, x='RSRP_dBm', y='SINR_dB', color='Band',
            size='Download_Mbps', size_max=15,
            labels={'RSRP_dBm': 'RSRP (dBm)', 'SINR_dB': 'SINR (dB)'},
            color_discrete_sequence=['#667eea', '#f093fb', '#4facfe'],
            opacity=0.7,
            hover_data=['CellID', 'TerminalType', 'Download_Mbps']
        )
        fig_scatter.update_layout(
            height=340,
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=-0.2,
                       title_text='频段', font=dict(color='#94a3b8')),
            xaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8'),
                      titlefont=dict(color='#e2e8f0')),
            yaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8'),
                      titlefont=dict(color='#e2e8f0')),
        )
        st.plotly_chart(fig_scatter, use_container_width=True, config={'displayModeBar': False})

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("<p style='color:#8892b0;font-size:0.9rem;'>⬇️ 各频段下载速率分布</p>", unsafe_allow_html=True)
        fig_violin = px.violin(
            df, x='Band', y='Download_Mbps', color='Band',
            box=True, points=False,
            labels={'Download_Mbps': '下载速率 (Mbps)'},
            color_discrete_sequence=['#667eea', '#f093fb', '#4facfe'],
        )
        fig_violin.update_layout(
            height=340,
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8'),
                      titlefont=dict(color='#e2e8f0')),
            yaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8'),
                      titlefont=dict(color='#e2e8f0')),
        )
        st.plotly_chart(fig_violin, use_container_width=True, config={'displayModeBar': False})

    with col4:
        st.markdown("<p style='color:#8892b0;font-size:0.9rem;'>📱 各终端类型性能对比</p>", unsafe_allow_html=True)
        terminal_stats = df.groupby('TerminalType').agg({
            'RSRP_dBm': 'mean',
            'SINR_dB': 'mean',
            'Download_Mbps': 'mean'
        }).round(1).reset_index()

        fig_term = go.Figure()
        colors = ['#667eea', '#f093fb', '#4facfe']
        names = ['RSRP (dBm)', 'SINR (dB)', '下载速率 (Mbps)']
        for i, col in enumerate(['RSRP_dBm', 'SINR_dB', 'Download_Mbps']):
            fig_term.add_trace(go.Bar(
                name=names[i], x=terminal_stats['TerminalType'],
                y=terminal_stats[col], marker_color=colors[i],
                opacity=0.85, text=terminal_stats[col],
                textposition='outside', textfont=dict(size=9)
            ))
        fig_term.update_layout(
            height=340, barmode='group',
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=-0.25,
                       font=dict(color='#94a3b8')),
            xaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8'),
                      titlefont=dict(color='#e2e8f0')),
            yaxis=dict(gridcolor='#1e293b', tickfont=dict(color='#94a3b8'),
                      titlefont=dict(color='#e2e8f0'), title='数值'),
        )
        st.plotly_chart(fig_term, use_container_width=True, config={'displayModeBar': False})


# ==========================================
# 频段对比分析
# ==========================================

def render_band_analysis(df: pd.DataFrame) -> None:
    """
    渲染频段对比分析区域。
    
    参数:
        df: 筛选后的 DataFrame。
    """
    st.markdown("---")
    st.markdown("<h3 style='color:#e2e8f0;'>📶 频段对比分析</h3>", unsafe_allow_html=True)

    band_summary = df.groupby('Band').agg({
        'RSRP_dBm': ['mean', 'min', 'max'],
        'SINR_dB': ['mean', 'min', 'max'],
        'Download_Mbps': ['mean', 'min', 'max'],
        'CellID': 'count'
    }).round(1)

    band_summary.columns = ['平均RSRP', '最低RSRP', '最高RSRP',
                            '平均SINR', '最低SINR', '最高SINR',
                            '平均下载', '最低下载', '最高下载',
                            '数据点数']
    band_summary = band_summary.reset_index()

    col_table, col_chart = st.columns([3, 2])

    with col_table:
        st.markdown("<p style='color:#8892b0;font-size:0.9rem;'>📋 频段统计汇总</p>", unsafe_allow_html=True)
        st.dataframe(
            band_summary,
            use_container_width=True,
            hide_index=True,
            column_config={
                'Band': st.column_config.TextColumn('频段', width='small'),
                '数据点数': st.column_config.NumberColumn('点数', width='small'),
                '平均RSRP': st.column_config.NumberColumn('平均RSRP (dBm)', format='%.1f'),
                '平均SINR': st.column_config.NumberColumn('平均SINR (dB)', format='%.1f'),
                '平均下载': st.column_config.NumberColumn('平均下载 (Mbps)', format='%.0f'),
            }
        )

    with col_chart:
        st.markdown("<p style='color:#8892b0;font-size:0.9rem;'>📊 频段使用分布</p>", unsafe_allow_html=True)
        band_counts = df['Band'].value_counts().sort_index()

        fig_band = go.Figure(data=[go.Pie(
            labels=band_counts.index,
            values=band_counts.values,
            hole=0.4,
            marker_colors=['#667eea', '#f093fb', '#4facfe'],
            textinfo='label+percent',
            textfont_size=12,
            hovertemplate='<b>%{label}</b><br>点数: %{value}<br>占比: %{percent}<extra></extra>'
        )])
        fig_band.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            annotations=[dict(text='频段', x=0.5, y=0.5,
                            font_size=14, showarrow=False, font_color='#e2e8f0')]
        )
        st.plotly_chart(fig_band, use_container_width=True, config={'displayModeBar': False})


# ==========================================
# 数据表格
# ==========================================

def render_data_table(df: pd.DataFrame) -> None:
    """
    渲染可展开的数据表格，支持 CSV 导出。
    
    参数:
        df: 筛选后的 DataFrame。
    """
    st.markdown("---")
    with st.expander("📋 查看详细数据表"):
        display_df = df[[
            'CellID', 'Band', 'Latitude', 'Longitude',
            'RSRP_dBm', 'SINR_dB', 'TerminalType', 'Download_Mbps', 'rsrp_category'
        ]].sort_values('RSRP_dBm', ascending=False)

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'CellID': st.column_config.NumberColumn('小区ID', width='small'),
                'Band': st.column_config.TextColumn('频段', width='small'),
                'RSRP_dBm': st.column_config.NumberColumn('RSRP (dBm)', format='%.1f'),
                'SINR_dB': st.column_config.NumberColumn('SINR (dB)', format='%.1f'),
                'Download_Mbps': st.column_config.NumberColumn('下载速率 (Mbps)', format='%.1f'),
                'rsrp_category': st.column_config.TextColumn('信号质量'),
            }
        )

        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 导出筛选数据 (CSV)",
            data=csv,
            file_name='5g_filtered_data.csv',
            mime='text/csv',
        )


# ==========================================
# 主应用入口
# ==========================================

def main() -> None:
    """
    5G 信号可视化看板主入口。
    """
    # 标题
    st.markdown("""
        <div style="text-align:center; padding:10px 0 20px 0;">
            <h1 style="margin:0; font-size:2.2rem; 
                       background:linear-gradient(135deg,#667eea,#764ba2);
                       -webkit-background-clip:text;
                       -webkit-text-fill-color:transparent;
                       background-clip:text;">
                📡 5G 信号可视化看板
            </h1>
            <p style="margin:8px 0 0 0; color:#64748b; font-size:0.9rem;">
                交互式 5G 路测数据分析平台 | 
                <b style="color:#667eea;">Code with AI</b> 极客探索赛
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # 加载数据
    try:
        df = load_data("data/signal_samples.csv")
    except FileNotFoundError:
        st.error("❌ 未找到数据文件，请确保 `data/signal_samples.csv` 存在。")
        st.stop()
    except Exception as e:
        st.error(f"❌ 加载数据出错: {e}")
        st.stop()

    # 侧边栏筛选
    filtered_df = render_sidebar_filters(df)

    if len(filtered_df) == 0:
        st.warning("⚠️ 没有数据匹配当前筛选条件，请调整筛选器。")
        st.stop()

    # 准备地图数据
    display_df = prepare_map_data(filtered_df)

    # 统计面板
    render_statistics(display_df)

    # 地图区域
    render_map_section(display_df)

    # 信号质量分析
    render_signal_quality_analysis(display_df)

    # 频段对比
    render_band_analysis(display_df)

    # 数据表格
    render_data_table(display_df)

    # 页脚
    st.markdown("---")
    st.markdown("""
        <div style="text-align:center; color:#475569; font-size:0.75rem; padding:10px 0;">
            🚀 使用 <b>Streamlit</b> + <b>PyDeck</b> + <b>Plotly</b> 构建 | 
            比赛: <a href="https://github.com/besa-2026/code-with-ai-contest" style="color:#667eea;text-decoration:none;">besa-2026/code-with-ai-contest</a> | 
            数据: 5G 路测模拟数据
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
