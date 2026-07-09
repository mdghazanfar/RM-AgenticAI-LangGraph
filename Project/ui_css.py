"""Premium Dark Glassmorphic CSS Design System for RM-AgenticAI Dashboard."""

def get_css(theme: str = "Dark") -> str:
    tokens = ""
    if theme == "Light":
        tokens = """
    /* ==================== DESIGN TOKENS ==================== */
    :root {
        --bg-primary: #FAFAFA;
        --bg-secondary: #F4F4F5;
        --bg-card: rgba(255,255,255,0.9);
        --bg-card-hover: rgba(255,255,255,1);
        --bg-glass: rgba(255,255,255,0.7);
        --border-glass: rgba(0,0,0,0.06);
        --border-glass-hover: rgba(37,99,235,0.3);
        --text-primary: #09090B;
        --text-secondary: #52525B;
        --text-muted: #71717A;
        --accent-indigo: #2563EB;
        --accent-violet: #4F46E5;
        --accent-emerald: #059669;
        --accent-amber: #D97706;
        --accent-rose: #E11D48;
        --accent-cyan: #0891B2;
        --gradient-primary: linear-gradient(135deg, #1E40AF 0%, #2563EB 50%, #3B82F6 100%);
        --gradient-card: linear-gradient(135deg, rgba(37,99,235,0.05) 0%, rgba(79,70,229,0.02) 100%);
        --title-gradient: linear-gradient(135deg, #09090B 0%, #1E40AF 50%, #4F46E5 100%);
        --sidebar-bg: linear-gradient(180deg, #FAFAFA 0%, #F4F4F5 100%);
        --shadow-glow: 0 0 15px rgba(37,99,235,0.1);
        --shadow-card: 0 4px 15px -2px rgba(0,0,0,0.03);
        --radius-lg: 14px;
        --radius-md: 10px;
        --radius-sm: 6px;
    }"""
    else:
        tokens = """
    /* ==================== DESIGN TOKENS ==================== */
    :root {
        --bg-primary: #09090B;
        --bg-secondary: #18181B;
        --bg-card: rgba(255,255,255,0.03);
        --bg-card-hover: rgba(255,255,255,0.05);
        --bg-glass: rgba(9,9,11,0.7);
        --border-glass: rgba(255,255,255,0.06);
        --border-glass-hover: rgba(59,130,246,0.3);
        --text-primary: #FAFAFA;
        --text-secondary: #A1A1AA;
        --text-muted: #71717A;
        --accent-indigo: #3B82F6;
        --accent-violet: #8B5CF6;
        --accent-emerald: #10B981;
        --accent-amber: #F59E0B;
        --accent-rose: #F43F5E;
        --accent-cyan: #22D3EE;
        --gradient-primary: linear-gradient(135deg, #2563EB 0%, #3B82F6 50%, #60A5FA 100%);
        --gradient-card: linear-gradient(135deg, rgba(59,130,246,0.08) 0%, rgba(139,92,246,0.03) 100%);
        --title-gradient: linear-gradient(135deg, #FFFFFF 0%, #93C5FD 50%, #8B5CF6 100%);
        --sidebar-bg: linear-gradient(180deg, #18181B 0%, #09090B 100%);
        --shadow-glow: 0 0 25px rgba(59,130,246,0.15);
        --shadow-card: 0 4px 20px -4px rgba(0,0,0,0.5);
        --radius-lg: 14px;
        --radius-md: 10px;
        --radius-sm: 6px;
    }"""

    base_css = """

    /* ==================== GLOBAL ==================== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

    .main, .stApp, [data-testid="stAppViewContainer"] {
        background: var(--bg-primary) !important;
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
    }

    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1400px;
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Outfit', sans-serif !important;
        color: var(--text-primary) !important;
    }

    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span {
        color: var(--text-primary);
    }

    /* ==================== ANIMATIONS ==================== */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 8px rgba(99,102,241,0.3); }
        50% { box-shadow: 0 0 20px rgba(99,102,241,0.6); }
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    @keyframes statusPulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes orbFloat {
        0% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(3%, 4%) scale(1.05); }
        66% { transform: translate(-2%, 5%) scale(0.95); }
        100% { transform: translate(0, 0) scale(1); }
    }

    /* ==================== BACKGROUND ANIMATION ==================== */
    [data-testid="stAppViewContainer"] {
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="stAppViewContainer"]::before, [data-testid="stAppViewContainer"]::after {
        content: '';
        position: fixed;
        border-radius: 50%;
        filter: blur(120px);
        z-index: 0;
        pointer-events: none;
        opacity: 0.15;
    }

    [data-testid="stAppViewContainer"]::before {
        top: -10%;
        left: -10%;
        width: 50vw;
        height: 50vw;
        background: var(--accent-indigo);
        animation: orbFloat 25s infinite alternate ease-in-out;
    }

    [data-testid="stAppViewContainer"]::after {
        bottom: -10%;
        right: -10%;
        width: 60vw;
        height: 60vw;
        background: var(--accent-cyan);
        animation: orbFloat 20s infinite alternate-reverse ease-in-out;
    }
    
    /* Ensure content is above background */
    .block-container {
        position: relative;
        z-index: 1;
    }

    /* ==================== SCROLLBAR ==================== */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.3); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.5); }

    /* ==================== HERO / LANDING ==================== */
    .main-header {
        background: radial-gradient(ellipse at 20% 50%, rgba(37,99,235,0.08) 0%, transparent 50%),
                    radial-gradient(ellipse at 80% 20%, rgba(139,92,246,0.05) 0%, transparent 50%),
                    radial-gradient(ellipse at 50% 80%, rgba(8,145,178,0.05) 0%, transparent 50%),
                    var(--bg-primary);
        padding: 6rem 2rem;
        border-radius: 0px;
        margin: -2rem -1rem 2rem -1rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        min-height: 75vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        width: 100vw;
        margin-left: calc(-50vw + 50%);
        margin-right: calc(-50vw + 50%);
        border-bottom: 1px solid var(--border-glass);
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: repeating-conic-gradient(
            rgba(37,99,235,0.015) 0deg 10deg,
            transparent 10deg 20deg
        );
        animation: spin 150s linear infinite;
    }

    .main-title {
        color: var(--text-primary);
        font-size: 4rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
        font-family: 'Outfit', sans-serif;
        letter-spacing: -1px;
        background: var(--title-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        position: relative;
        z-index: 1;
    }

    .main-subtitle {
        color: var(--text-secondary);
        font-size: 1.4rem;
        font-weight: 400;
        max-width: 700px;
        line-height: 1.6;
        margin-bottom: 2rem;
        position: relative;
        z-index: 1;
    }

    /* ==================== FEATURE CARDS ==================== */
    .feature-card {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-lg);
        padding: 2rem 1.5rem;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s ease-out both;
        min-height: 200px;
    }
    .feature-card:nth-child(2) { animation-delay: 0.15s; }
    .feature-card:nth-child(3) { animation-delay: 0.3s; }

    .feature-card:hover {
        background: var(--bg-card-hover);
        border-color: var(--border-glass-hover);
        transform: translateY(-6px);
        box-shadow: var(--shadow-glow);
    }

    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
    }

    .feature-card h3 {
        color: var(--text-primary) !important;
        font-family: 'Outfit', sans-serif;
        font-size: 1.15rem;
        margin-bottom: 0.75rem;
    }

    .feature-card p {
        color: var(--text-muted) !important;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    /* ==================== METRIC CARDS ==================== */
    .metric-card {
        background: var(--bg-card);
        backdrop-filter: blur(12px);
        padding: 1rem 0.75rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--border-glass);
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-card);
        height: 90px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        animation: fadeInUp 0.5s ease-out both;
    }

    .metric-card:hover {
        border-color: var(--border-glass-hover);
        transform: translateY(-2px);
        box-shadow: var(--shadow-glow);
    }

    .metric-label {
        font-size: 0.7rem;
        color: var(--text-muted);
        font-weight: 600;
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    .metric-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--text-primary);
        font-family: 'Outfit', sans-serif;
    }

    /* ==================== 2x2 GRID ==================== */
    .grid-2x2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.8rem;
        margin: 1rem 0;
    }
    .grid-item { min-height: 90px; }

    /* ==================== LOADING ==================== */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
        flex-direction: column;
    }
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 3px solid rgba(99,102,241,0.15);
        border-top: 3px solid var(--accent-indigo);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }

    /* ==================== ANALYSIS SECTIONS ==================== */
    .analysis-section {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid var(--border-glass);
        box-shadow: var(--shadow-card);
        animation: fadeInUp 0.5s ease-out both;
    }

    /* ==================== CHAT ==================== */
    .chat-message {
        padding: 1rem 1.25rem;
        border-radius: var(--radius-md);
        margin: 0.5rem 0;
        border: 1px solid var(--border-glass);
        backdrop-filter: blur(8px);
        transition: all 0.2s ease;
    }
    .user-message {
        background: rgba(99,102,241,0.06);
        margin-left: 2rem;
        border-left: 3px solid var(--accent-indigo);
    }
    .assistant-message {
        background: rgba(16,185,129,0.06);
        margin-right: 2rem;
        border-left: 3px solid var(--accent-emerald);
    }

    .suggestions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 0.75rem;
        margin: 1rem 0;
    }

    /* ==================== PRODUCT CARDS ==================== */
    .product-card {
        background: var(--bg-card);
        backdrop-filter: blur(12px);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-md);
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .product-card:hover {
        border-color: var(--border-glass-hover);
        transform: translateY(-2px);
        box-shadow: var(--shadow-glow);
    }
    .product-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    .product-title-txt {
        font-weight: 700;
        font-size: 1.05rem;
        color: var(--text-primary);
        font-family: 'Outfit', sans-serif;
    }
    .match-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .match-high { background: rgba(16,185,129,0.1); color: var(--accent-emerald); border: 1px solid rgba(16,185,129,0.2); }
    .match-med  { background: rgba(245,158,11,0.1); color: var(--accent-amber); border: 1px solid rgba(245,158,11,0.2); }
    .match-low  { background: rgba(244,63,94,0.1); color: var(--accent-rose); border: 1px solid rgba(244,63,94,0.2); }

    /* ==================== CONFIDENCE SCORE ==================== */
    .confidence-score {
        text-align: center;
        padding: 0.8rem;
        border-radius: var(--radius-md);
        margin: 1rem 0;
        backdrop-filter: blur(8px);
    }

    /* ==================== INSIGHT / ACTION CARDS ==================== */
    .insight-card, .action-card {
        background: var(--bg-card);
        backdrop-filter: blur(12px);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-md);
        padding: 1.25rem;
    }
    .insight-card { border-left: 3px solid var(--accent-indigo); }
    .action-card  { border-left: 3px solid var(--accent-emerald); }

    .card-title-inside {
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 0.75rem;
        color: var(--text-primary);
        font-family: 'Outfit', sans-serif;
    }
    .card-list {
        list-style: none;
        padding-left: 0;
        margin: 0;
    }
    .card-list li {
        padding: 0.35rem 0;
        padding-left: 1.2rem;
        position: relative;
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    .card-list li::before {
        content: "▸";
        color: var(--accent-indigo);
        position: absolute;
        left: 0;
        font-weight: bold;
    }

    /* ==================== CUSTOM BULLETS ==================== */
    .custom-bullet { list-style-type: none; padding-left: 0; }
    .custom-bullet li {
        padding: 0.35rem 0;
        position: relative;
        padding-left: 1.2rem;
        color: var(--text-secondary);
    }
    .custom-bullet li:before {
        content: "▸";
        color: var(--accent-indigo);
        font-weight: bold;
        position: absolute;
        left: 0;
    }

    /* ==================== PERSONA ==================== */
    .persona-heading {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.3rem;
    }
    .persona-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--accent-indigo);
        font-family: 'Outfit', sans-serif;
        margin-bottom: 1rem;
    }

    .section-spacing { margin-bottom: 1.5rem; }
    .compact-viz { margin: 0.5rem 0; }

    /* ==================== BUTTONS ==================== */
    .stButton > button {
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid var(--border-glass) !important;
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-glow) !important;
        border-color: var(--border-glass-hover) !important;
        background: var(--bg-card-hover) !important;
    }
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        background: var(--gradient-primary) !important;
        border: none !important;
        color: white !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {
        box-shadow: 0 8px 30px rgba(99,102,241,0.4) !important;
    }
    
    .stButton > button[kind="primary"] *,
    .stButton > button[data-testid="baseButton-primary"] *,
    .stButton > button[data-testid="stBaseButton-primary"] * {
        color: white !important;
    }

    /* ==================== SIDEBAR ==================== */
    [data-testid="stSidebar"] {
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-glass) !important;
        min-width: 280px !important;
        max-width: 300px !important;
    }
    [data-testid="stSidebar"] .block-container {
        padding: 1rem 1.5rem;
    }
    [data-testid="stSidebar"] label {
        color: var(--text-secondary) !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--text-primary) !important;
    }

    .sidebar-header {
        background: var(--gradient-card);
        backdrop-filter: blur(16px);
        padding: 1.2rem 1rem;
        border-radius: var(--radius-md);
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-card);
        border: 1px solid var(--border-glass);
    }
    .sidebar-header h2 {
        color: var(--text-primary) !important;
        margin: 0;
        font-size: 1.2rem;
        font-weight: 700;
        font-family: 'Outfit', sans-serif;
    }

    /* Sidebar compact overrides */
    .sidebar-compact .stButton button {
        font-size: 0.85rem;
        padding: 0.6rem 1rem;
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm);
        font-weight: 600;
    }
    .sidebar-compact .stButton button:hover {
        box-shadow: 0 4px 20px rgba(99,102,241,0.4) !important;
        transform: translateY(-1px);
    }

    .sidebar-compact .stSelectbox div[data-baseweb="select"] {
        border-radius: var(--radius-sm);
        border: 1px solid var(--border-glass);
        background: var(--bg-card);
    }
    .sidebar-compact .stSelectbox div[data-baseweb="select"]:hover {
        border-color: var(--border-glass-hover);
    }

    .sidebar-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 0.75rem;
        border-radius: var(--radius-sm);
        margin: 0.25rem 0;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .status-success {
        background: rgba(16,185,129,0.1);
        color: var(--accent-emerald) !important;
        border: 1px solid rgba(16,185,129,0.2);
    }
    .status-warning {
        background: rgba(245,158,11,0.1);
        color: var(--accent-amber) !important;
        border: 1px solid rgba(245,158,11,0.2);
    }

    .about-section {
        background: var(--gradient-card);
        backdrop-filter: blur(12px);
        padding: 1.2rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--border-glass);
        border-left: 3px solid var(--accent-indigo);
        margin-top: 1rem;
    }
    .about-section h4 {
        margin: 0 0 0.5rem 0;
        color: var(--text-primary) !important;
        font-size: 0.95rem;
        font-weight: 700;
        font-family: 'Outfit', sans-serif;
    }
    .about-section p {
        margin: 0;
        color: var(--text-muted) !important;
        font-size: 0.8rem;
        line-height: 1.5;
    }

    /* ==================== TABS ==================== */
    div[role="tablist"] {
        gap: 0.25rem;
        background: var(--bg-card);
        padding: 0.35rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--border-glass);
        margin-bottom: 1.5rem;
        backdrop-filter: blur(12px);
    }
    button[data-baseweb="tab"] {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: var(--text-muted) !important;
        background: transparent !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.45rem 0.75rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    button[data-baseweb="tab"]:hover {
        color: var(--accent-indigo) !important;
        background: rgba(99,102,241,0.08) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: white !important;
        background: var(--gradient-primary) !important;
        box-shadow: 0 4px 16px rgba(99,102,241,0.3) !important;
    }
    div[role="tablist"] > div[role="presentation"] {
        display: none !important;
    }

    /* ==================== STREAMLIT OVERRIDES ==================== */
    .stRadio > div {
        background: var(--bg-card);
        border-radius: var(--radius-md);
        padding: 0.5rem;
        border: 1px solid var(--border-glass);
    }
    .stRadio label { color: var(--text-secondary) !important; }

    .stDivider { border-color: var(--border-glass) !important; }

    .stExpander {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius-md) !important;
    }
    .stExpander header { color: var(--text-primary) !important; }

    /* Alerts */
    [data-testid="stAlert"] * {
        color: var(--text-primary) !important;
    }

    .stMetric {
        background: var(--bg-card);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-md);
        padding: 0.75rem;
    }
    .stMetric label { color: var(--text-muted) !important; }
    .stMetric [data-testid="stMetricValue"] { color: var(--text-primary) !important; font-family: 'Outfit', sans-serif; }

    .stProgress > div > div { background: var(--gradient-primary) !important; }
    .stSpinner > div { color: var(--accent-indigo) !important; }

    /* Selectbox / Input dark theme */
    .stSelectbox label,
    .stTextInput label,
    .stNumberInput label { color: var(--text-secondary) !important; }

    div[data-baseweb="select"] > div,
    .stTextInput input,
    .stNumberInput input {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-glass) !important;
        color: var(--text-primary) !important;
    }

    div[data-testid="stForm"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius-md) !important;
        padding: 1.5rem !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: var(--shadow-card) !important;
    }

    .stChatInput, [data-testid="stChatInput"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius-md) !important;
    }
    .stChatInput textarea { color: var(--text-primary) !important; }

    /* JSON viewer */
    .stJson { background: var(--bg-card) !important; border-radius: var(--radius-sm) !important; }
</style>
"""
    return f"<style>\n{tokens}\n{base_css}"
