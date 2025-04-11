import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

# Page configuration
st.set_page_config(page_title="Advanced Composite Analysis", page_icon="📊", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main {padding: 2rem;}
    .stButton>button {width: 100%;}
    .stDownloadButton>button {width: 100%;}
    .stTextInput>div>div>input {text-align: center;}
    .stNumberInput>div>div>input {text-align: center;}
    .reportview-container .main .block-container {padding-top: 2rem;}
    h1 {color: #2a5c9a;}
    h2 {color: #3a7ca5;}
    .sidebar .sidebar-content {background-color: #f8f9fa;}
    .property-table {font-size: 0.9em;}
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("Advanced Composite Material Analysis Tool")
st.markdown("""
This enhanced application supports:
- Multiple fiber and matrix constituents
- Custom volume fractions
- Advanced micromechanics calculations
- Comprehensive laminate analysis
""")

# Navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select Analysis Mode", [
    "Material Properties",
    "Single Ply Analysis",
    "Laminate Analysis",
    "Failure Prediction"
])

# Initialize session state
if 'materials_db' not in st.session_state:
    st.session_state.materials_db = {
        'fibers': {},
        'matrices': {}
    }

if 'composite_definitions' not in st.session_state:
    st.session_state.composite_definitions = {}

if 'laminate_layers' not in st.session_state:
    st.session_state.laminate_layers = []

# Material Properties Module with multiple constituents
def material_properties_module():
    st.header("1. Material Properties Definition")
    
    tab1, tab2, tab3 = st.tabs(["Fiber Properties", "Matrix Properties", "Composite Definition"])
    
    with tab1:
        st.subheader("Fiber Constituents")
        
        col1, col2 = st.columns(2)
        with col1:
            fiber_name = st.text_input("Fiber Name (e.g., Carbon, Glass)", key="fiber_name")
            E_fiber = st.number_input("Young's Modulus (GPa)", min_value=0.1, value=230.0, key="E_fiber")
            nu_fiber = st.number_input("Poisson's Ratio", min_value=0.0, max_value=0.5, value=0.2, step=0.01, key="nu_fiber")
        
        with col2:
            G_fiber = st.number_input("Shear Modulus (GPa)", min_value=0.1, value=90.0, key="G_fiber")
            density_fiber = st.number_input("Density (g/cm³)", min_value=0.1, value=1.8, key="density_fiber")
        
        if st.button("Add Fiber", key="add_fiber"):
            if fiber_name:
                st.session_state.materials_db['fibers'][fiber_name] = {
                    'E': E_fiber,
                    'nu': nu_fiber,
                    'G': G_fiber,
                    'density': density_fiber
                }
                st.success(f"Added {fiber_name} fiber to database")
            else:
                st.error("Please enter a fiber name")
        
        st.subheader("Current Fiber Database")
        if st.session_state.materials_db['fibers']:
            fiber_df = pd.DataFrame.from_dict(st.session_state.materials_db['fibers'], orient='index')
            st.dataframe(fiber_df.style.format("{:.2f}"), use_container_width=True)
        else:
            st.info("No fibers defined yet")
    
    with tab2:
        st.subheader("Matrix Constituents")
        
        col1, col2 = st.columns(2)
        with col1:
            matrix_name = st.text_input("Matrix Name (e.g., Epoxy, Polyester)", key="matrix_name")
            E_matrix = st.number_input("Young's Modulus (GPa)", min_value=0.1, value=3.5, key="E_matrix")
            nu_matrix = st.number_input("Poisson's Ratio", min_value=0.0, max_value=0.5, value=0.35, step=0.01, key="nu_matrix")
        
        with col2:
            G_matrix = st.number_input("Shear Modulus (GPa)", min_value=0.1, value=1.3, key="G_matrix")
            density_matrix = st.number_input("Density (g/cm³)", min_value=0.1, value=1.2, key="density_matrix")
        
        if st.button("Add Matrix", key="add_matrix"):
            if matrix_name:
                st.session_state.materials_db['matrices'][matrix_name] = {
                    'E': E_matrix,
                    'nu': nu_matrix,
                    'G': G_matrix,
                    'density': density_matrix
                }
                st.success(f"Added {matrix_name} matrix to database")
            else:
                st.error("Please enter a matrix name")
        
        st.subheader("Current Matrix Database")
        if st.session_state.materials_db['matrices']:
            matrix_df = pd.DataFrame.from_dict(st.session_state.materials_db['matrices'], orient='index')
            st.dataframe(matrix_df.style.format("{:.2f}"), use_container_width=True)
        else:
            st.info("No matrices defined yet")
    
    with tab3:
        st.subheader("Composite Definition")
        
        if not st.session_state.materials_db['fibers'] or not st.session_state.materials_db['matrices']:
            st.warning("Please define at least one fiber and one matrix first")
            return
        
        composite_name = st.text_input("Composite Name (e.g., Carbon/Epoxy)", key="composite_name")
        
        # Fiber selection and volume fractions
        st.markdown("**Fiber Constituents**")
        fiber_cols = st.columns(3)
        fiber_selections = {}
        total_fiber_vf = 0.0
        
        for i, (fiber_name, props) in enumerate(st.session_state.materials_db['fibers'].items()):
            with fiber_cols[i % 3]:
                vf = st.number_input(
                    f"{fiber_name} Volume Fraction",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.6 if i == 0 else 0.0,
                    step=0.01,
                    key=f"vf_{fiber_name}"
                )
                fiber_selections[fiber_name] = vf
                total_fiber_vf += vf
        
        st.markdown(f"**Total Fiber Volume Fraction: {total_fiber_vf:.2f}**")
        
        # Matrix selection and volume fractions
        st.markdown("**Matrix Constituents**")
        matrix_cols = st.columns(3)
        matrix_selections = {}
        total_matrix_vf = 0.0
        
        for i, (matrix_name, props) in enumerate(st.session_state.materials_db['matrices'].items()):
            with matrix_cols[i % 3]:
                vf = st.number_input(
                    f"{matrix_name} Volume Fraction",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.4 if i == 0 else 0.0,
                    step=0.01,
                    key=f"vf_{matrix_name}"
                )
                matrix_selections[matrix_name] = vf
                total_matrix_vf += vf
        
        st.markdown(f"**Total Matrix Volume Fraction: {total_matrix_vf:.2f}**")
        
        # Check volume fraction balance
        vf_error = None
        if not np.isclose(total_fiber_vf + total_matrix_vf, 1.0, atol=0.01):
            vf_error = f"Total volume fractions must sum to 1.0 (current: {total_fiber_vf + total_matrix_vf:.2f})"
            st.error(vf_error)
        
        if st.button("Calculate Composite Properties") and not vf_error and composite_name:
            # Calculate composite properties using generalized rule of mixtures
            E1 = 0.0
            E2_denominator = 0.0
            G12_denominator = 0.0
            nu12 = 0.0
            density = 0.0
            
            # Fiber contributions
            for fiber_name, vf in fiber_selections.items():
                fiber = st.session_state.materials_db['fibers'][fiber_name]
                E1 += fiber['E'] * vf
                E2_denominator += vf / fiber['E']
                G12_denominator += vf / fiber['G']
                nu12 += fiber['nu'] * vf
                density += fiber['density'] * vf
            
            # Matrix contributions
            for matrix_name, vf in matrix_selections.items():
                matrix = st.session_state.materials_db['matrices'][matrix_name]
                E1 += matrix['E'] * vf
                E2_denominator += vf / matrix['E']
                G12_denominator += vf / matrix['G']
                nu12 += matrix['nu'] * vf
                density += matrix['density'] * vf
            
            E2 = 1 / E2_denominator
            G12 = 1 / G12_denominator
            nu21 = nu12 * E2 / E1
            
            # Store composite definition
            st.session_state.composite_definitions[composite_name] = {
                'E1': E1,
                'E2': E2,
                'G12': G12,
                'nu12': nu12,
                'nu21': nu21,
                'density': density,
                'fiber_constituents': fiber_selections,
                'matrix_constituents': matrix_selections
            }
            
            # Display results
            st.subheader("Composite Properties")
            results = {
                "Property": ["E₁ (Longitudinal Modulus)", "E₂ (Transverse Modulus)", 
                            "G₁₂ (In-plane Shear Modulus)", "ν₁₂ (Major Poisson's Ratio)", 
                            "ν₂₁ (Minor Poisson's Ratio)", "Density"],
                "Value": [f"{E1:.2f} GPa", f"{E2:.2f} GPa", f"{G12:.2f} GPa", 
                         f"{nu12:.4f}", f"{nu21:.4f}", f"{density:.2f} g/cm³"],
                "Formula": ["Σ(Eᵢ·Vᵢ)", "1/Σ(Vᵢ/Eᵢ)", "1/Σ(Vᵢ/Gᵢ)", 
                           "Σ(νᵢ·Vᵢ)", "ν₁₂·E₂/E₁", "Σ(ρᵢ·Vᵢ)"]
            }
            
            st.table(pd.DataFrame(results))
            
            # Composition visualization
            st.subheader("Composition Breakdown")
            
            fig, ax = plt.subplots(1, 2, figsize=(12, 4))
            
            # Fiber pie chart
            fiber_labels = [f"{k} ({v:.0%})" for k, v in fiber_selections.items() if v > 0]
            fiber_values = [v for v in fiber_selections.values() if v > 0]
            if fiber_values:
                ax[0].pie(fiber_values, labels=fiber_labels, autopct='%1.1f%%', startangle=90)
                ax[0].set_title("Fiber Constituents")
            
            # Matrix pie chart
            matrix_labels = [f"{k} ({v:.0%})" for k, v in matrix_selections.items() if v > 0]
            matrix_values = [v for v in matrix_selections.values() if v > 0]
            if matrix_values:
                ax[1].pie(matrix_values, labels=matrix_labels, autopct='%1.1f%%', startangle=90)
                ax[1].set_title("Matrix Constituents")
            
            st.pyplot(fig)
    
    # Show all defined composites
    if st.session_state.composite_definitions:
        st.subheader("Defined Composites")
        comp_df = pd.DataFrame.from_dict({
            name: {k: v for k, v in props.items() if k in ['E1', 'E2', 'G12', 'nu12', 'density']}
            for name, props in st.session_state.composite_definitions.items()
        }, orient='index')
        st.dataframe(comp_df.style.format("{:.2f}"), use_container_width=True)

# (The rest of your modules - Single Ply Analysis, Laminate Analysis, Failure Prediction - 
# would remain largely the same but would pull from the composite_definitions instead of 
# direct input. You would need to add a composite material selection at the start of each module.)

# Main app logic
if app_mode == "Material Properties":
    material_properties_module()
elif app_mode == "Single Ply Analysis":
    st.warning("Implementation note: This module would need to be updated to select from defined composites")
elif app_mode == "Laminate Analysis":
    st.warning("Implementation note: This module would need to be updated to select from defined composites")
elif app_mode == "Failure Prediction":
    st.warning("Implementation note: This module would need to be updated to select from defined composites")

# Footer
st.markdown("---")
st.markdown("**Advanced Composite Material Analysis Tool** - Created for Composite Model Review")
