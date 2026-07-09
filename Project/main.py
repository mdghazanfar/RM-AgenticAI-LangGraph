


"""
Streamlit web application for RM-AgenticAI-LangGraph system.
Provides user interface for prospect analysis and chat interaction.
Enhanced UI Version with Modern Design
"""

import streamlit as st
import pandas as pd
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import random

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import setup_logging, get_settings, get_logger
from config.settings import settings
from graph import ProspectAnalysisWorkflow
from state import WorkflowState

# Initialize
setup_logging()
logger = get_logger("main")
settings = get_settings()

# Page configuration with wider sidebar
st.set_page_config(
    page_title=settings.page_title, 
    page_icon=settings.page_icon, 
    layout=settings.layout,
    initial_sidebar_state="expanded"
)

# Theme state
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

# Premium Glassmorphic CSS
from ui_css import get_css
st.markdown(get_css(st.session_state.theme), unsafe_allow_html=True)

_CSS_INJECTED = True  # marker so we don't re-read the style block below
if False:  # -- original CSS removed, now in ui_css.py --
    pass


@st.cache_resource
def get_workflow() -> Optional[ProspectAnalysisWorkflow]:
    """Cache and return workflow instance."""
    try:
        return ProspectAnalysisWorkflow()
    except Exception as e:
        st.error(f"Failed to initialize workflow: {e}")
        return None

@st.cache_data
def load_prospects() -> List[Dict[str, Any]]:
    """Load prospect data from CSV or create dummy data."""
    try:
        prospects_df = pd.read_csv(settings.prospects_csv)
        prospects = prospects_df.to_dict('records')
        logger.info(f"Loaded {len(prospects)} prospects")
        return prospects
    except Exception as e:
        logger.warning(f"Using dummy data: {e}")
        return get_dummy_prospects()

def get_dummy_prospects() -> List[Dict[str, Any]]:
    """Generate dummy prospect data."""
    return [
        {"prospect_id": "DEMO001", "name": "Rajesh Kumar", "age": 32, "annual_income": 1200000, "current_savings": 500000, "target_goal_amount": 2000000, "investment_horizon_years": 5, "number_of_dependents": 2, "investment_experience_level": "Intermediate", "investment_goal": "Children's Education Fund"},
        {"prospect_id": "DEMO002", "name": "Priya Sharma", "age": 28, "annual_income": 800000, "current_savings": 300000, "target_goal_amount": 1500000, "investment_horizon_years": 10, "number_of_dependents": 0, "investment_experience_level": "Beginner", "investment_goal": "Retirement Planning"},
        {"prospect_id": "DEMO003", "name": "Amit Patel", "age": 45, "annual_income": 1500000, "current_savings": 2000000, "target_goal_amount": 5000000, "investment_horizon_years": 15, "number_of_dependents": 3, "investment_experience_level": "Advanced", "investment_goal": "Wealth Accumulation"}
    ]

def ensure_models_trained() -> bool:
    """Auto-train ML models if needed."""
    risk_model_path = Path(settings.risk_model_path)
    goal_model_path = Path(settings.goal_model_path)
    if not risk_model_path.exists() or not goal_model_path.exists():
        st.warning("⚠️ Training ML models (one-time setup)...")
        try:
            settings.models_dir.mkdir(parents=True, exist_ok=True)
            from ml.training.train_models import main as train_models
            with st.spinner("Training models..."):
                success = train_models()
            if success:
                st.success("✅ Models trained!")
                return True
            else:
                st.error("❌ Training failed")
                return False
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.info("System will use rule-based fallback")
            return False
    return True

def check_model_status() -> Dict[str, bool]:
    """Verify ML model availability."""
    status = {}
    try:
        import joblib
        joblib.load(settings.risk_model_path)
        status['risk_model'] = True
    except:
        status['risk_model'] = False
    try:
        import joblib
        joblib.load(settings.goal_model_path)
        status['goal_model'] = True
    except:
        status['goal_model'] = False
    return status

def run_analysis(workflow: ProspectAnalysisWorkflow, prospect_data: Dict[str, Any]) -> WorkflowState:
    """Execute analysis with event loop management."""
    if sys.platform == 'win32':
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except:
            pass
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(workflow.analyze_prospect(prospect_data))
        return result
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise

def safe_get(obj: Any, path: str, default: Any = None) -> Any:
    """Safely retrieve nested attributes."""
    try:
        parts = path.split('.')
        value = obj
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = getattr(value, part, None)
            if value is None:
                return default
        return value
    except:
        return default

def create_compact_risk_gauge(risk_level: str, confidence: float):
    """Create a compact gauge chart for risk assessment."""
    risk_mapping = {
        'Low': 25,
        'Moderate': 50,
        'High': 75,
        'Very High': 90
    }
    
    value = risk_mapping.get(risk_level, 50)
    
    theme = st.session_state.get('theme', 'Dark')
    font_color = '#FAFAFA' if theme == 'Dark' else '#09090B'
    axis_color = '#A1A1AA' if theme == 'Dark' else '#71717A'

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Risk Level: {risk_level}", 'font': {'size': 18, 'family': 'Outfit, sans-serif', 'color': font_color}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': '#64748b', 'tickfont': {'color': axis_color}},
            'bar': {'color': "#3B82F6"},
            'steps': [
                {'range': [0, 25], 'color': 'rgba(52,211,153,0.12)'},
                {'range': [25, 50], 'color': 'rgba(251,191,36,0.12)'},
                {'range': [50, 75], 'color': 'rgba(251,146,60,0.12)'},
                {'range': [75, 100], 'color': 'rgba(251,113,133,0.12)'}
            ],
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=30, r=30, t=80, b=30),
        font={'family': 'Inter, sans-serif', 'color': axis_color},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_performance_dashboard(state: WorkflowState):
    """Create performance dashboard with trading-style visualizations."""
    if not state.agent_executions:
        st.info("No execution data available")
        return
    
    # Agent Performance Bar Chart
    st.subheader("📊 Agent Performance Timeline")
    
    agents = [execution.agent_name for execution in state.agent_executions]
    execution_times = [execution.execution_time or 0 for execution in state.agent_executions]
    status_colors = ['#10B981' if execution.status == 'completed' else '#F43F5E' for execution in state.agent_executions]
    
    # Create bar chart
    fig = px.bar(
        x=agents, 
        y=execution_times,
        color=status_colors,
        color_discrete_map="identity",
        labels={'x': 'Agents', 'y': 'Execution Time (seconds)'},
        title="Agent Execution Performance"
    )
    
    theme = st.session_state.get('theme', 'Dark')
    axis_color = '#A1A1AA' if theme == 'Dark' else '#71717A'
    grid_color = 'rgba(255,255,255,0.06)' if theme == 'Dark' else 'rgba(0,0,0,0.06)'

    fig.update_layout(
        showlegend=False,
        height=350,
        xaxis_tickangle=-45,
        margin=dict(t=50, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter, sans-serif', 'color': axis_color},
        xaxis=dict(gridcolor=grid_color, color=axis_color),
        yaxis=dict(gridcolor=grid_color, color=axis_color)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add space between chart and metrics
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    
    # Performance Metrics Grid
    st.subheader("📈 Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_time = sum(execution_times)
        st.metric("Total Execution Time", f"{total_time:.2f}s")
    
    with col2:
        avg_time = total_time / len(execution_times) if execution_times else 0
        st.metric("Average Time", f"{avg_time:.2f}s")
    
    with col3:
        completed = sum(1 for e in state.agent_executions if e.status == 'completed')
        success_rate = (completed / len(state.agent_executions)) * 100
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    with col4:
        st.metric("Agents Executed", len(state.agent_executions))

def display_overview_tab(state: WorkflowState):
    """Display overview tab."""
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    
    st.header("📊 Overview")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        overall_conf = (state.overall_confidence or 0) * 100
        st.markdown(f'<div class="metric-card metric-card-success"><div class="metric-label">Overall Confidence</div><div class="metric-value">{overall_conf:.0f}%</div></div>', unsafe_allow_html=True)
    with col2:
        risk_level = safe_get(state, 'analysis.risk_assessment.risk_level', 'N/A')
        risk_class = "metric-card-info"
        if risk_level in ['High', 'Very High']:
            risk_class = "metric-card-danger"
        elif risk_level == 'Moderate':
            risk_class = "metric-card-warning"
        elif risk_level == 'Low':
            risk_class = "metric-card-success"
        st.markdown(f'<div class="metric-card {risk_class}"><div class="metric-label">Risk Level</div><div class="metric-value">{risk_level}</div></div>', unsafe_allow_html=True)
    with col3:
        persona = safe_get(state, 'analysis.persona_classification.persona_type', 'N/A')
        st.markdown(f'<div class="metric-card metric-card-info"><div class="metric-label">Investor Persona</div><div class="metric-value">{persona}</div></div>', unsafe_allow_html=True)
    with col4:
        num_products = len(state.recommendations.recommended_products)
        st.markdown(f'<div class="metric-card metric-card-info"><div class="metric-label">Products Recommended</div><div class="metric-value">{num_products}</div></div>', unsafe_allow_html=True)
    
    # Key Insights and Actions with better spacing
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
        st.markdown("""
            <div class="insight-card">
                <div class="card-title-inside">💡 Key Insights</div>
                <ul class="card-list">
        """, unsafe_allow_html=True)
        for insight in state.key_insights[:3]:
            st.markdown(f'<li>{insight}</li>', unsafe_allow_html=True)
        st.markdown("""
                </ul>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
        st.markdown("""
            <div class="action-card">
                <div class="card-title-inside">✓ Recommended Actions</div>
                <ul class="card-list">
        """, unsafe_allow_html=True)
        for action in state.action_items[:3]:
            st.markdown(f'<li>{action}</li>', unsafe_allow_html=True)
        st.markdown("""
                </ul>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_risk_tab(state: WorkflowState):
    """Display risk assessment tab."""
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    
    st.header("⚠️ Risk Assessment")
    risk = state.analysis.risk_assessment
    if risk:
        # Visualization first
        st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
        fig = create_compact_risk_gauge(risk.risk_level, risk.confidence_score)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Confidence score below visualization
        st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
        confidence_percent = risk.confidence_score * 100
        if confidence_percent >= 80:
            color = "#10b981"
            emoji = "🟢"
        elif confidence_percent >= 60:
            color = "#f59e0b"
            emoji = "🟡"
        else:
            color = "#F43F5E"
            emoji = "🔴"
            
        st.markdown(f"""
            <div class="confidence-score" style="background: {color}10; border: 2px solid {color}30;">
                <div style="font-size: 1rem; font-weight: 600; color: {color}; margin-bottom: 0.3rem;">Confidence Score</div>
                <div style="font-size: 1.2rem; font-weight: 700; color: {color};">{emoji} {confidence_percent:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Risk Factors below confidence score
        st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
        st.subheader("Risk Factors")
        st.markdown('<ul class="custom-bullet">', unsafe_allow_html=True)
        for factor in risk.risk_factors[:4]:
            st.markdown(f'<li>{factor}</li>', unsafe_allow_html=True)
        st.markdown('</ul>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Risk assessment not available")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_persona_tab(state: WorkflowState):
    """Display persona tab."""
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    
    st.header("👤 Investor Persona")
    persona = state.analysis.persona_classification
    if persona:
        # Persona Type with clear heading and value
        st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
        st.markdown('<div class="persona-heading">Persona Type</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="persona-value">{persona.persona_type}</div>', unsafe_allow_html=True)
        
        # Confidence score below persona type
        confidence_percent = persona.confidence_score * 100
        if confidence_percent >= 80:
            color = "#10b981"
            emoji = "🟢"
        elif confidence_percent >= 60:
            color = "#f59e0b"
            emoji = "🟡"
        else:
            color = "#F43F5E"
            emoji = "🔴"
            
        st.markdown(f"""
            <div class="confidence-score" style="background: {color}10; border: 2px solid {color}30; margin-top: 1rem;">
                <div style="font-size: 1rem; font-weight: 600; color: {color}; margin-bottom: 0.3rem;">Confidence Score</div>
                <div style="font-size: 1.2rem; font-weight: 700; color: {color};">{emoji} {confidence_percent:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Characteristics and insights in separate sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
            st.subheader("Characteristics")
            st.markdown('<ul class="custom-bullet">', unsafe_allow_html=True)
            for char in persona.characteristics[:4]:
                st.markdown(f'<li>{char}</li>', unsafe_allow_html=True)
            st.markdown('</ul>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
            st.subheader("Behavioral Insights")
            st.markdown('<ul class="custom-bullet">', unsafe_allow_html=True)
            for insight in persona.behavioral_insights[:3]:
                st.markdown(f'<li>{insight}</li>', unsafe_allow_html=True)
            st.markdown('</ul>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Persona classification not available")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_products_tab(state: WorkflowState):
    """Display products tab."""
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    
    st.header("💼 Product Recommendations")
    if state.recommendations.recommended_products:
        # Product suitability chart
        product_names = [p.product_name for p in state.recommendations.recommended_products]
        suitability_scores = [p.suitability_score * 100 for p in state.recommendations.recommended_products]
        
        fig = px.bar(
            x=suitability_scores, 
            y=product_names, 
            orientation='h',
            title="Product Suitability Scores",
            labels={'x': 'Suitability Score (%)', 'y': 'Products'},
            color=suitability_scores,
            color_continuous_scale=[[0, '#3B82F6'], [0.5, '#60A5FA'], [1, '#22D3EE']]
        )
        theme = st.session_state.get('theme', 'Dark')
        axis_color = '#A1A1AA' if theme == 'Dark' else '#71717A'
        grid_color = 'rgba(255,255,255,0.06)' if theme == 'Dark' else 'rgba(0,0,0,0.06)'

        fig.update_layout(
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'family': 'Inter, sans-serif', 'color': axis_color},
            margin=dict(l=20, r=20, t=50, b=20),
            coloraxis_showscale=False,
            xaxis=dict(gridcolor=grid_color, color=axis_color),
            yaxis=dict(gridcolor=grid_color, color=axis_color)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Product details in custom cards
        for i, product in enumerate(state.recommendations.recommended_products, 1):
            score = product.suitability_score * 100
            badge_class = "match-high" if score >= 80 else ("match-med" if score >= 50 else "match-low")
            
            st.markdown(f"""
                <div class="product-card">
                    <div class="product-header-row">
                        <span class="product-title-txt">#{i} - {product.product_name}</span>
                        <span class="match-badge {badge_class}">{score:.0f}% Match</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 0.75rem; font-size: 0.9rem;">
                        <div>
                            <strong>Type:</strong> {product.product_type}<br/>
                            <strong>Expected Returns:</strong> {product.expected_returns}
                        </div>
                        <div>
                            <strong>Fees:</strong> {product.fees}<br/>
                            <strong>Risk Alignment:</strong> {product.risk_alignment}
                        </div>
                    </div>
                    <div style="font-size: 0.85rem; color: #64748b; line-height: 1.4; border-top: 1px dashed #f1f5f9; padding-top: 0.5rem; margin-top: 0.5rem;">
                        <strong>Recommendation Basis:</strong> {product.justification}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No product recommendations generated")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_quality_tab(state: WorkflowState):
    """Display data quality tab."""
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    
    st.header("📈 Data Quality Assessment")
    
    quality_score = state.prospect.data_quality_score or 0
    quality_percent = quality_score * 100
    
    # Quality visualization first
    st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
    theme = st.session_state.get('theme', 'Dark')
    font_color = '#FAFAFA' if theme == 'Dark' else '#09090B'
    axis_color = '#A1A1AA' if theme == 'Dark' else '#71717A'

    # Quality gauge
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = quality_percent,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Data Quality Score", 'font': {'size': 16, 'color': font_color}},
        number = {'font': {'color': font_color}},
        gauge = {
            'axis': {'range': [None, 100], 'tickfont': {'color': axis_color}},
            'bar': {'color': "#22d3ee"},
            'steps': [
                {'range': [0, 50], 'color': 'rgba(251,113,133,0.15)'},
                {'range': [50, 80], 'color': 'rgba(251,191,36,0.15)'},
                {'range': [80, 100], 'color': 'rgba(52,211,153,0.15)'}
            ],
        }
    ))
    
    fig.update_layout(
        height=220,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': axis_color}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quality metrics below visualization
    st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
    if quality_percent >= 80:
        status = "🟢 Excellent"
        color = "#10b981"
    elif quality_percent >= 60:
        status = "🟡 Good"
        color = "#f59e0b"
    else:
        status = "🔴 Needs Improvement"
        color = "#F43F5E"
        
    st.markdown(f"""
        <div class="confidence-score" style="background: {color}10; border: 2px solid {color}30;">
            <div style="font-size: 1rem; font-weight: 600; color: {color}; margin-bottom: 0.3rem;">Quality Status</div>
            <div style="font-size: 1.2rem; font-weight: 700; color: {color};">{status} - {quality_percent:.1f}%</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Validation issues below quality status
    st.markdown('<div class="section-spacing">', unsafe_allow_html=True)
    if state.prospect.validation_errors:
        st.error(f"**Validation Issues:** {len(state.prospect.validation_errors)} found")
        st.markdown('<ul class="custom-bullet">', unsafe_allow_html=True)
        for error in state.prospect.validation_errors[:2]:
            st.markdown(f'<li>{error}</li>', unsafe_allow_html=True)
        st.markdown('</ul>', unsafe_allow_html=True)
    else:
        st.success("✅ No validation errors")
    
    if state.prospect.missing_fields:
        st.warning(f"**Missing Fields:** {len(state.prospect.missing_fields)}")
        st.markdown('<ul class="custom-bullet">', unsafe_allow_html=True)
        for field in state.prospect.missing_fields[:2]:
            st.markdown(f'<li>{field}</li>', unsafe_allow_html=True)
        st.markdown('</ul>', unsafe_allow_html=True)
    else:
        st.success("✅ All required fields present")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def display_goal_tab(state: WorkflowState):
    """Display goal feasibility and timeline assessment."""
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.header("🎯 Goal Feasibility & Timeline")
    
    gp = state.analysis.goal_prediction
    if gp:
        # Feasibility Summary Card
        prob_percent = gp.probability * 100
        if prob_percent >= 80:
            color = "#10b981"
            status = "Likely Achievable"
            emoji = "🟢"
        elif prob_percent >= 50:
            color = "#f59e0b"
            status = "Moderately Achievable"
            emoji = "🟡"
        else:
            color = "#F43F5E"
            status = "Unlikely Achievable"
            emoji = "🔴"
            
        st.markdown(f"""
            <div class="confidence-score" style="background: {color}10; border: 2px solid {color}30; margin-bottom: 1.5rem;">
                <div style="font-size: 1rem; font-weight: 600; color: {color}; margin-bottom: 0.3rem;">Feasibility Verdict</div>
                <div style="font-size: 1.4rem; font-weight: 700; color: {color};">{emoji} {gp.goal_success} - {status} ({prob_percent:.1f}% Probability)</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Timeline details
        timeline = gp.timeline_analysis
        if timeline:
            st.markdown(f"""
                <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #0ea5e9;">
                    <strong>Estimated Timeline:</strong> {timeline.get('estimated_years_to_goal', 'N/A')} years to reach the goal.
                </div>
            """, unsafe_allow_html=True)
            
        # Success factors and Challenges side by side
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🌟 Success Factors")
            if gp.success_factors:
                st.markdown('<ul class="custom-bullet">', unsafe_allow_html=True)
                for factor in gp.success_factors:
                    st.markdown(f'<li>{factor}</li>', unsafe_allow_html=True)
                st.markdown('</ul>', unsafe_allow_html=True)
            else:
                st.write("No specific success factors identified.")
                
        with col2:
            st.subheader("⚠️ Potential Obstacles")
            if gp.challenges:
                st.markdown('<ul class="custom-bullet">', unsafe_allow_html=True)
                for challenge in gp.challenges:
                    st.markdown(f'<li>{challenge}</li>', unsafe_allow_html=True)
                st.markdown('</ul>', unsafe_allow_html=True)
            else:
                st.write("No significant challenges identified.")
    else:
        st.warning("Goal feasibility analysis not available")
        
    st.markdown('</div>', unsafe_allow_html=True)


def display_portfolio_tab(state: WorkflowState):
    """Display optimized portfolio allocation."""
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.header("📈 Portfolio Allocation")
    
    alloc = state.recommendations.portfolio_allocation
    if alloc:
        # Build mappings
        prod_name_map = {p.product_id: p.product_name for p in state.recommendations.recommended_products}
        prod_type_map = {p.product_id: p.product_type for p in state.recommendations.recommended_products}
        
        labels = [prod_name_map.get(pid, pid) for pid in alloc.keys()]
        values = [weight * 100 for weight in alloc.values()]
        
        col1, col2 = st.columns([3, 2])
        
        theme = st.session_state.get('theme', 'Dark')
        axis_color = '#A1A1AA' if theme == 'Dark' else '#71717A'
        text_color = '#FAFAFA' if theme == 'Dark' else '#09090B'

        with col1:
            fig = px.pie(
                names=labels,
                values=values,
                title="Recommended Asset & Fund Allocation",
                hole=0.4,
                color_discrete_sequence=['#3B82F6', '#22D3EE', '#10B981', '#F59E0B', '#F43F5E', '#8B5CF6']
            )
            fig.update_layout(
                height=350,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'family': 'Outfit, sans-serif', 'color': text_color},
                margin=dict(l=20, r=20, t=50, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, font={'color': axis_color})
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("Allocation Breakdown")
            st.markdown(f"<p style='color: {axis_color}; font-size: 0.9rem;'>Target weights for optimal risk-adjusted returns:</p>", unsafe_allow_html=True)
            
            for pid, weight in sorted(alloc.items(), key=lambda x: x[1], reverse=True):
                name = prod_name_map.get(pid, pid)
                ptype = prod_type_map.get(pid, "Investment")
                border_color = 'rgba(255,255,255,0.08)' if theme == 'Dark' else 'rgba(0,0,0,0.08)'
                bg_color = 'rgba(255,255,255,0.04)' if theme == 'Dark' else 'rgba(0,0,0,0.02)'
                
                st.markdown(f"""
                    <div style="background: {bg_color}; padding: 1rem; border-radius: 12px; margin-bottom: 0.75rem; border: 1px solid {border_color}; border-right: 4px solid #3B82F6; backdrop-filter: blur(8px);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong style="font-size: 0.95rem; color: {text_color};">{name}</strong>
                            <span style="color: #3B82F6; font-weight: 700; font-size: 1rem;">{weight:.1%}</span>
                        </div>
                        <div style="font-size: 0.8rem; color: {axis_color}; margin-top: 0.25rem;">Type: {ptype}</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Portfolio optimization results not available")
        
    st.markdown('</div>', unsafe_allow_html=True)


def display_compliance_tab(state: WorkflowState):
    """Display suitability and regulatory compliance check results."""
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.header("⚖️ Compliance Check")
    
    cc = state.recommendations.compliance_check
    if cc:
        # Compliance Summary Card
        score_percent = cc.compliance_score * 100
        if cc.is_compliant:
            color = "#10b981"
            status = "Fully Compliant"
            emoji = "✅"
        else:
            color = "#F43F5E"
            status = "Action Required"
            emoji = "❌"
            
        st.markdown(f"""
            <div class="confidence-score" style="background: {color}10; border: 2px solid {color}30; margin-bottom: 1.5rem;">
                <div style="font-size: 1rem; font-weight: 600; color: {color}; margin-bottom: 0.3rem;">Compliance Status</div>
                <div style="font-size: 1.4rem; font-weight: 700; color: {color};">{emoji} {status} (Score: {score_percent:.1f}%)</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Display Violations if any
        if cc.violations:
            st.error(f"⚠️ **Violations Detected ({len(cc.violations)})**")
            st.markdown('<ul class="custom-bullet" style="color: #b91c1c;">', unsafe_allow_html=True)
            for violation in cc.violations:
                st.markdown(f'<li>{violation}</li>', unsafe_allow_html=True)
            st.markdown('</ul>', unsafe_allow_html=True)
            
        # Display Warnings if any
        if cc.warnings:
            st.warning(f"⚠️ **Warnings & Suitability Flags ({len(cc.warnings)})**")
            st.markdown('<ul class="custom-bullet" style="color: #b45309;">', unsafe_allow_html=True)
            for warning in cc.warnings:
                st.markdown(f'<li>{warning}</li>', unsafe_allow_html=True)
            st.markdown('</ul>', unsafe_allow_html=True)
            
        # Required Disclosures
        st.subheader("📋 Required Regulatory Disclosures")
        if cc.required_disclosures:
            st.markdown('<ul class="custom-bullet">', unsafe_allow_html=True)
            for disclosure in cc.required_disclosures:
                st.markdown(f'<li>{disclosure}</li>', unsafe_allow_html=True)
            st.markdown('</ul>', unsafe_allow_html=True)
        else:
            st.success("✅ No extra disclosures required for these product recommendations.")
    else:
        st.warning("Compliance check assessment not available")
        
    st.markdown('</div>', unsafe_allow_html=True)


def display_meeting_tab(state: WorkflowState):
    """Display relationship manager client meeting guide."""
    st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
    st.header("🤝 Client Meeting Guide")
    
    mg = state.meeting.meeting_guide
    if mg:
        st.markdown(f"""
            <div style="background: #f0f9ff; padding: 0.8rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid #0284c7;">
                <strong>Estimated Duration:</strong> {mg.estimated_duration or '45 minutes'}
            </div>
        """, unsafe_allow_html=True)
        
        # Create columns or collapse sections for Agenda and Talking Points
        st.subheader("📅 Proposed Agenda")
        st.markdown('<ul class="custom-bullet">', unsafe_allow_html=True)
        for item in mg.agenda_items:
            st.markdown(f'<li>{item}</li>', unsafe_allow_html=True)
        st.markdown('</ul>', unsafe_allow_html=True)
        
        st.subheader("🗣️ Key Talking Points")
        st.markdown('<ul class="custom-bullet">', unsafe_allow_html=True)
        for point in mg.key_talking_points:
            st.markdown(f'<li>{point}</li>', unsafe_allow_html=True)
        st.markdown('</ul>', unsafe_allow_html=True)
        
        st.subheader("❓ Discovery Questions to Ask")
        st.markdown('<ul class="custom-bullet">', unsafe_allow_html=True)
        for question in mg.questions_to_ask:
            st.markdown(f'<li>{question}</li>', unsafe_allow_html=True)
        st.markdown('</ul>', unsafe_allow_html=True)
        
        st.subheader("🛡️ Objection Handling Strategies")
        for obj, strategy in mg.objection_handling.items():
            with st.expander(f"Objection: {obj.replace('_', ' ').title()}"):
                st.write(strategy)
                
        st.subheader("⏭️ Next Steps & Action Plan")
        st.markdown('<ul class="custom-bullet">', unsafe_allow_html=True)
        for step in mg.next_steps:
            st.markdown(f'<li>{step}</li>', unsafe_allow_html=True)
        st.markdown('</ul>', unsafe_allow_html=True)
    else:
        st.warning("Client meeting guide not available")
        
    st.markdown('</div>', unsafe_allow_html=True)


def generate_chat_response(query: str, analysis_state: WorkflowState) -> str:
    """Generate AI response to user questions."""
    try:
        try:
            import google.generativeai as genai
            if not settings.gemini_api_key:
                logger.warning("No Gemini API key configured, using fallback")
                return generate_fallback_response(query, analysis_state)
            genai.configure(api_key=settings.gemini_api_key)
            context_parts = []
            if analysis_state.analysis.risk_assessment:
                risk = analysis_state.analysis.risk_assessment
                context_parts.append(f"Risk Level: {risk.risk_level} (Confidence: {risk.confidence_score:.0%})")
                context_parts.append(f"Risk Factors: {', '.join(risk.risk_factors[:3])}")
            if analysis_state.analysis.persona_classification:
                persona = analysis_state.analysis.persona_classification
                context_parts.append(f"Investor Persona: {persona.persona_type}")
                context_parts.append(f"Characteristics: {', '.join(persona.characteristics[:3])}")
            if analysis_state.analysis.goal_prediction:
                gp = analysis_state.analysis.goal_prediction
                context_parts.append(f"Goal Success: {gp.goal_success} (Probability: {gp.probability:.0%})")
            if analysis_state.recommendations.recommended_products:
                products = [p.product_name for p in analysis_state.recommendations.recommended_products[:3]]
                context_parts.append(f"Recommended Products: {', '.join(products)}")
            if analysis_state.recommendations.portfolio_allocation:
                allocs = [f"{k}: {v:.0%}" for k, v in analysis_state.recommendations.portfolio_allocation.items()]
                context_parts.append(f"Portfolio Allocation: {', '.join(allocs)}")
            if analysis_state.recommendations.compliance_check:
                cc = analysis_state.recommendations.compliance_check
                status = "Compliant" if cc.is_compliant else "Non-Compliant"
                context_parts.append(f"Compliance: {status} (Score: {cc.compliance_score:.2f})")
            if analysis_state.key_insights:
                context_parts.append(f"Key Insights: {'; '.join(analysis_state.key_insights[:2])}")
            context = "\n".join(context_parts)
            prompt = f"""You are an expert financial advisor assistant. Answer the user's question based on the prospect analysis below.

ANALYSIS CONTEXT:
{context}

USER QUESTION: {query}

Provide a clear, concise, and professional answer (2-4 sentences). Focus on being helpful and actionable."""
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            response = model.generate_content(prompt)
            return response.text.strip()
        except ImportError as e:
            logger.warning(f"Google Generative AI not available: {e}")
            return generate_fallback_response(query, analysis_state)
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return generate_fallback_response(query, analysis_state)
    except Exception as e:
        logger.error(f"Chat response generation failed: {e}")
        return "I apologize, but I'm having trouble processing your question right now. Please try rephrasing or ask about specific aspects like risk profile, investor persona, or product recommendations."

def generate_fallback_response(query: str, analysis_state: WorkflowState) -> str:
    """Enhanced rule-based response when AI unavailable."""
    query_lower = query.lower()
    if any(word in query_lower for word in ['risk', 'profile', 'assessment']):
        if analysis_state.analysis.risk_assessment:
            risk = analysis_state.analysis.risk_assessment
            factors_str = ", ".join(risk.risk_factors[:2]) if risk.risk_factors else "various factors"
            return f"The prospect has a **{risk.risk_level}** risk profile with {risk.confidence_score:.0%} confidence. Key factors include: {factors_str}. {risk.recommendations[0] if risk.recommendations else ''}"
        return "Risk assessment data is not currently available for this prospect."
    if any(word in query_lower for word in ['persona', 'investor', 'type', 'classification', 'behavior']):
        if analysis_state.analysis.persona_classification:
            persona = analysis_state.analysis.persona_classification
            chars_str = ", ".join(persona.characteristics[:2]) if persona.characteristics else "various characteristics"
            return f"This prospect is classified as a **{persona.persona_type}** investor. Key characteristics: {chars_str}. This classification helps tailor investment recommendations to their specific needs and preferences."
        return "Persona classification data is not currently available for this prospect."
    if any(word in query_lower for word in ['product', 'recommend', 'investment', 'fund', 'option']):
        if analysis_state.recommendations.recommended_products:
            top = analysis_state.recommendations.recommended_products[0]
            second = analysis_state.recommendations.recommended_products[1] if len(analysis_state.recommendations.recommended_products) > 1 else None
            response = f"Top recommendation: **{top.product_name}** ({top.suitability_score:.0%} suitability). {top.justification[:100]}..."
            if second:
                response += f" Also consider {second.product_name} ({second.suitability_score:.0%} suitability)."
            return response
        return "Product recommendations have not been generated yet for this prospect."
    if any(word in query_lower for word in ['goal', 'feasibility', 'achieve', 'probability']):
        if analysis_state.analysis.goal_prediction:
            gp = analysis_state.analysis.goal_prediction
            return f"The prospect's goal is predicted as **{gp.goal_success}** to succeed with a probability of **{gp.probability:.0%}**. Key challenges include: {', '.join(gp.challenges[:2])}."
        return "Goal prediction data is not available."
    if any(word in query_lower for word in ['portfolio', 'allocation', 'weight', 'diversify']):
        if analysis_state.recommendations.portfolio_allocation:
            alloc_str = ", ".join([f"{k}: {v:.0%}" for k, v in analysis_state.recommendations.portfolio_allocation.items()])
            return f"The recommended portfolio allocation is: {alloc_str}."
        return "Portfolio allocation data is not available."
    if any(word in query_lower for word in ['compliance', 'compliant', 'violation', 'regulation']):
        if analysis_state.recommendations.compliance_check:
            cc = analysis_state.recommendations.compliance_check
            status = "compliant" if cc.is_compliant else "non-compliant"
            violations = f" Violations found: {', '.join(cc.violations)}." if cc.violations else ""
            return f"The product recommendations are **{status}** with a compliance score of **{cc.compliance_score:.2f}**.{violations}"
        return "Compliance check data is not available."
    if any(word in query_lower for word in ['meeting', 'agenda', 'guide', 'objection']):
        if analysis_state.meeting.meeting_guide:
            mg = analysis_state.meeting.meeting_guide
            return f"Meeting guide is ready (estimated duration: {mg.estimated_duration}). Key talking points: {', '.join(mg.key_talking_points[:2])}."
        return "Meeting guide data is not available."
    return "I can help you understand this prospect's analysis. Ask me about risk profile, investor persona, product recommendations, goal feasibility, portfolio allocation, compliance, or key insights from the analysis."

def get_suggested_questions(analysis_state: WorkflowState) -> List[str]:
    """Generate contextual question suggestions."""
    questions = []
    if analysis_state.analysis.risk_assessment:
        risk_level = analysis_state.analysis.risk_assessment.risk_level
        questions.append(f"Why is this prospect's risk level {risk_level}?")
        questions.append("What factors contribute to the risk assessment?")
    if analysis_state.analysis.persona_classification:
        persona = analysis_state.analysis.persona_classification.persona_type
        questions.append(f"How should I approach a {persona} investor?")
    if analysis_state.recommendations.recommended_products:
        questions.append("Why were these specific products recommended?")
    questions.extend(["What are the next steps for this prospect?", "What are the key insights from the analysis?", "How confident is this analysis?"])
    return questions[:4]

def display_landing_page():
    """Display the landing page with full background image."""
    st.markdown("""
        <div class="main-header">
            <div class="main-title">
                RM Agentic AI System
            </div>
            <div class="main-subtitle">
                Advanced Multi-Agent Platform for Intelligent Financial Prospect Analysis and Investment Recommendations
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Features section
    st.markdown("""
        <div style='text-align: center; margin: 3rem 0 2rem 0;'>
            <h2 style='font-family: "Outfit", sans-serif; color: #0f172a; font-weight: 700; font-size: 1.8rem;'>
                Powerful AI-Driven Financial Analysis
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <h3 style="font-family: 'Outfit', sans-serif; font-weight: 600; font-size: 1.25rem; color: #1e293b; margin-bottom: 0.75rem;">Multi-Agent System</h3>
                <p style="color: #64748b; font-size: 0.9rem; line-height: 1.5; margin: 0;">Collaborative AI agents working together to provide comprehensive financial analysis</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3 style="font-family: 'Outfit', sans-serif; font-weight: 600; font-size: 1.25rem; color: #1e293b; margin-bottom: 0.75rem;">Risk Assessment</h3>
                <p style="color: #64748b; font-size: 0.9rem; line-height: 1.5; margin: 0;">Advanced ML models to evaluate investment risk profiles and suitability</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">💼</div>
                <h3 style="font-family: 'Outfit', sans-serif; font-weight: 600; font-size: 1.25rem; color: #1e293b; margin-bottom: 0.75rem;">Smart Recommendations</h3>
                <p style="color: #64748b; font-size: 0.9rem; line-height: 1.5; margin: 0;">Personalized investment product recommendations based on individual profiles</p>
            </div>
        """, unsafe_allow_html=True)

def display_application(selected_prospect):
    """Display the main application when a prospect is selected."""
    # Prospect Overview in 2x2 Grid - FIXED LAYOUT
    st.markdown(f"""
        <div style='background: var(--bg-card);
                    padding: 1.5rem;
                    border-radius: 16px;
                    border: 1px solid var(--border-glass);
                    box-shadow: var(--shadow-card);
                    margin-bottom: 1.5rem;
                    backdrop-filter: blur(12px);'>
            <h2 style='margin: 0; font-family: "Outfit", sans-serif; font-weight: 700; color: var(--text-primary); font-size: 1.5rem;'>
                👤 Prospect: {selected_prospect['name']}
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    # FIXED: 2x2 Grid Layout for prospect details - properly arranged with accents
    st.markdown(f"""
    <div class="grid-2x2">
        <div class="grid-item">
            <div class="metric-card metric-card-info">
                <div class="metric-label">Age</div>
                <div class="metric-value">{selected_prospect["age"]}</div>
            </div>
        </div>
        <div class="grid-item">
            <div class="metric-card metric-card-success">
                <div class="metric-label">Annual Income</div>
                <div class="metric-value">₹{selected_prospect["annual_income"]:,.0f}</div>
            </div>
        </div>
        <div class="grid-item">
            <div class="metric-card metric-card-success">
                <div class="metric-label">Current Savings</div>
                <div class="metric-value">₹{selected_prospect["current_savings"]:,.0f}</div>
            </div>
        </div>
        <div class="grid-item">
            <div class="metric-card metric-card-info">
                <div class="metric-label">Target Goal</div>
                <div class="metric-value">₹{selected_prospect["target_goal_amount"]:,.0f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📊 View Full Prospect Details"):
        st.json(selected_prospect)
    
    st.divider()
    
    # Analysis Section
    st.markdown("""
        <h2 style='text-align: center;
                   color: var(--text-primary);
                   font-size: 1.5rem;
                   font-weight: 700;
                   margin-bottom: 1.5rem;
                   font-family: "Outfit", sans-serif;'>
            🔍 AI-Powered Analysis
        </h2>
    """, unsafe_allow_html=True)
    
    analyze_button = st.button("🚀 Start AI Analysis", type="primary", use_container_width=True)
   
    if analyze_button:
        workflow = get_workflow()
        if workflow is None:
            st.error("Failed to initialize workflow")
            return
        
        with st.spinner("🤖 Analyzing prospect..."):
            # Show loading animation
            st.markdown("""
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                </div>
                <p style='text-align: center; color: #64748b; margin-top: 1rem;'>
                    Processing your analysis... This may take a few moments.
                </p>
            """, unsafe_allow_html=True)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            try:
                status_text.text("🔍 Validating data...")
                progress_bar.progress(20)
                result_state = run_analysis(workflow, selected_prospect)
                progress_bar.progress(100)
                status_text.text("✅ Complete!")
                st.session_state['analysis_result'] = result_state
                st.session_state['analyzed_prospect'] = selected_prospect
                import time
                time.sleep(1)
                status_text.empty()
                progress_bar.empty()
                st.success("✅ Analysis completed successfully!")
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                logger.error(f"Error: {e}", exc_info=True)
                return
   
    # Display results
    if 'analysis_result' in st.session_state:
        st.divider()
        
        st.markdown("""
            <h2 style='text-align: center;
                       color: var(--text-primary);
                       font-size: 1.5rem;
                       font-weight: 700;
                       margin-bottom: 1.5rem;
                       font-family: "Outfit", sans-serif;'>
                📊 Analysis Dashboard
            </h2>
        """, unsafe_allow_html=True)
        
        selected_tab = st.radio(
            "Select View:",
            ["📊 Analysis Results", "💬 Chat Assistant", "⚡ Performance"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        st.session_state.current_tab = selected_tab
        
        st.divider()
        
        # Display content based on selected tab
        if selected_tab == "📊 Analysis Results":
            analysis_tabs = st.tabs([
                "📊 Overview", 
                "⚠️ Risk", 
                "🎯 Goal Feasibility",
                "👤 Persona", 
                "💼 Products", 
                "📈 Portfolio Allocation",
                "⚖️ Compliance Check",
                "🤝 Meeting Guide",
                "📈 Quality"
            ])
            
            with analysis_tabs[0]:
                display_overview_tab(st.session_state["analysis_result"])
            
            with analysis_tabs[1]:
                display_risk_tab(st.session_state["analysis_result"])
            
            with analysis_tabs[2]:
                display_goal_tab(st.session_state["analysis_result"])

            with analysis_tabs[3]:
                display_persona_tab(st.session_state["analysis_result"])
            
            with analysis_tabs[4]:
                display_products_tab(st.session_state["analysis_result"])

            with analysis_tabs[5]:
                display_portfolio_tab(st.session_state["analysis_result"])

            with analysis_tabs[6]:
                display_compliance_tab(st.session_state["analysis_result"])

            with analysis_tabs[7]:
                display_meeting_tab(st.session_state["analysis_result"])
            
            with analysis_tabs[8]:
                display_quality_tab(st.session_state["analysis_result"])
            
        elif selected_tab == "💬 Chat Assistant":
            st.markdown("""
                <div style='background: var(--bg-card);
                            padding: 1.5rem;
                            border-radius: 16px;
                            border: 1px solid var(--border-glass);
                            box-shadow: var(--shadow-card);
                            margin-bottom: 1.5rem;
                            backdrop-filter: blur(12px);'>
                    <h2 style='margin: 0 0 0.5rem 0; font-family: "Outfit", sans-serif; color: var(--text-primary); font-weight: 700; font-size: 1.5rem;'>💬 Chat Assistant</h2>
                    <p style='margin: 0; color: var(--text-secondary); font-size: 0.95rem;'>Ask questions about the analysis</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Suggested Questions
            st.subheader("💡 Suggested Questions")
            suggestions = get_suggested_questions(st.session_state["analysis_result"])
            
            # Display suggestions in a grid and handle clicks
            st.markdown('<div class="suggestions-grid">', unsafe_allow_html=True)
            
            # Create columns for the suggestions
            cols = st.columns(2)
            clicked_suggestion = None
            
            for idx, suggestion in enumerate(suggestions):
                with cols[idx % 2]:
                    if st.button(suggestion, key=f"suggestion_{idx}", use_container_width=True):
                        clicked_suggestion = suggestion
                        st.session_state.last_suggestion = suggestion
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Handle suggestion click and generate response
            if clicked_suggestion:
                # Add user message to chat history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": clicked_suggestion,
                    "timestamp": datetime.now()
                })
                
                # Generate and add assistant response
                with st.spinner("🤖 Generating answer..."):
                    response = generate_chat_response(
                        clicked_suggestion,
                        st.session_state["analysis_result"]
                    )
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now()
                })
                
                # Clear the last suggestion to prevent repeated triggers
                st.session_state.last_suggestion = None
                st.rerun()
            
            # Chat Input with Send Button
            user_query = st.chat_input("Ask about risk, products, or any analysis aspect...")
            if user_query:
                # Add user message to chat history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_query,
                    "timestamp": datetime.now()
                })
                
                # Generate and add assistant response
                with st.spinner("🤖 Thinking..."):
                    response = generate_chat_response(
                        user_query,
                        st.session_state["analysis_result"]
                    )
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now()
                })
                st.rerun()
            
            # Display chat history
            if st.session_state.chat_history:
                st.subheader("💬 Conversation")
                for message in st.session_state.chat_history:
                    time_str = message['timestamp'].strftime('%H:%M:%S')
                    if message["role"] == "user":
                        st.markdown(f"""
                            <div class="chat-message user-message">
                                <div class="chat-avatar user-avatar">👤</div>
                                <div style="flex: 1;">
                                    <div style="font-weight: 600; margin-bottom: 0.25rem; font-size: 0.85rem; color: #475569;">You</div>
                                    <div>{message['content']}</div>
                                    <div class="chat-time">{time_str}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="chat-message assistant-message">
                                <div class="chat-avatar assistant-avatar">🤖</div>
                                <div style="flex: 1;">
                                    <div style="font-weight: 600; margin-bottom: 0.25rem; font-size: 0.85rem; color: #4f46e5;">AI Advisor</div>
                                    <div>{message['content']}</div>
                                    <div class="chat-time">{time_str}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                
                if st.button("🗑️ Clear Chat History", type="secondary"):
                    st.session_state.chat_history = []
                    st.session_state.chat_input = ""
                    st.session_state.last_suggestion = None
                    st.rerun()
                    
        elif selected_tab == "⚡ Performance":
            create_performance_dashboard(st.session_state["analysis_result"])
            
    else:
        st.info("👆 Click **Start AI Analysis** to begin the comprehensive prospect evaluation")

def main():
    """Main application execution."""
    
    # Initialize session state
    if "current_tab" not in st.session_state:
        st.session_state.current_tab = "📊 Analysis Results"
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Track last clicked suggestion
    if "last_suggestion" not in st.session_state:
        st.session_state.last_suggestion = None

    # Enhanced Sidebar with professional layout
    with st.sidebar:
        st.markdown("""
            <div class="sidebar-header">
                <h2>⚙️ System Control</h2>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-compact">', unsafe_allow_html=True)
        
        # Theme toggle
        def on_theme_change():
            pass # Streamlit handles session state automatically for widget keys
            
        st.session_state.theme = st.radio(
            "UI Theme",
            ["Dark", "Light"],
            horizontal=True,
            index=0 if st.session_state.theme == "Dark" else 1
        )
        
        st.divider()
        
        st.subheader("🧠 ML Model Status")
        model_status = check_model_status()
        
        col1, col2 = st.columns(2)
        with col1:
            if model_status.get('risk_model'):
                st.markdown('<div class="sidebar-status status-success">✅ Risk</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="sidebar-status status-warning">⚠️ Risk</div>', unsafe_allow_html=True)
        with col2:
            if model_status.get('goal_model'):
                st.markdown('<div class="sidebar-status status-success">✅ Goal</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="sidebar-status status-warning">⚠️ Goal</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Train Models", use_container_width=True):
            ensure_models_trained()
            st.rerun()
        
        st.divider()
        
        st.subheader("👤 Select Prospect")
        prospects = load_prospects()
        
        prospect_source = st.radio(
            "Prospect Source",
            ["Existing Prospect", "Create Custom Prospect"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        selected_prospect = None
        
        if prospect_source == "Existing Prospect":
            # Add empty option at the beginning
            prospect_options = ["Select prospect..."] + [f"{p['name']} (Age {p['age']})" for p in prospects]
            selected_idx = st.selectbox(
                "Choose a prospect:", 
                range(len(prospect_options)), 
                format_func=lambda i: prospect_options[i],
                label_visibility="collapsed"
            )
            
            # Handle the empty selection
            if selected_idx > 0:
                selected_prospect = prospects[selected_idx - 1]  # Adjust for the empty option
            else:
                st.info("👈 Select a prospect to begin analysis")
        else:
            with st.form("custom_prospect_form"):
                st.markdown("<h4 style='color: var(--text-primary); margin-top:0; font-family: Outfit, sans-serif;'>✨ Custom Details</h4>", unsafe_allow_html=True)
                cp_name = st.text_input("Full Name", value="Jane Doe")
                
                c1, c2 = st.columns(2)
                with c1:
                    cp_age = st.number_input("Age", min_value=18, max_value=100, value=35)
                    cp_income = st.number_input("Income (₹)", min_value=0, value=1500000, step=100000)
                    cp_horizon = st.number_input("Horizon (Yrs)", min_value=1, max_value=50, value=10)
                with c2:
                    cp_dependents = st.number_input("Dependents", min_value=0, max_value=10, value=2)
                    cp_savings = st.number_input("Savings (₹)", min_value=0, value=500000, step=100000)
                    cp_target = st.number_input("Target (₹)", min_value=0, value=5000000, step=500000)
                
                cp_experience = st.selectbox("Experience Level", ["Beginner", "Intermediate", "Advanced"])
                cp_goal = st.text_input("Investment Goal", value="Wealth Accumulation")
                
                submit_custom = st.form_submit_button("Analyze Custom Prospect", type="primary", use_container_width=True)
                
                if submit_custom:
                    st.session_state.custom_prospect = {
                        "prospect_id": f"CUST{random.randint(1000, 9999)}",
                        "name": cp_name,
                        "age": cp_age,
                        "annual_income": cp_income,
                        "current_savings": cp_savings,
                        "target_goal_amount": cp_target,
                        "investment_horizon_years": cp_horizon,
                        "number_of_dependents": cp_dependents,
                        "investment_experience_level": cp_experience,
                        "investment_goal": cp_goal
                    }
                    
            if 'custom_prospect' in st.session_state:
                selected_prospect = st.session_state.custom_prospect
        
        st.divider()
        
        st.markdown("""
            <div class="about-section">
                <h4>ℹ️ About</h4>
                <p><strong>Multi-Agent AI System</strong> for comprehensive prospect analysis with risk assessment, persona classification, and product recommendations.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
   
    # Main content logic
    if selected_prospect is None:
        # Show landing page when no prospect is selected
        display_landing_page()
    else:
        # Show application when prospect is selected
        display_application(selected_prospect)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Application error: {e}")
        logger.error(f"Application crashed: {e}", exc_info=True)
