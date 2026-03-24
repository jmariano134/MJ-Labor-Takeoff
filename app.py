import streamlit as st
import re
try:
    from pypdf import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# --- CALIBRATED DATABASE (Boss's 105-Hour Chart) ---
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

if 'estimate' not in st.session_state:
    st.session_state.estimate = []

# --- PDF PARSING ENGINE ---
def parse_windustrial_slip(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    # 1. Extract Pipes (Looking for: Quantity + Size + 'PIPE')
    # Matches patterns like "147 1-1/4 STD BLK...PIPE"
    pipe_pattern = r"(\d+)\s+([\d/-]+)\s+STD BLK.*?PIPE"
    pipes = re.findall(pipe_pattern, text)
    for qty, size_str in pipes:
        # Convert "1-1/4" to 1.25
        size_val = 1.25 if "1-1/4" in size_str else 1.5 if "1-1/2" in size_str else 1.0 if size_str == "1" else 0.75
        st.session_state.estimate.append({"name": "Pipe (per ft)", "size": size_val, "qty": float(qty)})

    # 2. Extract Fittings (Elbows/Tees/Valves)
    fitting_map = {"ELBOW 90": "90° Elbow", "TEE": "Tee", "UNION": "Union", "GAS BV": "Ball Valve", "SPLIT CLAMP": "Hanger/Split Clamp"}
    for keyword, db_name in fitting_map.items():
        # Matches patterns like "10 WI 1-1/4 ELBOW 90 BLK"
        pattern = r"(\d+)\s+.*?([\d/-]+)?\s+.*?" + keyword
        matches = re.findall(pattern, text)
        for qty, size_str in matches:
            size_val = "Any" if db_name == "Hanger/Split Clamp" else 1.25 if "1-1/4" in str(size_str) else 1.0
            st.session_state.estimate.append({"name": db_name, "size": size_val, "qty": float(qty)})

# --- SIDEBAR ---
with st.sidebar:
    st.header("Job Settings")
    condition = st.radio("Environment", ["Standard (1.0x)", "Ladder Work (1.15x)", "Crawlspace (1.3x)"])
    mult = 1.0 if "Standard" in condition else 1.15 if "Ladder" in condition else 1.3
    
    st.divider()
    if PDF_SUPPORT:
        uploaded_file = st.file_uploader("Upload Windustrial Slip", type="pdf")
        if uploaded_file and st.button("🚀 Scan & Load Slip"):
            parse_windustrial_slip(uploaded_file)
            st.success("Items loaded! Verify sizes below.")

# --- MANUAL INPUT & DISPLAY ---
st.subheader("Current Project Breakdown")
# [Rest of your manual input and total display code remains the same]
