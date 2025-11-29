import streamlit as st
from datetime import datetime
from collections import defaultdict

# =========================================
# Utility / Constants (WHO 5 / ICC Entities)
# =========================================

# Strict WHO 5th (ICC/Bluebook) categorization
REACTIVE_ENTITIES = [
    "Reactive follicular hyperplasia (Polyclonal B/T)",
    "Paracortical (Interfollicular) hyperplasia",
    "Sinus histiocytosis / Rosai-Dorfman Disease",
    "Granulomatous lymphadenitis (Necrotizing/Non-Necrotizing)",
    "Dermatopathic lymphadenitis",
    "Atypical lymphoid hyperplasia (Indeterminate for Lymphoma)",
]

B_CELL_NODAL = [
    "Chronic lymphocytic leukemia / Small lymphocytic lymphoma (CLL/SLL)",
    "Mantle cell lymphoma, classic (MCL)",
    "Mantle cell lymphoma, blastoid/pleomorphic variant (MCL)",
    "Follicular lymphoma, classic (Grade 1-2)",
    "Follicular large B-cell lymphoma (Grade 3B)",
    "Diffuse large B-cell lymphoma, NOS (DLBCL, NOS)",
    "High-grade B-cell lymphoma (HGBL) with MYC/BCL2/BCL6 R",
    "Burkitt lymphoma",
    "Nodal Marginal Zone Lymphoma (NMZL)",
]

T_CELL_NODAL = [
    "Peripheral T-cell lymphoma, NOS (PTCL-NOS)",
    "Angioimmunoblastic T-cell lymphoma (AITL)",
    "Nodal T-follicular helper cell lymphoma (nTFHL), NOS",
    "Anaplastic large cell lymphoma (ALCL), ALK-positive",
    "Anaplastic large cell lymphoma (ALCL), ALK-negative",
]

CUTANEOUS_LYMPHOMA = [
    "Mycosis Fungoides (MF) / Sézary Syndrome (SS)",
    "Primary cutaneous CD30+ LPD (incl. LyP)",
    "Primary cutaneous follicle center lymphoma (PCFCL)",
    "Subcutaneous panniculitis-like T-cell lymphoma (SPTCL)",
    "Primary cutaneous acral CD8+ T-cell lymphoma",
]

# Set page configuration
st.set_page_config(
    page_title="HemePath Synoptic Reporter (WHO 5)",
    layout="wide",
    page_icon="🔬"
)

# Custom CSS for a professional, compact look
st.markdown("""
<style>
    .stApp {max-width: 1200px; margin: 0 auto;}
    .report-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
    }
    h1 {font-size: 2em;}
    h2 {font-size: 1.5em;}
</style>
""", unsafe_allow_html=True)

# Initialize session state for persistence
if "microscopic_text" not in st.session_state:
    st.session_state["microscopic_text"] = ""
if "final_diagnosis_text" not in st.session_state:
    st.session_state["final_diagnosis_text"] = ""
if "comment_text_input" not in st.session_state:
    st.session_state["comment_text_input"] = ""


# =========================================
# REPORT GENERATION FUNCTIONS
# =========================================

def generate_microscopic_text(inputs):
    """Builds the Microscopic Description based on UI inputs."""
    
    # Destructure inputs for readability
    site = inputs['site']
    specimen_class = inputs['specimen_class']
    procedure_type = inputs['procedure_type']
    integrity = inputs['integrity']
    
    arch = inputs['architecture']
    morph = inputs['morphology']
    bg_features = inputs['background_features']
    
    ihc_map = inputs['ihc_map']
    ki67 = inputs['ki67']
    flow = inputs['flow_result']

    text = ""
    limit_disclaimer = ""
    
    # 1. Specimen Triage (Core Biopsy/Limitation)
    if integrity != "Intact/Long":
        limit_disclaimer = f"The specimen ({procedure_type}) consists of {integrity.lower()} material, which limits complete architectural assessment of the entire lymph node."
        text += limit_disclaimer + " "
    
    # 2. General Architecture/Site
    if "Skin" in specimen_class:
        text += f"The {site} skin biopsy shows a {arch['skin_pattern'].lower()} infiltrate in the dermis. "
        if "Epidermotropism" in arch['skin_specifics']:
             text += "There is notable epidermotropism with small, haloed lymphocytes in the epidermis (Pautrier microabscesses absent/present). "
    elif "Node" in specimen_class:
        text += f"Sections of the {site} lymph node show the architecture is largely effaced by a proliferation with a {' / '.join(arch['pattern']).lower()} pattern. "
        
        # Follicular details
        if "Nodular/Follicular" in arch['pattern']:
            text += f"The follicles show {arch['follicle_zoning'].lower()} zoning and {arch['follicle_pattern'].lower()} growth. "

    # 3. Cytology & Morphology
    text += f"\n\n**Morphology:** The atypical population is composed of {morph['cell_size'].lower()} cells with {morph['nuclear_contour'].lower()} nuclei and {morph['chromatin'].lower()} chromatin. "
    
    if morph['nucleoli'] != "Inconspicuous/Absent":
        text += f"Nucleoli are {morph['nucleoli'].lower()}. "
        
    if morph['specific_shape']:
        text += f"Specific morphologic findings include: {morph['specific_shape'].lower()}. "
        
    # 4. Background & Milieu
    if bg_features:
        text += f"\n\n**Background:** The background is complex, containing {', '.join(bg_features).lower()}. "
        if "Epithelioid Histiocytes" in bg_features:
            text += "Epithelioid histiocyte clusters are scattered, a feature supportive of AITL/PTCL-NOS. "
        
    # 5. IHC Summary
    positives = [f"{m} ({s})" for m, s in ihc_map.items() if s in ("+", "Subset", "Focal")]
    negatives = [m for m, s in ihc_map.items() if s == "-"]
    
    text += "\n\n**Immunohistochemistry:** The atypical cells are positive for "
    text += ", ".join(positives) if positives else "no specific markers in the panel"
    text += f" and negative for {', '.join(negatives)}."
    text += f" The Ki-67 proliferation index is approximately {ki67}%."
    
    # 6. Ancillary Summary
    if flow != "Not performed":
        text += f" **Flow Cytometry:** {flow}. "

    return text

def generate_final_diagnosis_text(inputs, dx_tools):
    """Builds the Final Diagnosis, including grade, stage, and comments."""
    
    primary_entity = inputs['primary_entity']
    site = inputs['site']
    procedure_type = inputs['procedure_type']
    integrity = inputs['integrity']
    
    comment_text = inputs['comment']
    reco_text = inputs['recommendations']

    final_dx = f"{site.upper()}, {procedure_type.upper()}:\n"
    
    # 1. Primary Diagnosis Line
    dx_line = f"- {primary_entity.upper()}."

    # 2. Grading/Sub-classification (Dynamic based on entity)
    sub_lines = []
    
    # DLBCL/HGBL
    if "DLBCL" in primary_entity or "HGBL" in primary_entity:
        sub_lines.append(f"Cell of Origin: {dx_tools['coo_text']}")
        if dx_tools['de_status'] != "Not Tested":
             sub_lines.append(f"DE Status: {dx_tools['de_status']}")
        
    # Follicular Lymphoma
    elif "Follicular lymphoma" in primary_entity:
        sub_lines.append(f"WHO Grade: {dx_tools['fl_grade']}")
        sub_lines.append(f"Growth Pattern: {dx_tools['fl_pattern']}")
        
    # T-Cell
    elif "AITL" in primary_entity or "TFH" in primary_entity:
        if dx_tools['tfh_text'] != "Confirmed":
            sub_lines.append(f"TFH Phenotype: {dx_tools['tfh_text']} (Atypical/Incomplete)")

    final_dx += dx_line

    if sub_lines:
        final_dx += "\n- " + " | ".join(sub_lines)
        
    # 3. Specimen Limitation Note
    if integrity != "Intact/Long":
        final_dx += f"\n\nNOTE: Limited by {integrity.lower()} specimen, pending additional molecular studies."
        
    # 4. Ancillary/Molecular Data
    if dx_tools['fish_summary']:
        final_dx += f"\n\nANCILLARY TESTING:\n- {dx_tools['fish_summary']}"
        
    # 5. Comment/Differential
    if comment_text:
        final_dx += f"\n\nCOMMENT:\n{comment_text}"
        
    # 6. Recommendations
    if reco_text:
        final_dx += f"\n\nRECOMMENDATION:\n{reco_text}"
        
    return final_dx


# =========================================
# Streamlit UI Setup
# =========================================
st.title("Lymphoid Neoplasm Synoptic Reporter (WHO 5/ICC)")

# --- Sidebar for Context and Specimen Triage ---
with st.sidebar:
    st.header("1. Triage & Context")
    
    clinical_hx = st.text_area("Clinical History", height=60,
                               placeholder="e.g. 68M with persistent cervical LAD. Rule out lymphoma.")
    
    site = st.text_input("Site/Source", value="Cervical Lymph Node")
    
    specimen_class = st.selectbox(
        "Specimen Category",
        ["Lymph Node (Nodal)", "Skin / Cutaneous", "Extranodal / Other"]
    )
    
    procedure_type = st.selectbox(
        "Procedure Type",
        ["Excisional Biopsy", "Incisional Biopsy", "Needle Core Biopsy", "Punch/Shave Biopsy", "Fine Needle Aspiration"]
    )
    
    st.markdown("---")
    st.subheader("Core Biopsy Integrity")
    integrity = st.selectbox("Integrity Assessment", ["Intact/Long", "Fragmented/Minute", "Crushed/Distorted"], index=0)

    # Dictionary to hold all inputs for easy passing to functions
    report_inputs = defaultdict(dict)
    report_inputs['site'] = site
    report_inputs['specimen_class'] = specimen_class
    report_inputs['procedure_type'] = procedure_type
    report_inputs['integrity'] = integrity


# --- Main Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "2. Architecture", 
    "3. Cytology & Background", 
    "4. Immunophenotype", 
    "5. Diagnostic Synthesis",
    "6. Report Preview"
])


# =========================================
# Tab 1: Architecture
# =========================================
with tab1:
    st.subheader(f"Architectural Pattern ({specimen_class})")
    
    if "Node" in specimen_class:
        architecture_pattern = st.multiselect(
            "Select Dominant Pattern(s)",
            ["Nodular/Follicular", "Diffuse/Effaced", "Paracortical (Interfollicular)", "Sinusoidal/Hilar", "Mantle Zone Expanded", "Marginal Zone Expanded"],
            default=["Diffuse/Effaced"]
        )
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            follicle_pattern = st.selectbox("Follicle Growth Pattern", ["Back-to-back/Confluent (FL-like)", "Regressed/Atrophic (NLPHL-like)", "Exploded/Transformed (PCNSL/HGBL)"])
        with col_f2:
            follicle_zoning = st.selectbox("Follicle Zoning/Polarity", ["Absent/Indistinct (FL-like)", "Preserved/Polarized (Reactive)", "Mantle Cuff Absent (TCL)"])

        report_inputs['architecture']['pattern'] = architecture_pattern
        report_inputs['architecture']['follicle_pattern'] = follicle_pattern
        report_inputs['architecture']['follicle_zoning'] = follicle_zoning
        report_inputs['architecture']['skin_pattern'] = "N/A"
        report_inputs['architecture']['skin_specifics'] = []
        
    elif "Skin" in specimen_class:
        skin_pattern = st.selectbox("Primary Dermal Infiltrate Pattern", ["Band-like (Lichenoid)", "Nodular/Diffuse Dermal", "Panniculitis-like (Subcutis)"])
        skin_specifics = st.multiselect("Specific Cutaneous Features", ["Epidermotropism", "Pautrier Microabscesses", "Adnexal involvement", "Bottom-heavy pattern"])
        
        report_inputs['architecture']['pattern'] = [skin_pattern]
        report_inputs['architecture']['skin_pattern'] = skin_pattern
        report_inputs['architecture']['skin_specifics'] = skin_specifics

# =========================================
# Tab 2: Cytology & Background
# =========================================
with tab2:
    st.subheader("Atypical Cell Morphology")
    morphology_c1, morphology_c2 = st.columns(2)
    
    with morphology_c1:
        cell_size = st.selectbox("Dominant Cell Size", ["Small (CLL/SLL, MZL)", "Small-Medium (MCL, FL)", "Medium-Large (DLBCL, AITL)", "Large/Anaplastic (ALCL, CHL)"])
        nuclear_contour = st.selectbox("Nuclear Contours", ["Round/Regular (Immunoblast)", "Irregular/Cleaved (Centrocytic)", "Convoluted (Sézary)", "Multilobated (Popcorn/L&H)"])
    with morphology_c2:
        chromatin = st.selectbox("Chromatin Texture", ["Condensed/Clumped (CLL/MCL)", "Vesicular/Open (Centroblastic)", "Fine/Dusty (Prolymphocyte)"])
        nucleoli = st.selectbox("Nucleoli", ["Inconspicuous/Absent", "Small basophilic", "Prominent central/multiple peripheral", "Eosinophilic/Inclusion-like (RS-like)"])
        specific_shape = st.text_input("Other specific features:", placeholder="e.g. Starry-sky pattern, Plasmacytoid differentiation, Nuclear fragmentation")
    
    report_inputs['morphology'] = {
        "cell_size": cell_size, "nuclear_contour": nuclear_contour,
        "chromatin": chromatin, "nucleoli": nucleoli,
        "specific_shape": specific_shape
    }

    st.markdown("---")
    st.subheader("Background Milieu")
    background_features = st.multiselect(
        "Select Background Cellularity/Features:", 
        ["Eosinophils", "Plasma Cells (Polyclonal)", "Epithelioid Histiocytes (Clusters)", 
         "Sclerosis (Nodular/Bands)", "Vascular Proliferation (HEV/Capillaries)", 
         "Necrosis (Focal/Geographic)", "Mummified/Apoptotic Cells", "Starry-sky Pattern"]
    )
    report_inputs['background_features'] = background_features

# =========================================
# Tab 3: Immunophenotype
# =========================================
with tab3:
    st.subheader("IHC Matrix")
    
    col_ihc_1, col_ihc_2, col_ihc_3 = st.columns(3)
    
    # Define common markers and their default status
    marker_defaults = {
        "CD20": "+", "CD79a": "+", "PAX5": "+",
        "CD3": "-", "CD5": "-", "CD7": "-",
        "CD10": "-", "BCL6": "-", "BCL2": "+",
        "Cyclin D1": "-", "SOX11": "-", "TdT": "-",
        "CD30": "Focal", "ALK": "-", "PD-1": "Perifollicular",
        "MUM1": "Subset", "Ki-67": 30 # Special handling for Ki-67
    }
    
    # Display and update marker map
    ihc_map = {}
    
    with col_ihc_1:
        st.caption("B-Cell & Proliferation")
        ihc_map['CD20'] = st.selectbox("CD20", ["+", "Subset", "-"], index=0)
        ihc_map['CD10'] = st.selectbox("CD10", ["+", "-", "Subset"], index=1)
        ihc_map['BCL6'] = st.selectbox("BCL6", ["+", "-", "Subset"], index=1)
        ihc_map['BCL2'] = st.selectbox("BCL2", ["+", "-", "Loss"], index=0)
        
    with col_ihc_2:
        st.caption("Mantle/TFH/ALCL")
        ihc_map['CD5'] = st.selectbox("CD5", ["+", "Subset", "-"], index=2)
        ihc_map['Cyclin D1'] = st.selectbox("Cyclin D1", ["+", "-", "Subset"], index=1)
        ihc_map['MUM1'] = st.selectbox("MUM1", ["+", "-", "Subset"], index=2)
        ihc_map['ALK'] = st.selectbox("ALK", ["+", "Focal", "-"], index=2)

    with col_ihc_3:
        st.caption("T-Cell & Activation")
        ihc_map['CD3'] = st.selectbox("CD3", ["+", "Subset", "-"], index=0)
        ihc_map['CD30'] = st.selectbox("CD30", ["+", "Focal", "Negative"], index=2)
        ihc_map['PD-1'] = st.selectbox("PD-1 (Pattern)", ["Perifollicular", "Diffuse", "Negative"], index=0)
        ihc_map['EBER-ISH'] = st.selectbox("EBER-ISH", ["+", "Rare+", "-"], index=2)
        
    st.markdown("---")
    
    col_ki, col_flow = st.columns(2)
    with col_ki:
        ki67 = st.slider("Ki-67 Proliferation Index (%)", 0, 100, 30)
    with col_flow:
        flow_result = st.selectbox("Flow Cytometry / Molecular Studies", 
                                 ["Not performed", 
                                  "Monotypic B-cell population detected", 
                                  "Aberrant T-cell population detected", 
                                  "Polyclonal B and T-cell populations",
                                  "No evidence of lymphoma by flow"])
        
    report_inputs['ihc_map'] = ihc_map
    report_inputs['ki67'] = ki67
    report_inputs['flow_result'] = flow_result
    

# =========================================
# Tab 4: Diagnostic Synthesis
# =========================================
with tab4:
    st.subheader("Primary Diagnostic Entity (WHO 5th/ICC)")
    
    dx_category = st.selectbox(
        "Diagnostic Category", 
        ["Reactive/Benign", "B-Cell Lymphoma (Nodal)", "T-Cell Lymphoma (Nodal)", "Hodgkin Lymphoma", "Cutaneous Lymphoma"]
    )

    entity_list = []
    if dx_category == "Reactive/Benign": entity_list = REACTIVE_ENTITIES
    elif dx_category == "B-Cell Lymphoma (Nodal)": entity_list = B_CELL_NODAL
    elif dx_category == "T-Cell Lymphoma (Nodal)": entity_list = T_CELL_NODAL
    elif dx_category == "Hodgkin Lymphoma": entity_list = HODGKIN_LYMPHOMA
    elif dx_category == "Cutaneous Lymphoma": entity_list = CUTANEOUS_LYMPHOMA
    
    primary_entity = st.selectbox("Select Primary Entity", entity_list)
    report_inputs['primary_entity'] = primary_entity
    
    # Dictionary to hold ancillary data required for Final DX
    dx_tools = defaultdict(lambda: "")

    st.markdown("---")
    st.subheader("Ancillary Differentiators")

    # Dynamic Ancillary Tools
    if "DLBCL" in primary_entity or "HGBL" in primary_entity:
        col_dl_1, col_dl_2, col_dl_3 = st.columns(3)
        dx_tools['coo_text'] = col_dl_1.selectbox("Cell of Origin (Hans)", ["GCB-type", "ABC-type / Non-GCB", "Indeterminate"])
        dx_tools['de_status'] = col_dl_2.selectbox("Double Expressor Status", ["Not Tested", "MYC+ BCL2+ (DE)", "Negative (Non-DE)"])
        if dx_tools['coo_text'] == "GCB-type" and dx_tools['de_status'] == "MYC+ BCL2+ (DE)":
            st.warning("⚠️ GCB + DE status requires correlation with FISH for Double/Triple Hit (HGBL).")
        
    elif "Follicular lymphoma" in primary_entity:
        col_fl_1, col_fl_2 = st.columns(2)
        dx_tools['fl_grade'] = col_fl_1.selectbox("FL Grade (WHO 5)", ["Grade 1-2 (Classic)", "Grade 3A", "Grade 3B (Follicular Large B-cell Lymphoma)"])
        dx_tools['fl_pattern'] = col_fl_2.selectbox("Growth Pattern", ["Predominantly Follicular (>75%)", "Follicular and Diffuse", "Predominantly Diffuse (>50%)"])

    elif "Mantle cell lymphoma" in primary_entity:
        if "blastoid" in primary_entity:
            st.info("Blastoid/Pleomorphic MCL phenotype is strongly suggested. Confirm with high Ki-67 and high-level Cyclin D1/SOX11.")
            
    elif "T-cell" in primary_entity and "Nodal" in dx_category:
        dx_tools['tfh_text'] = st.selectbox("TFH Phenotype Confirmation", ["Confirmed (Multiple TFH Markers)", "Incomplete/Atypical", "Pending"])

    # General Ancillary Input
    dx_tools['fish_summary'] = st.text_area("FISH/Molecular Summary:", placeholder="e.g. MYC rearrangement detected, BCL2 fusion present, RHOA G17V mutation.")
    
    comment = st.text_area("Final Diagnostic Comment (Optional)", key="comment_text_input", height=80, 
                           placeholder="Discuss differential diagnosis or challenging features.")
    
    reco_input = st.text_area("Recommendations (Optional)", key="reco_input", height=80, 
                              placeholder="e.g. Recommend molecular studies (NGS) for mutations.")
    
    report_inputs['comment'] = comment
    report_inputs['recommendations'] = reco_input
    
    # --- GENERATION BUTTON ---
    if st.button("Generate Synoptic Report", type="primary"):
        # 1. Generate Microscopic Text
        st.session_state["microscopic_text"] = generate_microscopic_text(report_inputs)
        
        # 2. Generate Final Diagnosis Text
        st.session_state["final_diagnosis_text"] = generate_final_diagnosis_text(report_inputs, dx_tools)


# =========================================
# Tab 5: Combined Report Preview
# =========================================
with tab5:
    st.header("Generated Synoptic Report")

    st.subheader("Clinical History")
    st.code(clinical_hx or "CLINICAL HISTORY NOT PROVIDED", language="markdown")

    st.subheader("Microscopic Description")
    st.text_area(
        "",
        value=st.session_state.get('microscopic_text', 'Microscopic Description will appear here after generation.'),
        height=350,
    )

    st.subheader("Final Diagnosis")
    st.text_area(
        "",
        value=st.session_state.get('final_diagnosis_text', 'Final Diagnosis will appear here after generation.'),
        height=400,
    )

    st.markdown("---")
    if st.session_state.get('final_diagnosis_text'):
        # Prepare data for download
        full_report = f"CLINICAL HISTORY:\n{clinical_hx}\n\nMICROSCOPIC DESCRIPTION:\n{st.session_state['microscopic_text']}\n\nFINAL DIAGNOSIS:\n{st.session_state['final_diagnosis_text']}"
        
        st.download_button(
            label="Download Full Report (TXT)",
            data=full_report,
            file_name=f"LymphNodeReport_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
