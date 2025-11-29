import streamlit as st

# =========================================
# Utility / Constants
# =========================================

st.set_page_config(
    page_title="Lymph Node & Cutaneous Lymphoma Reporting (WHO5)",
    layout="wide"
)

# ---------- WHO5-style entity lists (filtered to nodal / cutaneous lymphomas) ----------

REACTIVE_ENTITIES = [
    "Reactive follicular hyperplasia",
    "Paracortical (interfollicular) hyperplasia",
    "Sinus histiocytosis",
    "Granulomatous lymphadenitis",
    "Necrotizing lymphadenitis",
    "Dermatopathic lymphadenitis",
    "Castleman disease, hyaline-vascular type",
    "Castleman disease, plasma cell type",
    "Atypical lymphoid hyperplasia (indeterminate for lymphoma)",
]

B_CELL_NODAL = [
    # Classic nodal / systemic B-cell neoplasms
    "Chronic lymphocytic leukemia / Small lymphocytic lymphoma (CLL/SLL)",
    "Follicular lymphoma, classic (WHO5)",
    "Follicular large B-cell lymphoma",
    "Follicular lymphoma with unusual cytologic features",
    "Primary cutaneous follicle center lymphoma (PCFCL)",
    "Diffuse large B-cell lymphoma, NOS (DLBCL, NOS)",
    "Diffuse large B-cell lymphoma, EBV-positive",
    "Primary mediastinal (thymic) large B-cell lymphoma",
    "High-grade B-cell lymphoma (HGBL) with MYC and BCL2 and/or BCL6 rearrangements",
    "High-grade B-cell lymphoma with 11q aberration",
    "Burkitt lymphoma",
    "Mantle cell lymphoma, classic",
    "Mantle cell lymphoma, blastoid / pleomorphic",
    "Leukemic non-nodal mantle cell lymphoma",
    "Marginal zone lymphoma, nodal",
    "Marginal zone lymphoma, extranodal (MALT-type)",
    "Splenic marginal zone lymphoma",
    "Lymphoplasmacytic lymphoma / Waldenström macroglobulinemia",
    "Primary cutaneous diffuse large B-cell lymphoma, leg type (PCDLBCL-LT)",
]

T_NK_NODAL = [
    # WHO5 nTFH family
    "Nodal T-follicular helper cell lymphoma, angioimmunoblastic type (nTFHL-AI)",
    "Nodal T-follicular helper cell lymphoma, follicular type (nTFHL-F)",
    "Nodal T-follicular helper cell lymphoma, NOS (nTFHL-NOS)",
    # Other mature T/NK
    "Peripheral T-cell lymphoma, NOS",
    "Anaplastic large cell lymphoma (ALCL), ALK-positive",
    "Anaplastic large cell lymphoma (ALCL), ALK-negative",
    "EBV-positive nodal T- or NK-cell lymphoma, NOS",
    "Extranodal NK/T-cell lymphoma, nasal type",
    "Hepatosplenic T-cell lymphoma",
]

HODGKIN = [
    "Classical Hodgkin lymphoma, nodular sclerosis",
    "Classical Hodgkin lymphoma, mixed cellularity",
    "Classical Hodgkin lymphoma, lymphocyte-rich",
    "Classical Hodgkin lymphoma, lymphocyte-depleted",
    "Nodular lymphocyte-predominant Hodgkin lymphoma (NLPHL)",
]

CUTANEOUS_T = [
    "Mycosis fungoides (MF)",
    "Sézary syndrome (SS)",
    "Primary cutaneous CD4+ small/medium T-cell lymphoproliferative disorder",
    "Primary cutaneous acral CD8+ T-cell lymphoproliferative disorder",
    "Primary cutaneous CD8+ aggressive epidermotropic cytotoxic T-cell lymphoma",
    "Subcutaneous panniculitis-like T-cell lymphoma",
    "Primary cutaneous gamma/delta T-cell lymphoma",
    "Primary cutaneous peripheral T-cell lymphoma, NOS",
    "Lymphomatoid papulosis (LyP), type A",
    "Lymphomatoid papulosis (LyP), type B",
    "Lymphomatoid papulosis (LyP), type C",
    "Lymphomatoid papulosis (LyP), type D",
    "Lymphomatoid papulosis (LyP), type E",
    "Primary cutaneous anaplastic large cell lymphoma (pcALCL)",
]

CUTANEOUS_B = [
    "Primary cutaneous follicle center lymphoma (PCFCL)",
    "Primary cutaneous marginal zone lymphoma (PCMZL)",
    "Primary cutaneous diffuse large B-cell lymphoma, leg type (PCDLBCL-LT)",
]

OTHER_STROMAL_HISTIOCYTIC = [
    "Rosai-Dorfman disease",
    "Langerhans cell histiocytosis",
    "Follicular dendritic cell sarcoma",
    "Fibroblastic reticular cell tumor",
]

ALL_ENTITIES = (
    REACTIVE_ENTITIES
    + B_CELL_NODAL
    + T_NK_NODAL
    + HODGKIN
    + CUTANEOUS_T
    + CUTANEOUS_B
    + OTHER_STROMAL_HISTIOCYTIC
)

# ---------- Helper functions ----------

def hans_algorithm(cd10, bcl6, mum1):
    """
    Implement Hans cell-of-origin algorithm for DLBCL.
    Inputs are True/False for positivity.
    Returns 'GCB', 'Non-GCB', or 'Indeterminate'.
    """
    if cd10:
        return "Germinal center B-cell (GCB) type"
    if not cd10 and not bcl6:
        return "Activated B-cell (ABC / non-GCB) type"
    if not cd10 and bcl6 and mum1:
        return "Activated B-cell (ABC / non-GCB) type"
    if not cd10 and bcl6 and not mum1:
        return "Germinal center B-cell (GCB) type"
    return "Indeterminate by Hans algorithm"


def tfh_marker_summary(markers_dict):
    """
    markers_dict: dict of {marker_name: bool}
    Returns text and count.
    """
    positive = [m for m, v in markers_dict.items() if v]
    return positive, len(positive)


def double_expressor_status(myc_pct, bcl2_pct, myc_cutoff=40, bcl2_cutoff=50):
    if myc_pct is None or bcl2_pct is None:
        return "Not assessable"
    if myc_pct >= myc_cutoff and bcl2_pct >= bcl2_cutoff:
        return "Meets immunohistochemical criteria for MYC/BCL2 double-expressor status."
    return "Does not meet double-expressor cutoffs."


def build_specimen_sentence(specimen_class, procedure_type, site_text, core_count,
                            core_length, integrity, skin_depth):
    parts = []
    if specimen_class == "Lymph node":
        if procedure_type == "Needle core biopsy":
            base = f"Needle core biopsy of {site_text} lymph node."
            cores = []
            if core_count:
                cores.append(f"{core_count} cores")
            if core_length:
                cores.append(f"aggregate length {core_length:.1f} cm")
            if cores:
                base += f" The specimen consists of {', '.join(cores)}."
            if integrity:
                base += f" The cores are {integrity.lower()}."
            if core_length is not None and core_length < 0.5:
                base += " The limited tissue sampling may restrict comprehensive architectural assessment."
            parts.append(base)
        elif procedure_type in ["Excisional biopsy", "Incisional biopsy"]:
            parts.append(f"{procedure_type} of {site_text} lymph node.")
        else:
            parts.append(f"{procedure_type} of {site_text}.")
    elif specimen_class == "Skin":
        base = f"{procedure_type} of skin, {site_text}."
        if skin_depth:
            base += " The biopsy includes: " + ", ".join(skin_depth) + "."
        parts.append(base)
    else:
        parts.append(f"{procedure_type} of {site_text}.")
    return " ".join(parts)


def build_microscopic_description(
    specimen_class,
    nodal_arch,
    pattern,
    follicles_present,
    follicle_desc,
    follicles_polarized,
    tingible_macrophages,
    mantle_zones,
    cell_size,
    nuclear_features,
    chromatin,
    nucleoli,
    cytoplasm,
    background_cells,
    sclerosis_pattern,
    skin_epidermis,
    skin_dermis,
    skin_other
):
    sentences = []

    # Architecture
    if specimen_class == "Lymph node":
        if nodal_arch == "Preserved":
            s = "Sections show a lymph node with preserved overall architecture."
        elif nodal_arch == "Partially effaced":
            s = "Sections show partial effacement of the lymph node architecture."
        elif nodal_arch == "Effaced":
            s = "Sections show near-complete effacement of the lymph node architecture."
        else:
            s = "Sections show lymphoid tissue."
        if pattern:
            s += " The infiltrate is arranged in a " + " and ".join(pattern).lower() + " pattern."
        sentences.append(s)

        if follicles_present:
            follicle_sentence = "Numerous follicles are present, showing "
            if follicle_desc:
                follicle_sentence += follicle_desc.lower()
            else:
                follicle_sentence += "reactive features"
            extras = []
            if follicles_polarized:
                extras.append("polarization with dark and light zones")
            if tingible_macrophages:
                extras.append("prominent tingible-body macrophages")
            if mantle_zones:
                extras.append(f"mantle zones that are {mantle_zones.lower()}")
            if extras:
                follicle_sentence += ", with " + ", ".join(extras)
            follicle_sentence += "."
            sentences.append(follicle_sentence)

    # Cytology
    if cell_size or nuclear_features or chromatin or nucleoli or cytoplasm:
        cyto_parts = []
        if cell_size:
            cyto_parts.append(f"{cell_size.lower()} to intermediate-sized lymphoid cells")
        else:
            cyto_parts.append("lymphoid cells")
        if nuclear_features:
            cyto_parts.append("with " + ", ".join([nf.lower() for nf in nuclear_features]) + " nuclei")
        if chromatin:
            cyto_parts.append(f"and {chromatin.lower()} chromatin")
        if nucleoli:
            cyto_parts.append(f"and {nucleoli.lower()} nucleoli")
        if cytoplasm:
            cyto_parts.append(f"and {cytoplasm.lower()} cytoplasm")
        cyto_sentence = "The infiltrate is composed predominantly of " + " ".join(cyto_parts) + "."
        sentences.append(cyto_sentence)

    # Background cells
    if background_cells or sclerosis_pattern:
        bg = []
        if background_cells:
            bg.append("a background rich in " + ", ".join([b.lower() for b in background_cells]))
        if sclerosis_pattern:
            bg.append(sclerosis_pattern.lower() + " fibrosis")
        if bg:
            sentences.append("The microenvironment shows " + " and ".join(bg) + ".")

    # Skin-specific description
    if specimen_class == "Skin":
        if skin_epidermis or skin_dermis or skin_other:
            skin_sentence = "In the skin biopsy, "
            subparts = []
            if skin_epidermis:
                subparts.append("epidermis with " + ", ".join([e.lower() for e in skin_epidermis]))
            if skin_dermis:
                subparts.append("dermis with " + ", ".join([d.lower() for d in skin_dermis]))
            if skin_other:
                subparts.append(", ".join([o.lower() for o in skin_other]))
            skin_sentence += "; ".join(subparts) + "."
            sentences.append(skin_sentence)

    if not sentences:
        sentences.append("Sections show lymphoid tissue; please see immunophenotypic and molecular studies.")
    return " ".join(sentences)


def build_flow_sentence(flow_status):
    if flow_status == "Polyclonal / no evidence of clonal population":
        return "Flow cytometry shows a polytypic B-cell population without evidence of a clonal B- or aberrant T-cell population."
    elif flow_status == "Clonal B-cell population":
        return "Flow cytometry identifies a clonal B-cell population with light chain restriction."
    elif flow_status == "Clonal T-cell population":
        return "Flow cytometry identifies an aberrant T-cell population."
    elif flow_status == "Not performed / not available":
        return "Flow cytometry was not performed or not available for review."
    return ""


def build_molecular_sentence(molecular_findings):
    if not molecular_findings:
        return ""
    return "Molecular studies: " + molecular_findings.strip()


def build_final_diagnosis(
    qualifier,
    primary_entity,
    site_text,
    specimen_class,
    procedure_type,
    coo_text,
    de_status,
    fish_summary,
    tfh_text,
    core_length,
    integrity,
    recommendations,
    comment
):
    lines = []

    # Line 1: Diagnosis header
    if primary_entity:
        prefix = ""
        if qualifier in ["Suspicious for", "Favour", "Indeterminate, cannot exclude"]:
            prefix = qualifier + " "
        elif qualifier == "Limited for diagnosis; see comment":
            prefix = "Limited for diagnosis. Features are suggestive of "
        elif qualifier == "Definitive":
            prefix = ""
        diagnosis_line = prefix + primary_entity
        if site_text:
            diagnosis_line += f", {site_text}"
        diagnosis_line += "."
        lines.append(diagnosis_line)
    else:
        lines.append("No specific lymphoma identified. See comment.")

    # Disclaimers for core biopsies
    if specimen_class == "Lymph node" and procedure_type == "Needle core biopsy":
        disc = "This diagnosis is rendered on a needle core biopsy. "
        if core_length is not None and core_length < 0.5:
            disc += "The limited tissue and fragmented cores restrict evaluation of nodal architecture; correlation with clinical, radiologic, and, if indicated, an excisional biopsy is recommended."
        else:
            disc += "Architectural assessment is inherently limited in core biopsies; correlation with clinical and imaging findings is advised."
        lines.append(disc)

    # DLBCL / HGBL add-ons
    if primary_entity and "large B-cell lymphoma" in primary_entity.lower():
        if coo_text:
            lines.append(f"Cell-of-origin (Hans algorithm): {coo_text}.")
        if de_status:
            lines.append(de_status)
        if fish_summary:
            lines.append(fish_summary)

    # nTFHL / TFH markers
    if primary_entity and "t-follicular helper" in primary_entity.lower():
        if tfh_text:
            lines.append(tfh_text)

    # Recommendations
    if recommendations:
        lines.append("Recommendations: " + recommendations.strip())

    # Comment
    if comment:
        lines.append("Comment: " + comment.strip())

    return "\n".join(lines)


# =========================================
# Session state initialization
# =========================================

if "microscopic_text" not in st.session_state:
    st.session_state["microscopic_text"] = ""

if "final_diagnosis_text" not in st.session_state:
    st.session_state["final_diagnosis_text"] = ""


# =========================================
# Sidebar – global inputs
# =========================================

st.sidebar.title("Specimen & Clinical")

specimen_class = st.sidebar.selectbox(
    "Specimen class",
    ["Lymph node", "Skin", "Other"],
)

procedure_type = st.sidebar.selectbox(
    "Procedure type",
    ["Needle core biopsy", "Excisional biopsy", "Incisional biopsy", "Punch biopsy", "Shave biopsy", "Excision (skin)"],
)

site_text = st.sidebar.text_input("Site (e.g., 'left axillary', 'right cervical', 'left forearm')")

clinical_hx = st.sidebar.text_area("Clinical history / Indication", height=120)

# Core details
core_count = None
core_length = None
integrity = None
if procedure_type == "Needle core biopsy":
    col_c1, col_c2 = st.sidebar.columns(2)
    with col_c1:
        core_count = st.number_input("Number of cores", min_value=0, max_value=30, value=3)
    with col_c2:
        core_length = st.number_input("Aggregate length (cm)", min_value=0.0, max_value=10.0, value=1.0, step=0.1)
    integrity = st.sidebar.selectbox("Specimen integrity", ["Intact", "Fragmented", "Crushed"])

# Skin depth
skin_depth = []
if specimen_class == "Skin":
    skin_depth = st.sidebar.multiselect(
        "Biopsy depth represented",
        ["Epidermis", "Papillary dermis", "Reticular dermis", "Subcutis"]
    )

st.sidebar.markdown("---")
st.sidebar.write("This app assembles **Microscopic Description** and **Final Diagnosis** text with WHO5-aligned entities and logic.")


# =========================================
# Main layout – tabs
# =========================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Morphology",
    "Immunophenotype",
    "Ancillary Studies",
    "Diagnosis",
    "Generated Report",
])

# ---------- Tab 1: Morphology ----------
with tab1:
    st.header("Morphology / Architecture")

    if specimen_class == "Lymph node":
        nodal_arch = st.radio(
            "Overall nodal architecture",
            ["Preserved", "Partially effaced", "Effaced", "Not assessable"],
            horizontal=True,
        )

        pattern = st.multiselect(
            "Growth pattern (low power)",
            ["Nodular", "Follicular", "Diffuse", "Interfollicular", "Sinusoidal", "Mantle zone", "Marginal zone"],
        )

        st.subheader("Follicular / germinal center features")
        follicles_present = st.checkbox("Follicles / follicular structures present")
        follicle_desc = None
        follicles_polarized = False
        tingible_macrophages = False
        mantle_zones = None
        if follicles_present:
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                follicle_desc = st.selectbox(
                    "Follicle type",
                    [
                        "",
                        "Secondary, reactive",
                        "Crowded / back-to-back, suspicious for neoplastic",
                        "Regressed / atrophic (AITL / nTFHL-like)",
                        "Expanded mantle zones",
                    ],
                )
            with col_f2:
                follicles_polarized = st.checkbox("Polarization (dark and light zones)")
                tingible_macrophages = st.checkbox("Tingible-body macrophages present")
                mantle_zones = st.selectbox(
                    "Mantle zone status",
                    ["", "Intact", "Attenuated", "Absent"],
                )
        else:
            follicle_desc = None
            follicles_polarized = False
            tingible_macrophages = False
            mantle_zones = None

    else:
        nodal_arch = "Not applicable"
        pattern = []
        follicles_present = False
        follicle_desc = None
        follicles_polarized = False
        tingible_macrophages = False
        mantle_zones = None

    st.subheader("Cytology – dominant cell population")

    cell_size = st.selectbox(
        "Cell size",
        ["", "Small", "Medium", "Large", "Mixed (polymorphous)"],
    )

    nuclear_features = st.multiselect(
        "Nuclear contours / features",
        [
            "Round",
            "Irregular",
            "Cleaved / angulated (centrocyte-like)",
            "Cerebriform (Sezary / MF-like)",
            "Kidney-shaped / reniform (hallmark cells, ALCL-like)",
            "Multilobated / 'popcorn' (LP cells)",
        ],
    )

    chromatin = st.selectbox(
        "Chromatin",
        ["", "Condensed / clumped", "Fine", "Vesicular / open"],
    )

    nucleoli = st.selectbox(
        "Nucleoli",
        ["", "Inconspicuous", "Small basophilic", "Multiple peripheral", "Prominent central / single eosinophilic"],
    )

    cytoplasm = st.selectbox(
        "Cytoplasm",
        ["", "Scant", "Moderate", "Abundant", "Clear / pale", "Plasmacytoid", "Eosinophilic"],
    )

    st.subheader("Background milieu / microenvironment")

    background_cells = st.multiselect(
        "Background cells / features",
        [
            "Eosinophils",
            "Plasma cells",
            "Histiocytes / epithelioid histiocytes",
            "Tingible-body macrophages",
            "High endothelial venules (HEVs)",
            "Expanded follicular dendritic cell meshworks",
            "Starry-sky pattern",
            "Granulomas",
        ],
    )

    sclerosis_pattern = st.selectbox(
        "Fibrosis / sclerosis",
        [
            "",
            "Broad bands of collagen (NS-CHL-like)",
            "Fine compartmentalizing fibrosis (PMBL-like)",
            "Perivascular fibrosis",
        ],
    )

    # Skin-specific
    st.markdown("---")
    st.subheader("Skin-specific features (if applicable)")
    if specimen_class == "Skin":
        skin_epidermis = st.multiselect(
            "Epidermal features",
            [
                "Epidermotropism of atypical lymphocytes",
                "Pautrier microabscesses",
                "Spongiosis (minimal / absent)",
                "Spongiosis (marked)",
                "Parakeratosis",
            ],
        )
        skin_dermis = st.multiselect(
            "Dermal features",
            [
                "Band-like (lichenoid) infiltrate",
                "Perivascular infiltrate",
                "Periadnexal infiltrate",
                "Papillary dermal fibrosis ('wire-like' collagen)",
                "Subcutaneous panniculitis-like infiltrate",
                "Angiocentric / angiodestructive infiltrate",
            ],
        )
        skin_other = st.multiselect(
            "Other cutaneous features",
            [
                "Epidermal ulceration",
                "Necrosis",
                "Large CD30+ cells in clusters",
            ],
        )
    else:
        skin_epidermis = []
        skin_dermis = []
        skin_other = []

    st.markdown("—")
    if st.button("Generate / update Microscopic Description", type="primary"):
        spec_sentence = build_specimen_sentence(
            specimen_class, procedure_type, site_text, core_count, core_length, integrity, skin_depth
        )

        micro_sentence = build_microscopic_description(
            specimen_class,
            nodal_arch,
            pattern,
            follicles_present,
            follicle_desc,
            follicles_polarized,
            tingible_macrophages,
            mantle_zones,
            cell_size,
            nuclear_features,
            chromatin,
            nucleoli,
            cytoplasm,
            background_cells,
            sclerosis_pattern,
            skin_epidermis,
            skin_dermis,
            skin_other,
        )

        combined = spec_sentence + " " + micro_sentence
        st.session_state["microscopic_text"] = combined

    st.text_area(
        "Microscopic Description (editable)",
        key="microscopic_text",
        height=260,
    )

# ---------- Tab 2: Immunophenotype ----------
with tab2:
    st.header("Immunophenotype / IHC")

    st.markdown("Enter key markers. This section feeds Hans algorithm, TFH logic, and phenotype sanity checks.")

    col_a, col_b, col_c, col_d = st.columns(4)

    with col_a:
        cd3 = st.checkbox("CD3 positive")
        cd20 = st.checkbox("CD20 positive")
        cd5 = st.checkbox("CD5 positive")
        cd23 = st.checkbox("CD23 positive")

    with col_b:
        cd10 = st.checkbox("CD10 positive")
        bcl6 = st.checkbox("BCL6 positive")
        bcl2 = st.checkbox("BCL2 positive")
        cyclin_d1 = st.checkbox("Cyclin D1 positive")
        sox11 = st.checkbox("SOX11 positive")

    with col_c:
        cd30 = st.checkbox("CD30 positive (strong / diffuse)")
        alk = st.checkbox("ALK positive")
        mum1 = st.checkbox("MUM1 positive")
        eber = st.checkbox("EBER positive (ISH)")
        cd21_fdc = st.checkbox("CD21 highlights expanded FDC meshworks")

    with col_d:
        ki67_pct = st.slider("Ki-67 proliferation index (%)", 0, 100, 40)
        myc_pct = st.slider("MYC expression (%)", 0, 100, 30)
        bcl2_pct = st.slider("BCL2 expression (%)", 0, 100, 60)

    # Hans algorithm (DLBCL COO)
    st.markdown("---")
    st.subheader("Hans cell-of-origin (for DLBCL)")

    coo_text = hans_algorithm(cd10, bcl6, mum1)
    st.write(f"**Hans COO classification:** {coo_text}")

    # Double-expressor status
    de_result = double_expressor_status(myc_pct, bcl2_pct)
    st.write(f"**MYC/BCL2 double-expressor assessment:** {de_result}")

    # TFH markers
    st.markdown("---")
    st.subheader("T-follicular helper (TFH) phenotype markers (for nTFHL)")

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        tfh_cd10 = st.checkbox("TFH CD10+", key="tfh_cd10")
        tfh_bcl6 = st.checkbox("TFH BCL6+", key="tfh_bcl6")
    with col_t2:
        tfh_pd1 = st.checkbox("PD-1+", key="tfh_pd1")
        tfh_cxcl13 = st.checkbox("CXCL13+", key="tfh_cxcl13")
    with col_t3:
        tfh_icos = st.checkbox("ICOS+", key="tfh_icos")

    tfh_dict = {
        "CD10": tfh_cd10,
        "BCL6": tfh_bcl6,
        "PD-1": tfh_pd1,
        "CXCL13": tfh_cxcl13,
        "ICOS": tfh_icos,
    }
    tfh_positive, tfh_count = tfh_marker_summary(tfh_dict)

    if tfh_count > 0:
        st.write(f"TFH markers expressed: {', '.join(tfh_positive)} (total {tfh_count})")
    else:
        st.write("No TFH markers selected.")

    tfh_comment = ""
    if tfh_count >= 3:
        tfh_comment = f"Immunophenotype supports a T-follicular helper phenotype (≥3 TFH markers: {', '.join(tfh_positive)})."
    elif 2 <= tfh_count < 3:
        tfh_comment = f"At least 2 TFH markers expressed ({', '.join(tfh_positive)}); compatible with TFH phenotype but correlation with morphology is required."
    elif tfh_count < 2:
        tfh_comment = "Insufficient TFH markers for a definitive nTFHL diagnosis; consider PTCL, NOS or reactive conditions depending on morphology."

    st.info(tfh_comment)

# ---------- Tab 3: Ancillary studies ----------
with tab3:
    st.header("Ancillary Studies – Flow / Molecular / FISH")

    st.subheader("Flow cytometry")
    flow_status = st.selectbox(
        "Flow cytometry interpretation",
        [
            "",
            "Polyclonal / no evidence of clonal population",
            "Clonal B-cell population",
            "Clonal T-cell population",
            "Not performed / not available",
        ],
    )

    flow_sentence = build_flow_sentence(flow_status)
    if flow_sentence:
        st.write(flow_sentence)

    st.subheader("Molecular studies (PCR / NGS)")
    molecular_findings = st.text_area(
        "Summarize key molecular results (e.g., IGH / TRG clonality, MYD88 L265P, BCL2/BCL6 mutations, etc.)",
        height=120,
    )

    st.subheader("Cytogenetics / FISH")
    fish_myc = st.checkbox("FISH: MYC rearranged")
    fish_bcl2 = st.checkbox("FISH: BCL2 rearranged")
    fish_bcl6 = st.checkbox("FISH: BCL6 rearranged")
    fish_11q = st.checkbox("FISH: 11q aberration (high-grade B-cell lymphoma with 11q)")
    fish_other = st.text_area("Other cytogenetic / FISH findings", height=80)

    fish_summary_parts = []
    hits = []
    if fish_myc:
        hits.append("MYC")
    if fish_bcl2:
        hits.append("BCL2")
    if fish_bcl6:
        hits.append("BCL6")
    if hits:
        fish_summary_parts.append("Rearrangements detected involving " + ", ".join(hits) + ".")
    if fish_11q:
        fish_summary_parts.append("11q aberration present, compatible with high-grade B-cell lymphoma with 11q aberration in the appropriate morphologic and clinical setting.")
    if fish_other.strip():
        fish_summary_parts.append(fish_other.strip())
    fish_summary = " ".join(fish_summary_parts)

    st.text_area(
        "Ancillary studies text (auto-populated + editable suggestion)",
        value="\n".join(
            [x for x in [flow_sentence, build_molecular_sentence(molecular_findings), fish_summary] if x]
        ),
        height=200,
    )

# ---------- Tab 4: Diagnosis ----------
with tab4:
    st.header("Diagnostic Impression (WHO5-aligned)")

    diag_family = st.selectbox(
        "Diagnostic family",
        [
            "Reactive / non-neoplastic",
            "Mature B-cell neoplasm",
            "Mature T / NK-cell neoplasm",
            "Hodgkin lymphoma",
            "Primary cutaneous T-cell lymphoma / LPD",
            "Primary cutaneous B-cell lymphoma",
            "Other / histiocytic / stromal",
        ],
    )

    if diag_family == "Reactive / non-neoplastic":
        options = REACTIVE_ENTITIES
    elif diag_family == "Mature B-cell neoplasm":
        options = B_CELL_NODAL
    elif diag_family == "Mature T / NK-cell neoplasm":
        options = T_NK_NODAL
    elif diag_family == "Hodgkin lymphoma":
        options = HODGKIN
    elif diag_family == "Primary cutaneous T-cell lymphoma / LPD":
        options = CUTANEOUS_T
    elif diag_family == "Primary cutaneous B-cell lymphoma":
        options = CUTANEOUS_B
    else:
        options = OTHER_STROMAL_HISTIOCYTIC

    primary_entity = st.selectbox("Primary diagnostic entity (WHO5 terminology)", [""] + options)

    qualifier = st.selectbox(
        "Diagnostic qualifier",
        [
            "Definitive",
            "Suspicious for",
            "Favour",
            "Indeterminate, cannot exclude",
            "Limited for diagnosis; see comment",
        ],
    )

    # nTFHL / TFH guidance display
    if "T-follicular helper" in primary_entity:
        st.info("Selected entity is an nTFHL subtype. Ensure TFH phenotype (≥2 markers), expanded HEVs, and FDC meshwork are present morphologically.")

    # DLBCL / HGBL logic hints
    if "large B-cell lymphoma" in primary_entity.lower():
        st.warning(
            "For large B-cell lymphomas, ensure cell-of-origin (Hans), MYC/BCL2 expression, and MYC/BCL2/BCL6 FISH are assessed when clinically relevant."
        )

    st.subheader("Recommendations / additional comments")
    default_recs = ""
    if primary_entity in REACTIVE_ENTITIES or "Atypical lymphoid hyperplasia" in primary_entity:
        default_recs = "Clinical and radiologic correlation is recommended. Repeat biopsy can be considered if lymphadenopathy persists or progresses."
    elif "large B-cell lymphoma" in primary_entity.lower():
        default_recs = "Clinical staging, bone marrow evaluation as indicated, and multidisciplinary discussion (lymphoma tumor board) are recommended."
    elif "Mycosis fungoides" in primary_entity or "Sézary" in primary_entity:
        default_recs = "Correlation with clinical staging (TNMB), additional skin biopsies as needed, and hematologic evaluation for blood involvement are recommended."
    elif "anaplastic large cell lymphoma" in primary_entity.lower():
        default_recs = "Staging imaging and evaluation for systemic involvement are recommended. Distinguish primary cutaneous from systemic ALCL based on clinical data."

    recommendations = st.text_area(
        "Recommendations (editable)",
        value=default_recs,
        height=120,
    )

    comment = st.text_area(
        "Comment (optional; for grey-zone / limitations / differential diagnosis)",
        height=160,
    )

    # Build tfh_text for final diagnosis, based on TFH markers
    if "T-follicular helper" in primary_entity:
        tfh_text = tfh_comment
    else:
        tfh_text = ""

    if st.button("Generate / update Final Diagnosis", type="primary"):
        final_dx = build_final_diagnosis(
            qualifier=qualifier,
            primary_entity=primary_entity,
            site_text=site_text,
            specimen_class=specimen_class,
            procedure_type=procedure_type,
            coo_text=coo_text if "large B-cell lymphoma" in (primary_entity or "").lower() else "",
            de_status=de_result if "large B-cell lymphoma" in (primary_entity or "").lower() else "",
            fish_summary=fish_summary if "large B-cell lymphoma" in (primary_entity or "").lower() else "",
            tfh_text=tfh_text,
            core_length=core_length,
            integrity=integrity,
            recommendations=recommendations,
            comment=comment,
        )
        st.session_state["final_diagnosis_text"] = final_dx

    st.text_area(
        "Final Diagnosis (editable)",
        key="final_diagnosis_text",
        height=280,
    )

# ---------- Tab 5: Combined report ----------
with tab5:
    st.header("Generated Report")

    st.subheader("Clinical History")
    st.code(clinical_hx or "", language="markdown")

    st.subheader("Microscopic Description")
    st.code(
        st.session_state.get("microscopic_text", ""),
        language="markdown",
    )

    st.subheader("Final Diagnosis")
    st.code(
        st.session_state.get("final_diagnosis_text", ""),
        language="markdown",
    )

    st.markdown(
        """
You can copy-paste the **Microscopic Description** and **Final Diagnosis** into your LIS.
Both sections update from the editable fields in the earlier tabs and persist while you switch tabs.
"""
    )
