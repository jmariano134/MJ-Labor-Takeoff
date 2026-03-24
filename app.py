import streamlit as st

# Safe import to prevent the 'Exit Code' from breaking the whole app
try:
    from pypdf import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# --- CALIBRATED DATABASE (Matches Boss's 105-Hour Chart) ---
labor_db = {
    "Pipe (per ft)": {0.5: 0.06, 0.75: 0.07, 1.0: 0.09, 1.25: 0.12, 1.5: 0.14, 2.0: 0.21, 2.5: 0.29, 3.0: 0.37},
    "90° Elbow": {0.5: 0.46, 0.75: 0.46, 1.0: 0.52, 1.25: 0.63, 1.5: 0.69, 2.0: 0.86, 2.5: 1.27, 3.0: 1.67},
    "Tee": {0.5: 0.63, 0.75: 0.63, 1.0: 0.69, 1.25: 0.86, 1.5: 0.92, 2.0: 1.15, 2.5: 1.61, 3.0: 2.13},
    "Union": {0.5: 0.69, 0.75: 0.69, 1.0: 0.75, 1.25: 0.98, 1.5: 1.04, 2.0: 1.32, 2.5: 1.84, 3.0: 2.42},
    "Ball Valve": {0.5: 0.92, 0.75: 0.92, 1.0: 1.04, 1.25: 1.27, 1.5: 1.38, 2.0: 1.73, 2.5: 2.53, 3.0: 3.22},
    "Hanger/Split Clamp": {"Any": 0.29},
    "Galv Strut (each)": {"Any": 0.58},
    "Misc (Nipples/Caps)": {"Any": 0.35}
}

st.set_page_config(page_title="MJ Mechanical Estimator", layout="centered")
st.title("🔧 MJ Mechanical Sales Tool")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Job Settings")
    condition = st.radio("Environment", ["Standard (1.0x)", "Ladder Work (1.15x)", "Crawlspace (1.3x)"])
    mult = 1.0 if "Standard" in condition else 1.15 if "Ladder" in condition else 1.3
    
    st.divider()
    if not PDF_SUPPORT:
        st.warning("PDF Library Loading... Use Manual Entry below.")
    else:
        uploaded_file = st.file_uploader("Upload Windustrial Slip", type="pdf")
        if uploaded_file:
            st.success("Slip Uploaded!")

# --- APP LOGIC ---
if 'estimate' not in st.session_state:
    st.session_state.estimate = []

col1, col2, col3 = st.columns([3, 2, 2])
with col1:
    item = st.selectbox("Material", list(labor_db.keys()))
with col2:
    sz = "Any" if "Any" in labor_db[item] else st.selectbox("Size", [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0])
with col3:
    qty = st.number_input("Qty/Feet", min_value=0.0, step=1.0)

if st.button("➕ Add to Quote"):
    st.session_state.estimate.append({"name": item, "size": sz, "qty": qty})

# --- RESULTS ---
total = 2.0 # Standard Setup Buffer
if st.session_state.estimate:
    st.subheader("Project Breakdown")
    for e in st.session_state.estimate:
        val = labor_db[e['name']][e['size']]
        sub = val * e['qty'] * mult
        total += sub
        st.write(f"**{e['qty']}** x {e['size']}\" {e['name']} : {sub:.2f} hrs")

    st.divider()
    st.metric("Total Labor", f"{total:.2f} Hours")
    st.write(f"🗓️ **Estimated Time:** {(total/16):.1f} Days (2-Man Crew)")
    
    if st.button("Clear List"):
        st.session_state.estimate = []
        st.rerun()
