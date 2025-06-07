import plotly.express as px
import plotly.graph_objects as go
from config import PLOTLY_AVAILABLE, COLOR_PALETTE

def create_styled_bar_chart(df, x, y, title, color=None):
    """スタイル付き棒グラフの作成"""
    if not PLOTLY_AVAILABLE:
        return None
    
    fig = px.bar(
        df, 
        x=x, 
        y=y, 
        title=title,
        color=color,
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12),
        title_font_size=16
    )
    
    return fig

def create_styled_scatter_plot(df, x, y, title, hover_data=None, size=None):
    """スタイル付き散布図の作成"""
    if not PLOTLY_AVAILABLE:
        return None
    
    fig = px.scatter(
        df,
        x=x,
        y=y,
        title=title,
        hover_data=hover_data,
        size=size
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12),
        title_font_size=16
    )
    
    return fig

