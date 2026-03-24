import streamlit as st

# --- DATABASE: CALIBRATED TO BOSS'S 105-HOUR CHART ---
# Units are Man-Hours (Pipe per ft, Others per each) [cite: 7]
labor_db = {
    "Pipe (per ft)": {0.5: 0.06, 0.75: 0.07, 1.0: 0.09, 1.25: 0.12, 1.5: 0.14, 2.0: 0.21, 2.5: 0.29, 3.0: 0.37},
    "90° Elbow": {0.5: 0.46, 0.75: 0.46, 1.0: 0.52, 1.25: 0.63, 1.5: 0.69, 2.0: 0.86, 2.5: 1.27, 3.0: 1.67},
    "Tee": {0.5: 0.63, 0.75: 0.63, 1.0: 0.69, 1.25: 0.86, 1.5: 0.92, 2.0: 1.15, 2.5: 1.61, 3.0: 2.13},
    "Union": {0.5: 0.69, 0.75: 0.69, 1.0: 0.75, 1.25: 0.98, 1.5: 1.04, 2.0: 1.32, 2.5: 1.84, 3.0: 2.42},
    "Ball Valve": {0.5: 0.92, 0.75: 0.92, 1.0: 1.04, 1.25: 1.27, 1.5: 1.38, 2.0: 1.73, 2.5: 2.53, 3.0: 3.22},
    "Hanger/Split Clamp": {"Any": 0.29}, # Includes rod and fastener [cite: 9]
    "Galv Strut (each)": {"Any": 0.58},
    "Misc (Nipples/Caps)": {"Any": 0.35}
}

st.set_page_config(page_title="MJ Mechanical Estimator", page_icon="🔧")

st.title("🔧 MJ Mechanical Sales Estimator")
st.info("Calibrated for Threaded Gas Pipe Projects")

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("Site Conditions")
    condition = st.radio("Working Environment", ["Standard (1.0x)", "Ladder Work (1.15x)", "Crawlspace (1.3x)"])
    multiplier = 1.0 if "Standard" in condition else 1.15 if "Ladder" in condition else 1.3
    
    st.divider()
    include_setup = st.checkbox("Heavy Machine Setup (2.0 hrs)", value=True)
    concrete = st.checkbox("Concrete Anchoring (+0.15/ea)", value=True)

# --- TRACKING THE LIST ---
if 'list' not in st.session_state:
    st.session_state.list = []

# --- INPUTS ---
c1, c2, c3 = st.columns([3, 2, 2])
with c1:
    item = st.selectbox("Material", list(labor_db.keys()))
with c2:
    if "Any" in labor_db[item]:
        size = "Any"
        st.text("Universal")
    else:
        size = st.selectbox("Size", [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0])
with c3:
    qty = st.number_input("Qty/Feet", min_value=0.0, value=1.0, step=1.0)

if st.button("➕ Add to Quote"):
    st.session_state.list.append({"name": item, "size": size, "qty": qty})

# --- RESULTS ---
total_hrs = 2.0 if include_setup else 0.0

if st.session_state.list:
    st.subheader("Current Quote Breakdown")
    for entry in st.session_state.list:
        base_labor = labor_db[entry['name']][entry['size']]
        anchor_time = 0.15 if (concrete and "Hanger" in entry['name']) else 0
        
        subtotal = (base_labor + anchor_time) * entry['qty'] * multiplier
        total_hrs += subtotal
        
        label = f"{entry['size']}\" " if entry['size'] != "Any" else ""
        st.write(f"**{entry['qty']}x** {label}{entry['name']} → {subtotal:.2f} hrs")

    st.divider()
    st.metric("Total Estimated Labor", f"{total_hrs:.2f} Hours")
    st.write(f"🕒 **Estimated Duration:** {(total_hrs/16):.1f} Days (2-Man Crew)")

    if st.button("Clear All Data"):
        st.session_state.list = []
        st.rerun()
