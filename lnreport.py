import streamlit as st
from datetime import datetime

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="HemePath Synoptic Reporter", layout="wide", page_icon="🔬")

# Custom CSS to compact the UI and improve readability
st.markdown("""
<style>
    .report-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4e8cff;
        font-family: 'Courier New', monospace;
    }
    .warning-box {
        background-color: #ffeeba;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ffdf7e;
        color: #856404;
    }
    div.stButton > button:first-child {
        background-color: #4e8cff;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: SPECIMEN TRIAGE ---
with st.sidebar:
    st.header("1. Specimen Triage")
    
    specimen_type = st.selectbox(
        "Specimen Category",
        ["Lymph Node", "Skin / Cutaneous", "Extranodal (Soft Tissue/Organ)"]
    )
    
    procedure = st.selectbox(
        "Procedure Type",
        ["Needle Core Biopsy", "Excisional Biopsy", "Incisional Biopsy", "Fine Needle Aspiration"] 
        if specimen_type != "Skin / Cutaneous" else 
        ["Punch Biopsy", "Shave Biopsy", "Excision", "Wide Local Excision"]
    )
    
    # Logic: Core Biopsy Limitations (Derived from Case 1 & 5 analysis)
    is_limited = False
    limitation_reason = []
    
    if "Core" in procedure:
        st.subheader("Core Assessment")
        core_integrity = st.radio("Integrity", ["Intact/Long", "Fragmented/Minute", "Crushed"], index=0)
        core_count = st.number_input("Number of Cores", 1, 10, 1)
        
        if core_integrity != "Intact/Long":
            is_limited = True
            limitation_reason.append(f"specimen consists of {core_integrity.lower()} cores")
            
    if "Shave" in procedure:
        st.info("⚠️ Shave biopsy may limit evaluation of deep subcutis (e.g., SPTCL vs LE).")
        is_limited = True
        limitation_reason.append("superficial nature of the biopsy")

    st.divider()
    st.caption("Reporting Logic v1.0")

# --- MAIN COLUMN STRUCTURE ---
col_inputs, col_preview = st.columns([1.2, 1])

with col_inputs:
    st.title("HemePath Reporter")
    
    # TABS for Different Workflows
    tab_micro, tab_ihc, tab_diagnosis = st.tabs(["2. Microscopic Features", "3. IHC & Flow", "4. Diagnostic Synthesis"])

    # --- TAB 2: MICROSCOPIC DESCRIPTION ---
    with tab_micro:
        st.subheader("Architectural Pattern")
        
        # Dynamic inputs based on Specimen Type
        if specimen_type == "Lymph Node":
            arch_pattern = st.multiselect(
                "Growth Pattern",
                ["Nodular/Follicular", "Diffuse", "Interfollicular/Paracortical", "Sinusoidal", "Mantle Zone Expansion", "Marginal Zone Expansion"],
                default=["Diffuse"]
            )
            
            follicle_details = ""
            if "Nodular/Follicular" in arch_pattern:
                st.markdown("---")
                c1, c2 = st.columns(2)
                with c1:
                    f_polarization = st.checkbox("Polarization (Reactive)")
                    f_tbm = st.checkbox("Tingible Body Macrophages")
                with c2:
                    f_shape = st.selectbox("Follicle Shape", ["Variably sized/Ovoid", "Crowded/Back-to-back", "Regressed/Atrophic", "Floral/Castlemanoid"])
                
                # Logic text builder for follicles
                follicle_details = f"showing a {f_shape.lower()} appearance. "
                if f_polarization: follicle_details += "Germinal centers show polarization. "
                if f_tbm: follicle_details += "Tingible body macrophages are present. "
                else: follicle_details += "Tingible body macrophages are inconspicuous/absent. "

        elif specimen_type == "Skin / Cutaneous":
            st.subheader("Epidermal & Dermal Interface")
            epidermis = st.multiselect("Epidermal Findings", 
                                     ["Epidermotropism", "Pautrier Microabscesses", "Spongiosis", "Haloed Lymphocytes", "Ulceration"],
                                     default=[])
            dermis = st.selectbox("Dermal Pattern", ["Band-like (Lichenoid)", "Perivascular/Periadnexal", "Nodular/Diffuse", "Bottom-heavy"])
            subcutis = st.checkbox("Involvement of Subcutis (Panniculitis-like)")
            
            skin_text_block = f"The epidermis shows {', '.join(epidermis).lower() if epidermis else 'no significant changes'}. "
            skin_text_block += f"There is a {dermis.lower()} infiltrate. "
            if subcutis: skin_text_block += "The infiltrate extends into the subcutaneous fat tissue. "

        st.markdown("---")
        st.subheader("Cytology & Background")
        c_cyto, c_bg = st.columns(2)
        
        with c_cyto:
            cell_size = st.select_slider("Dominant Cell Size", options=["Small", "Small-Medium", "Medium-Large", "Large", "Pleomorphic"])
            nuc_shape = st.selectbox("Nuclear Contours", ["Round/Regular", "Irregular/Cleaved", "Cerebriform", "Reniform/Kidney", "Multilobated (Popcorn)", "Hodgkin-like"])
            chromatin = st.selectbox("Chromatin", ["Condensed", "Vesicular/Open", "Fine/Dusty"])
            nucleoli = st.selectbox("Nucleoli", ["Inconspicuous", "Small basophilic", "Prominent central", "Multiple peripheral"])
            
        with c_bg:
            st.write("**Background Milieu**")
            bg_features = st.multiselect("Select all present:", 
                                       ["Eosinophils", "Plasma Cells", "Epithelioid Histiocytes", "High Endothelial Venules (HEV)", 
                                        "Sclerosis (Bands)", "Sclerosis (Fine)", "Necrosis", "Mummified cells"])

    # --- TAB 3: IHC & FLOW ---
    with tab_ihc:
        st.subheader("Immunophenotype")
        
        # Common Panels
        st.markdown("##### B-Cell Markers")
        b_col1, b_col2, b_col3, b_col4 = st.columns(4)
        cd20 = b_col1.selectbox("CD20", ["ND", "+", "-", "Subset"], index=0)
        cd10 = b_col2.selectbox("CD10", ["ND", "+", "-", "Subset"], index=0)
        bcl6 = b_col3.selectbox("BCL6", ["ND", "+", "-", "Subset"], index=0)
        bcl2 = b_col4.selectbox("BCL2", ["ND", "+", "-", "Subset"], index=0)
        
        mum1 = b_col1.selectbox("MUM1", ["ND", "+", "-", "Subset"], index=0)
        cyclind1 = b_col2.selectbox("Cyclin D1", ["ND", "+", "-", "Subset"], index=0)
        cd5 = b_col3.selectbox("CD5", ["ND", "+", "-", "Subset"], index=0)
        cmyc = b_col4.selectbox("MYC %", ["ND", "<40%", ">40%"], index=0)

        st.markdown("##### T-Cell / Hodgkin Markers")
        t_col1, t_col2, t_col3, t_col4 = st.columns(4)
        cd3 = t_col1.selectbox("CD3", ["ND", "+", "-", "Subset"], index=0)
        cd4 = t_col2.selectbox("CD4", ["ND", "+", "-", "Subset"], index=0)
        cd8 = t_col3.selectbox("CD8", ["ND", "+", "-", "Subset"], index=0)
        cd30 = t_col4.selectbox("CD30", ["ND", "+", "-", "Subset"], index=0)
        
        alk = t_col1.selectbox("ALK", ["ND", "+", "-"], index=0)
        pd1 = t_col2.selectbox("PD-1", ["ND", "+", "-", "Rosettes"], index=0)
        ebv = t_col3.selectbox("EBER", ["ND", "+", "-", "Rare cells"], index=0)
        ki67 = st.slider("Ki-67 Proliferation Index (%)", 0, 100, 10)

        # Molecular / Flow
        st.markdown("##### Ancillary Studies")
        flow_result = st.selectbox("Flow Cytometry", 
                                 ["Not performed", "Polytypic B-cells / No clonal T-cells", "Monotypic B-cell population identified", "Aberrant T-cell population identified"])
        fish_result = st.text_input("FISH/Molecular Findings (Optional)", placeholder="e.g. MYC rearrangement detected...")

    # --- TAB 4: DIAGNOSIS GENERATOR ---
    with tab_diagnosis:
        st.subheader("Diagnostic Synthesis")
        
        # DIAGNOSTIC LOGIC HELPERS
        dx_category = st.radio("Primary Differential", ["Reactive/Benign", "B-Cell Lymphoma", "T-Cell Lymphoma", "Hodgkin Lymphoma"], horizontal=True)
        
        suggested_diagnosis = ""
        diagnostic_comment = ""
        
        # 1. REACTIVE LOGIC
        if dx_category == "Reactive/Benign":
            subtype = st.selectbox("Reactive Pattern", ["Reactive Lymphoid Hyperplasia", "Dermatopathic Lymphadenopathy", "Castleman Disease (Hyaline Vascular)", "Rosai-Dorfman"])
            if subtype == "Reactive Lymphoid Hyperplasia":
                suggested_diagnosis = "REACTIVE LYMPHOID HYPERPLASIA."
                diagnostic_comment = "Flow cytometry and immunohistochemistry demonstrate no evidence of a clonal B-cell or aberrant T-cell population."

        # 2. B-CELL LOGIC
        elif dx_category == "B-Cell Lymphoma":
            b_subtype = st.selectbox("Entity", ["DLBCL, NOS", "Follicular Lymphoma", "Mantle Cell Lymphoma", "Marginal Zone Lymphoma", "CLL/SLL"])
            
            if b_subtype == "Follicular Lymphoma":
                grade = st.selectbox("Grading (WHO 5th / ICC)", ["Classic (Grade 1-2)", "Classic (Grade 3A)", "Follicular Large B-cell Lymphoma (Grade 3B)"])
                pattern_pct = st.selectbox("Pattern", ["Predominantly follicular (>75%)", "Follicular and Diffuse", "Predominantly diffuse"])
                suggested_diagnosis = f"FOLLICULAR LYMPHOMA, {grade.upper()}."
                diagnostic_comment = f"The neoplasm shows a {pattern_pct} growth pattern."
                if bcl2 == "-":
                    diagnostic_comment += " Note: The absence of BCL2 expression is atypical but does not exclude the diagnosis; correlation with BCL6 rearrangement is recommended."
            
            elif b_subtype == "DLBCL, NOS":
                # Hans Algorithm Logic
                coo = "Unable to determine"
                if cd10 == "+":
                    coo = "Germinal Center B-cell (GCB) type"
                elif cd10 == "-" and bcl6 == "-":
                    coo = "Activated B-cell (ABC)/Non-GCB type"
                elif cd10 == "-" and bcl6 == "+":
                    if mum1 == "+": coo = "Non-GCB type"
                    elif mum1 == "-": coo = "GCB type"
                
                suggested_diagnosis = f"DIFFUSE LARGE B-CELL LYMPHOMA, NOS, {coo.upper()}."
                
                # Double Expressor Logic
                if cmyc == ">40%" and bcl2 == "+":
                    diagnostic_comment += " The tumor cells co-express MYC and BCL2, consistent with 'double expressor' status (associated with aggressive clinical behavior)."

        # 3. T-CELL LOGIC
        elif dx_category == "T-Cell Lymphoma":
            t_subtype = st.selectbox("Entity", ["AITL / nTFHL-AI", "nTFHL-Follicular", "ALCL, ALK-positive", "ALCL, ALK-negative", "PTCL, NOS", "Mycosis Fungoides"])
            
            if "nTFHL" in t_subtype:
                tfh_markers = [m for m in [pd1, cd10, bcl6] if m == "+"] # Simplified list, in real app would include CXCL13/ICOS inputs
                suggested_diagnosis = f"NODAL T-FOLLICULAR HELPER CELL LYMPHOMA, {t_subtype.split('-')[-1].upper()} TYPE."
                if len(tfh_markers) < 2:
                    st.warning("⚠️ WHO 5th typically requires at least 2 TFH markers for this diagnosis.")
            
            elif t_subtype == "Mycosis Fungoides":
                suggested_diagnosis = "PERIPHERAL T-CELL LYMPHOMA, CONSISTENT WITH MYCOSIS FUNGOIDES."
                if "Epidermotropism" in epidermis:
                    diagnostic_comment = "The presence of epidermotropism supports the diagnosis."
                if flow_result == "Aberrant T-cell population identified":
                    diagnostic_comment += " Flow cytometry confirms an aberrant T-cell phenotype."

        # 4. HODGKIN LOGIC
        elif dx_category == "Hodgkin Lymphoma":
            hl_subtype = st.selectbox("Subtype", ["Classic Hodgkin Lymphoma, Nodular Sclerosis", "Classic Hodgkin Lymphoma, Mixed Cellularity", "NLPHL"])
            suggested_diagnosis = hl_subtype.upper() + "."
            if "Mummified cells" in bg_features:
                diagnostic_comment = "Background contains characteristic 'mummified' cells."

    # --- GENERATE BUTTON ---
    generate_btn = st.button("Generate Synoptic Report", type="primary")

# --- REPORT GENERATION LOGIC ---
if generate_btn:
    # 1. Construct Microscopic Description
    micro_text = ""
    
    # Sentence 1: Specimen & Architecture
    if specimen_type == "Lymph Node":
        micro_text += f"Sections of lymph node show {', '.join(arch_pattern).lower()} architecture. "
        if "Nodular/Follicular" in arch_pattern:
            micro_text += f"The follicles are {follicle_details}"
    elif specimen_type == "Skin / Cutaneous":
        micro_text += f"Sections of skin show {', '.join(epidermis).lower()}. "
        micro_text += f"Within the dermis, there is a {dermis.lower()} infiltrate. "

    # Sentence 2: Cytology
    micro_text += f"\nThe infiltrate is composed of {cell_size.lower()} lymphoid cells with {nuc_shape.lower()} nuclei, {chromatin.lower()} chromatin, and {nucleoli.lower()} nucleoli. "
    
    # Sentence 3: Background
    if bg_features:
        micro_text += f"The background milieu contains {', '.join(bg_features).lower()}. "
        if "High Endothelial Venules (HEV)" in bg_features:
            micro_text += "Arborizing high endothelial venules are prominent. "
            
    # Sentence 4: Core/Limit Disclaimer
    if is_limited:
        micro_text += f"\n\nNOTE: The specimen evaluation is limited by {', '.join(limitation_reason)}. "

    # Sentence 5: IHC Summary
    ihc_text = "\n\nImmunohistochemical studies performed on block [X] show the atypical cells are positive for "
    positives = []
    negatives = []
    
    # Helper to collect stains
    stain_map = {
        "CD20": cd20, "CD3": cd3, "CD10": cd10, "BCL6": bcl6, "BCL2": bcl2, 
        "Cyclin D1": cyclind1, "CD5": cd5, "CD30": cd30, "MUM1": mum1, "ALK": alk, "PD-1": pd1
    }
    
    for stain, result in stain_map.items():
        if result == "+": positives.append(stain)
        elif result == "-": negatives.append(stain)
        elif result == "Subset": positives.append(f"{stain} (subset)")
    
    if positives: ihc_text += ", ".join(positives) + ". "
    else: ihc_text += "no specific markers in the current panel. "
    
    if negatives: ihc_text += f"They are negative for {', '.join(negatives)}. "
    
    if cmyc != "ND": ihc_text += f"MYC is expressed in {cmyc} of cells. "
    ihc_text += f"The Ki-67 proliferation index is approximately {ki67}%."

    final_micro_desc = micro_text + ihc_text

    # 2. Construct Final Diagnosis
    final_dx = f"{specimen_type.upper()}, {procedure.upper()}:\n- {suggested_diagnosis}"
    
    if is_limited:
        final_dx += "\n- SEE NOTE."
        diagnostic_comment = f"NOTE: The specimen consists of {', '.join(limitation_reason)}, which limits complete architectural assessment. However, the immunophenotypic features are sufficient for the rendered diagnosis.\n\n" + diagnostic_comment
    
    if diagnostic_comment:
        final_dx += f"\n\nCOMMENT: {diagnostic_comment}"

    # --- PREVIEW COLUMN ---
    with col_preview:
        st.subheader("Generated Report")
        st.markdown("Copy and paste these fields into your LIS.")
        
        st.caption("Final Diagnosis")
        st.text_area("Dx", value=final_dx, height=200, label_visibility="collapsed")
        
        st.caption("Microscopic Description")
        st.text_area("Micro", value=final_micro_desc, height=400, label_visibility="collapsed")
        
        st.success("Report Generated.")

else:
    with col_preview:
        st.info("Select parameters on the left and click 'Generate Synoptic Report' to see the output here.")
        
        # Guide for the user
        with st.expander("Usage Guide & Logic"):
            st.markdown("""
            **1. Specimen Triage:**
            Selecting "Core Biopsy" and "Fragmented" will automatically append a "Limited Specimen" disclaimer to the final report (based on logic from Case 1 & 5).
            
            **2. Hans Algorithm:**
            For DLBCL, the app automatically calculates GCB vs Non-GCB based on your CD10, BCL6, and MUM1 inputs.
            
            **3. nTFHL Logic:**
            Selecting nTFHL subtypes triggers a check for TFH markers (PD1, CD10, BCL6) in the warning logic.
            
            **4. Reactive Cases:**
            Automatically generates the standard "Negative for clonal population" text.
            """)
