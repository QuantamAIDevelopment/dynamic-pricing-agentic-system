import streamlit as st
import requests
from typing import List, Dict
from datetime import datetime

API_URL = "http://localhost:8000"

# --- Custom CSS for new color scheme ---
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(90deg, #FFD6E8 0%, #BFD4FF 100%);
        color: black !important;
    }
    .stApp {
        background: linear-gradient(90deg, #FFD6E8 0%, #BFD4FF 100%) !important;
        color: black !important;
    }
    .dashboard-title {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-top: 2rem;
        margin-bottom: 0.5rem;
        color: #3A2D4D;
    }
    .dashboard-subtitle {
        font-size: 1.25rem;
        text-align: center;
        margin-bottom: 2.5rem;
        color: #222;
    }
    /* Style input fields */
    input, textarea, .stTextInput > div > div > input, .stTextArea > div > textarea {
        background: linear-gradient(90deg, #FFD6E8 0%, #BFD4FF 100%) !important;
        color: black !important;
        border: 2px solid #BFD4FF !important;
        border-radius: 12px !important;
    }
    /* Style placeholder text to black */
    input::placeholder, textarea::placeholder, .stTextInput > div > div > input::placeholder, .stTextArea > div > textarea::placeholder {
        color: black !important;
        opacity: 1 !important;
    }
    /* Style selectboxes */
    .stSelectbox > div > div > div, .stSelectbox > div > div > div > div {
        background: linear-gradient(90deg, #FFD6E8 0%, #BFD4FF 100%) !important;
        color: black !important;
        border-radius: 12px !important;
    }
    /* Style buttons */
    button, .stButton > button {
        background: linear-gradient(90deg, #FFD6E8 0%, #BFD4FF 100%) !important;
        color: black !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600;
        box-shadow: 0 2px 8px 0 rgba(80, 80, 120, 0.08);
        transition: box-shadow 0.2s;
    }
    button:hover, .stButton > button:hover {
        box-shadow: 0 4px 16px 0 rgba(80, 80, 120, 0.16);
        background: linear-gradient(90deg, #BFD4FF 0%, #FFD6E8 100%) !important;
    }
    /* Style sliders */
    .stSlider > div[data-baseweb="slider"] > div {
        background: linear-gradient(90deg, #FFD6E8 0%, #BFD4FF 100%) !important;
        border-radius: 8px !important;
    }
    .stSlider .rc-slider-track {
        background: #BFD4FF !important;
    }
    .stSlider .rc-slider-handle {
        border: 2px solid #FFD6E8 !important;
        background: #BFD4FF !important;
    }
    /* Style expander and subheader backgrounds */
    .stExpander, .stExpanderHeader, .stSubheader {
        background: linear-gradient(90deg, #FFD6E8 0%, #BFD4FF 100%) !important;
        color: black !important;
        border-radius: 12px !important;
    }
    /* Style info/warning boxes */
    .stAlert {
        background: linear-gradient(90deg, #FFD6E8 0%, #BFD4FF 100%) !important;
        color: black !important;
        border-radius: 12px !important;
    }
    /* Style all labels to black */
    label, .css-1cpxqw2, .css-1v0mbdj, .css-10trblm {
        color: black !important;
        font-weight: 600 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar Navigation ---
pages = [
    "Dashboard",
    "Add Product",
    "Supervisor Agent",
    "Pricing Analysis",
    "Demand Analysis",
    "Inventory Analysis",
    "Competitor Monitoring",
    "Comprehensive Analysis",
    "History"
]

st.sidebar.title("Dynamic Pricing Agentic System")
page = st.sidebar.radio("Go to", pages)

# --- Local Product Management (not persisted) ---
if 'products' not in st.session_state:
    st.session_state['products'] = []

# --- Helper Functions for API Calls ---
def supervisor_run(product_name: str):
    try:
        resp = requests.post(f"{API_URL}/agents/supervisor", json={"product_name": product_name})
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def get_pricing_history(product_id: str, days: int = 30):
    try:
        resp = requests.get(f"{API_URL}/agents/supervisor/history/{product_id}?days={days}")
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def pricing_analyze(product_id: str, include_forecast: bool = True):
    try:
        resp = requests.post(f"{API_URL}/agents/pricing/analyze", json={"product_id": product_id, "include_forecast": include_forecast})
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def get_pricing_recommendations(product_id: str):
    try:
        resp = requests.get(f"{API_URL}/agents/pricing/recommendations/{product_id}")
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def get_optimal_price(product_id: str):
    try:
        resp = requests.get(f"{API_URL}/agents/pricing/optimal-price/{product_id}")
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def demand_analyze(product_id: str, days: int = 30):
    try:
        resp = requests.post(f"{API_URL}/agents/demand/analyze", json={"product_id": product_id, "days": days})
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def get_demand_score(product_id: str):
    try:
        resp = requests.get(f"{API_URL}/agents/demand/score/{product_id}")
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def inventory_analyze(product_id: str, days_ahead: int = 30):
    try:
        resp = requests.post(f"{API_URL}/agents/inventory/analyze", json={"product_id": product_id, "days_ahead": days_ahead})
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def get_inventory_health(product_id: str):
    try:
        resp = requests.get(f"{API_URL}/agents/inventory/health/{product_id}")
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def get_inventory_optimization(product_id: str):
    try:
        resp = requests.get(f"{API_URL}/agents/inventory/optimize/{product_id}")
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def competitor_monitor(product_id: str):
    try:
        resp = requests.post(f"{API_URL}/agents/competitor/monitor", json={"product_id": product_id})
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def get_similar_products(product_name: str, category: str = "", limit: int = 5):
    try:
        params = f"?category={category}&limit={limit}" if category else f"?limit={limit}"
        resp = requests.get(f"{API_URL}/agents/competitor-monitoring/similar/{product_name}{params}")
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def comprehensive_analyze(product_id: str):
    try:
        resp = requests.post(f"{API_URL}/agents/comprehensive-analysis", json={"product_id": product_id})
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def add_product_api(product):
    try:
        resp = requests.post(f"{API_URL}/products", json=product)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return {"status": "error", "message": "Failed to add product."}

def render_status_badge(status):
    color = {
        "success": "#4BB543",
        "error": "#FF4B4B",
        "healthy": "#4BB543",
        "attention_required": "#FFD600",
        "critical": "#FF4B4B",
        "low": "#BFD4FF",
        "moderate": "#FFD6E8",
        "high": "#FF4B4B"
    }.get(str(status).lower(), "#BFD4FF")
    return f'<span style="background:{color};color:black;padding:0.3em 0.8em;border-radius:1em;font-weight:600;">{status}</span>'

def render_confidence_bar(confidence):
    pct = int(float(confidence) * 100)
    bar = f"<div style='background:linear-gradient(90deg,#FFD6E8 {pct}%,#BFD4FF {pct}%);border-radius:8px;width:100%;height:18px;'><div style='text-align:center;font-size:0.9em;color:black;font-weight:600;'>{pct}%</div></div>"
    return bar

def render_recommendations(recs):
    if isinstance(recs, list):
        return "<ul>" + "".join(f"<li>{r}</li>" for r in recs) + "</ul>"
    elif isinstance(recs, dict):
        out = ""
        for k, v in recs.items():
            if v:
                out += f"<b>{k.replace('_',' ').title()}:</b> " + render_recommendations(v) + "<br>"
        return out
    elif recs:
        return f"<span>{recs}</span>"
    return "<span>No recommendations</span>"

def render_reasoning_chain(chain):
    if isinstance(chain, list):
        return "<ol>" + "".join(f"<li>{r}</li>" for r in chain) + "</ol>"
    return chain

def render_supervisor_response(resp):
    d = resp.get("data", {})
    st.markdown(f"""
    <div style='background:#fff;border-radius:16px;padding:1.5em 2em;margin-bottom:1em;'>
        <h3 style='margin-top:0;'>Supervisor Agent Result</h3>
        <b>Product:</b> {d.get('product_name','')}<br>
        <b>Category:</b> {d.get('category','')}<br>
        <b>Competitor:</b> {d.get('competitor_name','')}<br>
        <b>Competitor Price:</b> ₹{d.get('competitor_price','')}<br>
        <b>Scraped At:</b> {d.get('scraped_at','')}
    </div>
    """, unsafe_allow_html=True)

def render_pricing_recommendations(resp):
    recs = resp.get("recommendations", {})
    st.markdown(f"""
    <div style='background:#fff;border-radius:16px;padding:1.5em 2em;margin-bottom:1em;'>
        <h3 style='margin-top:0;'>Pricing Recommendations</h3>
        <b>Overall Recommendation:</b> {render_status_badge(recs.get('overall_recommendation',''))}<br>
        <b>Confidence:</b> {render_confidence_bar(recs.get('confidence',0))}<br>
        <b>Reasoning:</b> {render_reasoning_chain(recs.get('reasoning',[]))}<br>
        <hr>
        <b>Optimal Price Analysis:</b><br>
        <ul>
            <li>Current Price: ₹{recs.get('optimal_price_analysis',{}).get('current_price','')}</li>
            <li>Optimal Price: ₹{recs.get('optimal_price_analysis',{}).get('optimal_price','')}</li>
            <li>Price Change: {recs.get('optimal_price_analysis',{}).get('price_change_percent','')}%</li>
            <li>Recommendation: {render_status_badge(recs.get('optimal_price_analysis',{}).get('recommendation',''))}</li>
            <li>Confidence: {render_confidence_bar(recs.get('optimal_price_analysis',{}).get('confidence',0))}</li>
        </ul>
        <b>Elasticity Analysis:</b><br>
        <ul>
            <li>Elasticity: {recs.get('elasticity_analysis',{}).get('elasticity','')}</li>
            <li>Confidence: {render_confidence_bar(recs.get('elasticity_analysis',{}).get('confidence',0))}</li>
            <li>Message: {recs.get('elasticity_analysis',{}).get('message','')}</li>
        </ul>
        <b>Competitor Analysis:</b><br>
        <ul>
            <li>Recommendation: {recs.get('competitor_analysis',{}).get('recommendation','')}</li>
            <li>Error: {recs.get('competitor_analysis',{}).get('error','')}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def render_optimal_price(resp):
    op = resp.get("optimal_price", {})
    st.markdown(f"""
    <div style='background:#fff;border-radius:16px;padding:1.5em 2em;margin-bottom:1em;'>
        <h3 style='margin-top:0;'>Optimal Price</h3>
        <b>Current Price:</b> ₹{op.get('current_price','')}<br>
        <b>Optimal Price:</b> ₹{op.get('optimal_price','')}<br>
        <b>Price Change:</b> {op.get('price_change_percent','')}%<br>
        <b>Recommendation:</b> {render_status_badge(op.get('recommendation',''))}<br>
        <b>Confidence:</b> {render_confidence_bar(op.get('confidence',0))}
    </div>
    """, unsafe_allow_html=True)

def render_inventory_analysis(resp):
    d = resp.get("data", {})
    health = d.get("inventory_health", {})
    st.markdown(f"""
    <div style='background:#fff;border-radius:16px;padding:1.5em 2em;margin-bottom:1em;'>
        <h3 style='margin-top:0;'>Inventory Health</h3>
        <b>Status:</b> {render_status_badge(health.get('inventory_status',''))}<br>
        <b>Urgency:</b> {render_status_badge(health.get('urgency_level',''))}<br>
        <b>Current Stock:</b> {health.get('current_stock','')}<br>
        <b>Reorder Point:</b> {health.get('reorder_point','')}<br>
        <b>Max Stock:</b> {health.get('max_stock','')}<br>
        <b>Recommendations:</b> {render_recommendations(health.get('recommendations',[]))}<br>
        <b>Last Updated:</b> {health.get('last_updated','')}
    </div>
    """, unsafe_allow_html=True)
    # Inventory Optimization
    opt = d.get("inventory_optimization", {})
    if opt:
        st.markdown(f"""
        <div style='background:#fff;border-radius:16px;padding:1.5em 2em;margin-bottom:1em;'>
            <h4>Inventory Optimization</h4>
            {render_recommendations(opt.get('recommendations',{}))}
            <b>Metrics:</b> {render_recommendations(opt.get('metrics',{}))}
        </div>
        """, unsafe_allow_html=True)
    # Reasoning Chain
    if d.get("reasoning_chain"):
        st.markdown(f"<b>Reasoning Chain:</b> {render_reasoning_chain(d.get('reasoning_chain'))}", unsafe_allow_html=True)
    # Reflection
    if d.get("reflection"):
        st.markdown(f"<b>Reflection:</b> {d.get('reflection')}", unsafe_allow_html=True)

def render_competitor_monitoring(resp):
    st.success(resp.get("message", "Competitor monitoring completed successfully"))

def render_similar_products(resp):
    prods = resp.get("similar_products", [])
    if prods:
        st.markdown("<b>Similar Products:</b>", unsafe_allow_html=True)
        st.table([
            {
                "Product Name": p.get("product_name"),
                "Category": p.get("category"),
                "Competitor": p.get("competitor_name"),
                "Price": p.get("competitor_price"),
                "Similarity": f"{p.get('similarity_score',0):.2f}"
            } for p in prods
        ])
    else:
        st.info("No similar products found.")

def render_comprehensive_analysis(resp):
    d = resp.get("data", {})
    st.markdown(f"<h3>Comprehensive Analysis</h3>", unsafe_allow_html=True)
    # Overall Assessment
    oa = d.get("overall_assessment", {})
    st.markdown(f"<b>Overall Status:</b> {render_status_badge(oa.get('status',''))} <b>Confidence:</b> {render_confidence_bar(oa.get('confidence',0))}", unsafe_allow_html=True)
    if oa.get("priority_actions"):
        st.markdown(f"<b>Priority Actions:</b> {render_recommendations(oa.get('priority_actions'))}", unsafe_allow_html=True)
    if oa.get("recommendations"):
        st.markdown(f"<b>Recommendations:</b> {render_recommendations(oa.get('recommendations'))}", unsafe_allow_html=True)
    # Pricing
    if d.get("pricing_analysis"):
        st.markdown("<b>Pricing Analysis:</b>", unsafe_allow_html=True)
        st.json(d["pricing_analysis"])
    # Demand
    if d.get("demand_analysis"):
        st.markdown("<b>Demand Analysis:</b>", unsafe_allow_html=True)
        st.json(d["demand_analysis"])
    # Inventory
    if d.get("inventory_analysis"):
        st.markdown("<b>Inventory Analysis:</b>", unsafe_allow_html=True)
        st.json(d["inventory_analysis"])
    # Competitor
    if d.get("competitor_analysis"):
        st.markdown("<b>Competitor Analysis:</b>", unsafe_allow_html=True)
        st.json(d["competitor_analysis"])

def render_history(resp):
    hist = resp.get("history", [])
    if hist:
        st.markdown("<b>Pricing History:</b>", unsafe_allow_html=True)
        st.table(hist)
    else:
        st.info("No pricing history available.")

def render_error(resp):
    st.error(resp.get("message", "An error occurred."))

# --- Dashboard Page ---
if page == "Dashboard":
    st.markdown('<div class="dashboard-title">Dynamic Pricing Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-subtitle">Explore our comprehensive suite of AI-powered pricing tools designed to optimize your e-commerce business.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    # Optionally, show a summary for each locally managed product below
    if st.session_state['products']:
        st.markdown('<div class="dashboard-title" style="font-size:2rem;margin-top:2rem;">Product Snapshots</div>', unsafe_allow_html=True)
        for p in st.session_state['products']:
            st.subheader(f"Product: {p['name']} (ID: {p['id']})")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**Pricing**")
                recs = get_pricing_recommendations(p['id'])
                if recs:
                    st.json(recs)
            with col2:
                st.write("**Demand**")
                score = get_demand_score(p['id'])
                if score:
                    st.json(score)
            with col3:
                st.write("**Inventory**")
                health = get_inventory_health(p['id'])
                if health:
                    st.json(health)
    else:
        st.info("No products in local list. Add products in any agent page.")

# --- Add Product Page ---
if page == "Add Product":
    st.title("Add Product")
    with st.form("add_product_form"):
        id = st.text_input("Product ID", placeholder="Enter Product ID")
        name = st.text_input("Product Name", placeholder="Enter Product Name")
        category = st.text_input("Category", placeholder="Enter Category")
        base_price = st.number_input("Base Price", min_value=0.0, step=0.01, format="%0.2f")
        current_price = st.number_input("Current Price", min_value=0.0, step=0.01, format="%0.2f")
        cost_price = st.number_input("Cost Price", min_value=0.0, step=0.01, format="%0.2f")
        stock_level = st.number_input("Stock Level", min_value=0, step=1)
        demand_score = st.number_input("Demand Score", min_value=0.0, max_value=1.0, step=0.01, format="%0.2f")
        sales_velocity = st.number_input("Sales Velocity", min_value=0.0, step=0.01, format="%0.2f")
        price_elasticity = st.number_input("Price Elasticity", min_value=0.0, step=0.01, format="%0.2f")
        market_position = st.selectbox("Market Position", ["premium", "mid-range", "budget"], index=1)
        is_active = st.checkbox("Is Active", value=True)
        submitted = st.form_submit_button("Add Product")
        if submitted:
            product = {
                "id": id,
                "name": name,
                "category": category,
                "base_price": base_price,
                "current_price": current_price,
                "cost_price": cost_price,
                "stock_level": stock_level,
                "demand_score": demand_score,
                "sales_velocity": sales_velocity,
                "price_elasticity": price_elasticity,
                "market_position": market_position,
                "is_active": is_active
            }
            result = add_product_api(product)
            if result["status"] == "success":
                st.success("Product added!")
                # Add to local list
                st.session_state['products'].append({"name": name, "id": id})
            else:
                st.error(result.get("message", "Failed to add product."))

# --- Supervisor Agent Page ---
elif page == "Supervisor Agent":
    st.title("Supervisor Agent")
    product_name = st.text_input("Product Name", placeholder="Enter Product Name")
    if st.button("Run Supervisor Agent"):
        with st.spinner("Running supervisor agent..."):
            result = supervisor_run(product_name)
            if result:
                if result.get("status") == "success":
                    render_supervisor_response(result)
                else:
                    render_error(result)
                # Add to local products if not present
                found = any(p['name'] == product_name for p in st.session_state['products'])
                if not found:
                    st.session_state['products'].append({'name': product_name, 'id': product_name})
            else:
                st.error("Failed to run supervisor agent.")

# --- Pricing Analysis Page ---
elif page == "Pricing Analysis":
    st.title("Pricing Analysis")
    product_id = st.selectbox("Select Product", [p['id'] for p in st.session_state['products']], key="pricing_select") if st.session_state['products'] else st.text_input("Product ID", placeholder="Enter Product ID", key="pricing_input")
    include_forecast = st.checkbox("Include Forecast", value=True)
    if st.button("Run Pricing Analysis"):
        with st.spinner("Running pricing analysis..."):
            result = pricing_analyze(product_id, include_forecast)
            if result:
                if result.get("status") == "success":
                    render_supervisor_response(result) if result.get("message","" ).lower().startswith("supervisor") else st.json(result)
                else:
                    render_error(result)
            else:
                st.error("Failed to run pricing analysis.")
    if st.button("Get Pricing Recommendations"):
        with st.spinner("Fetching recommendations..."):
            recs = get_pricing_recommendations(product_id)
            if recs:
                if recs.get("status") == "success":
                    render_pricing_recommendations(recs)
                else:
                    render_error(recs)
            else:
                st.error("Failed to fetch recommendations.")
    if st.button("Get Optimal Price"):
        with st.spinner("Fetching optimal price..."):
            opt = get_optimal_price(product_id)
            if opt:
                if opt.get("status") == "success":
                    render_optimal_price(opt)
                else:
                    render_error(opt)
            else:
                st.error("Failed to fetch optimal price.")

# --- Demand Analysis Page ---
elif page == "Demand Analysis":
    st.title("Demand Analysis")
    product_id = st.selectbox("Select Product", [p['id'] for p in st.session_state['products']], key="demand_select") if st.session_state['products'] else st.text_input("Product ID", placeholder="Enter Product ID", key="demand_input")
    days = st.slider("Days to Analyze", min_value=7, max_value=90, value=30)
    if st.button("Run Demand Analysis"):
        with st.spinner("Running demand analysis..."):
            result = demand_analyze(product_id, days)
            if result:
                st.json(result)
            else:
                st.error("Failed to run demand analysis.")
    if st.button("Get Demand Score"):
        with st.spinner("Fetching demand score..."):
            score = get_demand_score(product_id)
            if score:
                st.json(score)
            else:
                st.error("Failed to fetch demand score.")

# --- Inventory Analysis Page ---
elif page == "Inventory Analysis":
    st.title("Inventory Analysis")
    product_id = st.selectbox("Select Product", [p['id'] for p in st.session_state['products']], key="inventory_select") if st.session_state['products'] else st.text_input("Product ID", placeholder="Enter Product ID", key="inventory_input")
    days_ahead = st.slider("Days Ahead", min_value=7, max_value=90, value=30)
    if st.button("Run Inventory Analysis"):
        with st.spinner("Running inventory analysis..."):
            result = inventory_analyze(product_id, days_ahead)
            if result:
                if result.get("status") == "success":
                    render_inventory_analysis(result)
                else:
                    render_error(result)
            else:
                st.error("Failed to run inventory analysis.")
    if st.button("Get Inventory Health"):
        with st.spinner("Fetching inventory health..."):
            health = get_inventory_health(product_id)
            if health:
                if health.get("status") == "success":
                    render_inventory_analysis({"data": {"inventory_health": health.get("health", {})}})
                else:
                    render_error(health)
            else:
                st.error("Failed to fetch inventory health.")
    if st.button("Get Inventory Optimization"):
        with st.spinner("Fetching inventory optimization..."):
            opt = get_inventory_optimization(product_id)
            if opt:
                if opt.get("status") == "success":
                    render_inventory_analysis({"data": {"inventory_optimization": opt.get("optimization", {})}})
                else:
                    render_error(opt)
            else:
                st.error("Failed to fetch inventory optimization.")

# --- Competitor Monitoring Page ---
elif page == "Competitor Monitoring":
    st.title("Competitor Monitoring")
    product_id = st.selectbox("Select Product", [p['id'] for p in st.session_state['products']], key="competitor_select") if st.session_state['products'] else st.text_input("Product ID", placeholder="Enter Product ID", key="competitor_input")
    if st.button("Run Competitor Monitoring"):
        with st.spinner("Running competitor monitoring..."):
            result = competitor_monitor(product_id)
            if result:
                if result.get("status") == "success":
                    render_competitor_monitoring(result)
                else:
                    render_error(result)
            else:
                st.error("Failed to run competitor monitoring.")
    st.subheader("Find Similar Products")
    product_name = st.text_input("Product Name for Similar Search", value=product_id, placeholder="Enter Product Name", key="similar_name")
    category = st.text_input("Category (optional)", placeholder="Enter Category (optional)", key="similar_category")
    limit = st.slider("Limit", min_value=1, max_value=20, value=5)
    if st.button("Find Similar"):
        with st.spinner("Searching for similar products..."):
            sim = get_similar_products(product_name, category, limit)
            if sim:
                if sim.get("status") == "success":
                    render_similar_products(sim)
                else:
                    render_error(sim)
            else:
                st.error("Failed to find similar products.")

# --- Comprehensive Analysis Page ---
elif page == "Comprehensive Analysis":
    st.title("Comprehensive Analysis")
    product_id = st.selectbox("Select Product", [p['id'] for p in st.session_state['products']], key="comprehensive_select") if st.session_state['products'] else st.text_input("Product ID", placeholder="Enter Product ID", key="comprehensive_input")
    if st.button("Run Comprehensive Analysis"):
        with st.spinner("Running comprehensive analysis..."):
            result = comprehensive_analyze(product_id)
            if result:
                if result.get("status") == "success":
                    render_comprehensive_analysis(result)
                else:
                    render_error(result)
            else:
                st.error("Failed to run comprehensive analysis.")

# --- History Page ---
elif page == "History":
    st.title("Pricing History")
    product_id = st.selectbox("Select Product", [p['id'] for p in st.session_state['products']], key="history_select") if st.session_state['products'] else st.text_input("Product ID", placeholder="Enter Product ID", key="history_input")
    days = st.slider("Days", min_value=7, max_value=90, value=30)
    if st.button("Get Pricing History"):
        with st.spinner("Fetching pricing history..."):
            hist = get_pricing_history(product_id, days)
            if hist:
                if hist.get("status") == "success":
                    render_history(hist)
                else:
                    render_error(hist)
            else:
                st.error("Failed to fetch pricing history.") 