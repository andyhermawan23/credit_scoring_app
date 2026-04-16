import streamlit as st
import pandas as pd
import numpy as np
import pickle

# Konfigurasi Halaman
st.set_page_config(page_title="Credit Scoring App", layout="wide")

# --- FUNGSI LOAD MODEL ---
@st.cache_resource
def load_model():
    # Pastikan nama file sesuai dengan hasil export Anda
    filename = 'model_pipeline.pkl' 
    try:
        with open(filename, 'rb') as file:
            model = pickle.load(file)
        return model
    except FileNotFoundError:
        return None

model = load_model()

# --- UI STREAMLIT ---
st.title("🏦 Credit Scoring Predictor")
st.markdown("Aplikasi prediksi risiko kredit menggunakan model **Decision Tree**.")
st.divider()

if model is None:
    st.error("⚠️ File model '.pkl' tidak ditemukan. Pastikan file model ada di direktori yang sama.")
    st.stop()

# --- INPUT FORM ---
with st.form("prediction_form"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Personal & Loan")
        tenor_months = st.number_input("Tenor (Months)", 12, 24, 12)
        loan_amount = st.number_input("Loan Amount", 1000000.0, 20000000.0, 5000000.0)
        borrower_age = st.number_input("Age", 21, 59, 30)
        employment_type = st.selectbox("Employment", ['PNS', 'Karyawan Tetap', 'Profesional', 'Wiraswasta', 'Karyawan Kontrak'])
        region = st.selectbox("Region", ['Bali & Nusa Tenggara', 'Jawa', 'Sumatera', 'Kalimantan', 'Sulawesi'])

    with col2:
        st.subheader("Financials")
        monthly_income = st.number_input("Monthly Income", 340212.0, 27998010.0, 5000000.0)
        monthly_installment = st.number_input("Monthly Installment", 50447.0, 2066026.0, 500000.0)
        dti_ratio = st.slider("DTI Ratio", 0.1, 0.6, 0.3)
        interest_rate = st.number_input("Interest Rate (%)", 1.5, 3.49, 2.0)
        risk_grade = st.selectbox("Risk Grade", ['A', 'B', 'C', 'D', 'E'])

    with col3:
        st.subheader("Credit History")
        credit_score = st.slider("Credit Score", 304, 849, 600)
        dpd = st.number_input("Current DPD", 0, 29, 0)
        outstanding_balance = st.number_input("Outstanding Balance", 896577.0, 18920900.0, 1000000.0)
        loan_status = st.selectbox("Loan Status", ['Current', 'DPD1-29'])
        # Fitur tambahan yang ada di limitasi Anda
        pct_tenor_elapsed = st.number_input("Pct Tenor Elapsed", 0.04, 0.08, 0.05)

    submit = st.form_submit_button("Analisis Risiko")

# --- PROSES PREDIKSI ---
if submit:
    # Buat DataFrame dengan SEMUA kolom yang digunakan saat training
    # Sesuaikan urutan dan nama kolom dengan data training Anda
    data = {
        'tenor_months': [tenor_months],
        'loan_amount': [loan_amount],
        'monthly_installment': [monthly_installment],
        'interest_rate_monthly_pct': [interest_rate],
        'borrower_age': [borrower_age],
        'monthly_income': [monthly_income],
        'dti_ratio': [dti_ratio],
        'credit_score': [credit_score],
        'dpd': [dpd],
        'outstanding_balance': [outstanding_balance],
        'par30_amount': [0.0], 'par90_amount': [0.0], 'par30_rate': [0.0], 'par90_rate': [0.0],
        'is_current': [1 if loan_status == 'Current' else 0],
        'is_dpd1_29': [1 if loan_status == 'DPD1-29' else 0],
        'is_dpd30': [0], 'is_dpd60': [0], 'is_dpd90': [0], 'is_npl': [0], 'is_wo': [0],
        'max_dpd_cum': [dpd], 'avg_dpd_cum': [float(dpd)],
        'cnt_dpd1plus_cum': [1 if dpd > 0 else 0],
        'cnt_dpd30plus_cum': [0], 'cnt_dpd90plus_cum': [0], 'ever_dpd30': [0], 'ever_dpd90': [0],
        'max_dpd_3m': [dpd], 'avg_dpd_3m': [float(dpd)], 'cnt_dpd1plus_3m': [1 if dpd > 0 else 0],
        'dpd_worsened': [0], 'dpd_improved': [0],
        'pct_tenor_elapsed': [pct_tenor_elapsed],
        'pct_outstanding': [0.9], # Default value
        'product_type': ['KTA'], # Default value
        'channel': ['Mobile App'], # Default value
        'region': [region],
        'employment_type': [employment_type],
        'risk_grade': [risk_grade],
        'loan_purpose': ['Konsumtif'], # Default value
        'loan_status': [loan_status]
    }
    
    df_pred = pd.DataFrame(data)
    
    # Prediksi
    prediction = model.predict(df_pred)[0]
    probability = model.predict_proba(df_pred)[0]

    # Display Hasil
    st.divider()
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        if prediction == 0:
            st.success("### ✅ Status: LOW RISK")
        else:
            st.error("### ❌ Status: HIGH RISK")
    
    with res_col2:
        st.metric("Probability of Default", f"{round(probability[1]*100, 2)}%")