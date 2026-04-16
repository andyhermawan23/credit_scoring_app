import streamlit as st
import pandas as pd
import numpy as np
import pickle
import sklearn.compose._column_transformer
import sys
import plotly.graph_objects as go
from datetime import datetime

# --- FIX UNTUK PYTHON 3.13 & SKLEARN 1.6.1 ---
class _RemainderColsList(list):
    pass
sklearn.compose._column_transformer._RemainderColsList = _RemainderColsList
sys.modules['__main__']._RemainderColsList = _RemainderColsList

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="PADI - Dashboard UMKM", layout="wide")

# CSS KHUSUS UNTUK MERAPIKAN SIDEBAR (CONTAINER KIRI)
st.markdown("""
    <style>
    /* Mengubah background sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a3c5e !important;
    }
    
    /* Mengatur gaya teks navigasi di sidebar */
    [data-testid="stSidebar"] .st-emotion-cache-17l243g {
        color: white !important;
    }
    
    /* Mengubah warna label Radio Button di sidebar jadi putih & lebih besar */
    [data-testid="stSidebar"] .st-emotion-cache-1647z6a {
        color: rgba(255, 255, 255, 0.8) !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        padding: 10px 0px !important;
    }

    /* Mengubah teks "Navigasi" atau heading di sidebar */
    [data-testid="stSidebar"] p {
        color: white !important;
        font-size: 14px !important;
    }

    /* Styling kartu utama */
    .stCard {
        background-color: white; 
        padding: 24px; 
        border-radius: 12px;
        border: 1px solid #e2e8f0; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- COLORS ---
COLORS = {"primary": "#1a3c5e", "success": "#10b981", "warning": "#f59e0b", "danger": "#ef4444"}

# --- LOAD MODEL ---
@st.cache_resource
def load_model():
    try:
        with open('best_model.pkl', 'rb') as file:
            return pickle.load(file)
    except:
        return None

model = load_model()

# --- SIDEBAR (CONTAINER KIRI) ---
with st.sidebar:
    # Header Branding
    st.markdown(f"""
        <div style='padding: 10px 0px 20px 0px;'>
            <h1 style='color: white; font-size: 28px; margin-bottom: 0;'>PADI</h1>
            <p style='color: #38bdf8; font-size: 12px; margin-top: 0; font-weight: 600;'>
                Penilaian Alternatif Data Inklusif
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Menu Navigasi dengan ukuran teks yang sudah disesuaikan via CSS di atas
    menu = st.radio(
        "MENU UTAMA",
        ["📋 Input Scoring", "📊 Hasil Skor", "🔔 Early Warning"],
        index=0
    )
    
    # Push content to bottom
    st.markdown("<br>" * 10, unsafe_allow_html=True)
    st.divider()
    st.markdown("""
        <div style='color: rgba(255,255,255,0.4); font-size: 11px; text-align: center;'>
            v1.0.0 · PIDI Hackathon 2026<br>
            Designed for Financial Inclusion
        </div>
    """, unsafe_allow_html=True)

# --- HEADER COMPONENT ---
def render_header(title, subtitle):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<h2 style='color:#1e293b; margin-bottom:0;'>{title}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#64748b;'>{subtitle}</p>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div style='background:white; padding:8px; border-radius:8px; border:1px solid #e2e8f0; text-align:center; font-size:12px; color:#64748b; margin-top:15px;'>
                {datetime.now().strftime('%d %b %Y · %H:%M')} WIB
            </div>
            """, unsafe_allow_html=True)
    st.divider()

# --- APP LOGIC ---
if "prob_default" not in st.session_state:
    st.session_state.prob_default = None

if menu == "📋 Input Scoring":
    render_header("Form Input Scoring", "Analisis Kelayakan Kredit UMKM")
    
    if model is None:
        st.error("Model .pkl tidak ditemukan di direktori.")
        st.stop()

    with st.form("main_form"):
        # Section Header ala React Template
        st.markdown(f"<p style='color:{COLORS['primary']}; font-weight:700; text-transform:uppercase; font-size:12px; letter-spacing:0.1em;'>I. Profil & Pinjaman</p>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            tenor_months = st.number_input("Tenor (Bulan)", 12, 24, 12)
            loan_amount = st.number_input("Jumlah Pinjaman", 1000000.0, 20000000.0, 5000000.0)
        with c2:
            borrower_age = st.number_input("Usia Debitur", 21, 59, 30)
            employment_type = st.selectbox("Pekerjaan", ['PNS', 'Karyawan Tetap', 'Profesional', 'Wiraswasta', 'Karyawan Kontrak'])
        with c3:
            region = st.selectbox("Wilayah", ['Bali & Nusa Tenggara', 'Jawa', 'Sumatera', 'Kalimantan', 'Sulawesi'])
            risk_grade = st.selectbox("Risk Grade", ['A', 'B', 'C', 'D', 'E'])

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:{COLORS['primary']}; font-weight:700; text-transform:uppercase; font-size:12px; letter-spacing:0.1em;'>II. Data Keuangan & Kredit</p>", unsafe_allow_html=True)
        c4, c5, c6 = st.columns(3)
        with c4:
            monthly_income = st.number_input("Pendapatan Bulanan", 300000.0, 30000000.0, 5000000.0)
            monthly_installment = st.number_input("Angsuran Bulanan", 50000.0, 3000000.0, 500000.0)
        with c5:
            dti_ratio = st.slider("DTI Ratio", 0.1, 0.6, 0.3)
            interest_rate = st.number_input("Bunga (%)", 1.0, 5.0, 2.0)
        with c6:
            credit_score = st.slider("Credit Score", 300, 850, 600)
            loan_status = st.selectbox("Status Kredit", ['Current', 'DPD1-29'])

        # Hidden/Fixed Features (tetap dikirim ke model sesuai requirement 42 fitur)
        dpd = 0 # Default jika status 'Current'
        pct_tenor_elapsed = 0.05

        submit = st.form_submit_button("HITUNG SKOR SEKARANG →", use_container_width=True)

    if submit:
        # Mapping data ke 42 fitur (Urutan harus sama dengan training)
        data = {
            'tenor_months': [tenor_months], 'loan_amount': [loan_amount], 'monthly_installment': [monthly_installment],
            'interest_rate_monthly_pct': [interest_rate], 'borrower_age': [borrower_age], 'monthly_income': [monthly_income],
            'dti_ratio': [dti_ratio], 'credit_score': [credit_score], 'dpd': [dpd],
            'outstanding_balance': [loan_amount * 0.8], 'par30_amount': [0.0], 'par90_amount': [0.0], 
            'par30_rate': [0.0], 'par90_rate': [0.0],
            'is_current': [1 if loan_status == 'Current' else 0],
            'is_dpd1_29': [1 if loan_status == 'DPD1-29' else 0],
            'is_dpd30': [0], 'is_dpd60': [0], 'is_dpd90': [0], 'is_npl': [0], 'is_wo': [0],
            'max_dpd_cum': [dpd], 'avg_dpd_cum': [float(dpd)],
            'cnt_dpd1plus_cum': [1 if dpd > 0 else 0],
            'cnt_dpd30plus_cum': [0], 'cnt_dpd90plus_cum': [0], 'ever_dpd30': [0], 'ever_dpd90': [0],
            'max_dpd_3m': [dpd], 'avg_dpd_3m': [float(dpd)], 'cnt_dpd1plus_3m': [1 if dpd > 0 else 0],
            'dpd_worsened': [0], 'dpd_improved': [0],
            'pct_tenor_elapsed': [pct_tenor_elapsed], 'pct_outstanding': [0.9], 
            'product_type': ['KTA'], 'channel': ['Mobile App'], 'region': [region],
            'employment_type': [employment_type], 'risk_grade': [risk_grade], 
            'loan_purpose': ['Konsumtif'], 'loan_status': [loan_status]
        }
        
        df_pred = pd.DataFrame(data)
        st.session_state.prob_default = model.predict_proba(df_pred)[0][1]
        st.balloons()
        st.success("Analisis Selesai! Klik menu 'Hasil Skor' di samping untuk detailnya.")

elif menu == "📊 Hasil Skor":
    render_header("Hasil Penilaian", "Parameter Inklusif & Probabilitas Default")
    
    if st.session_state.prob_default is None:
        st.info("Silakan masukkan data pada menu Input Scoring terlebih dahulu.")
    else:
        prob = st.session_state.prob_default
        score = int(850 * (1 - prob)) # Konversi probabilitas ke skor 300-850 sederhana
        
        c1, c2 = st.columns([1, 2])
        with c1:
            # GAUGE
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = score,
                gauge = {
                    'axis': {'range': [300, 850]},
                    'bar': {'color': COLORS['success'] if prob < 0.3 else COLORS['danger']},
                    'steps': [
                        {'range': [300, 550], 'color': "#fee2e2"},
                        {'range': [550, 700], 'color': "#fef3c7"},
                        {'range': [700, 850], 'color': "#d1fae5"}
                    ]
                }
            ))
            fig.update_layout(height=280, margin=dict(l=30, r=30, t=50, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.markdown(f"""
                <div class='stCard'>
                    <h3 style='margin-top:0;'>Analisis Risiko</h3>
                    <p>Berdasarkan model <b>Decision Tree</b>, nasabah dikategorikan sebagai:</p>
                    <h2 style='color:{"#10b981" if prob < 0.3 else "#ef4444"}'>
                        {"LOW RISK" if prob < 0.3 else "HIGH RISK" if prob > 0.5 else "MEDIUM RISK"}
                    </h2>
                    <hr>
                    <p style='font-size:14px;'>Probabilitas Gagal Bayar: <b>{prob*100:.2f}%</b></p>
                    <p style='font-size:14px;'>Rekomendasi: <b>{"LAYAK DISPENSASI" if prob < 0.3 else "TINJAU ULANG"}</b></p>
                </div>
            """, unsafe_allow_html=True)

elif menu == "🔔 Early Warning":
    render_header("Panel Early Warning", "Deteksi Anomali pada Portofolio Aktif")
    st.warning("Menampilkan anomali perilaku pembayaran menggunakan Isolation Forest.")
    # (Visualisasi anomali bisa ditambahkan di sini)