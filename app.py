import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import openai
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Setup halaman
st.set_page_config(page_title="Distribusi & Analisis Kinerja", layout="wide")
st.title("📊 Distribusi Skor Penilaian & Analisis Pelindo AI")

# Upload data
uploaded_file = st.file_uploader("Unggah file CSV Penilaian Kinerja", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    for col in ["Skor_KPI_Final", "Skor_Assessment", "Skor_Kinerja_Individu"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    def classify_level(pos):
        if "Pelindo" in pos or pos == "Direktur Utama":
            return "Direktur"
        elif "Group Head" in pos:
            return "Group Head"
        elif "Department Head" in pos:
            return "Department Head"
        else:
            return "Pegawai"

    df['Level'] = df['Nama_Posisi'].apply(classify_level)

    st.subheader("Distribusi Skor Penilaian")
    col1, col2, col3 = st.columns(3)

    with col1:
        fig, ax = plt.subplots()
        sns.histplot(df["Skor_KPI_Final"].dropna(), kde=True, ax=ax, color="steelblue")
        ax.set_title("Distribusi Skor KPI Final")
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots()
        sns.histplot(df["Skor_Assessment"].dropna(), kde=True, ax=ax, color="orange")
        ax.set_title("Distribusi Skor Assessment")
        st.pyplot(fig)

    with col3:
        fig, ax = plt.subplots()
        sns.histplot(df["Skor_Kinerja_Individu"].dropna(), kde=True, ax=ax, color="green")
        ax.set_title("Distribusi Skor Kinerja Individu")
        st.pyplot(fig)

    st.subheader("📈 Perbandingan Rata-rata Skor per Level")
    level_scores = df.groupby('Level')[['Skor_KPI_Final', 'Skor_Assessment', 'Skor_Kinerja_Individu']].mean().reset_index()
    melt_df = level_scores.melt(id_vars='Level', var_name='Tipe_Skor', value_name='Nilai_Rata2')
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=melt_df, x='Level', y='Nilai_Rata2', hue='Tipe_Skor', palette='Set2')
    ax.set_title("Rata-rata Skor KPI, Assessment, dan Kinerja per Level Jabatan")
    st.pyplot(fig)

    st.subheader("📊 Simulasi Penentuan Kuota Berdasarkan Kurva Normal")
    st.markdown("""
    Proses ini mengikuti alur: 
    - Penarikan data performa per level unit kerja
    - Perhitungan gap performa antar level unit
    - Penyesuaian bobot distribusi berdasarkan gap
    - Mapping ke kurva normal (skewed left, normal, skewed right)
    - Penentuan kuota kinerja dan kategorisasi hasil tiap unit hingga ke level terkecil
    """)
    
    gap_df = df.copy()
    gap_df['Skor_Normalisasi'] = (gap_df['Skor_KPI_Final'] - gap_df['Skor_KPI_Final'].mean()) / gap_df['Skor_KPI_Final'].std()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(gap_df['Skor_Normalisasi'], kde=True, bins=20, color='purple')
    ax.set_title("Simulasi Kurva Normalisasi Skor KPI")
    st.pyplot(fig)

    if openai.api_key:
        with st.expander("🧠 Narasi Analisis dari Pelindo AI"):
            prompt = f"""
            Anda adalah analis SDM Pelindo. Simulasikan penentuan kuota kinerja unit kerja berdasarkan proses berikut:
            1. Hitung gap antar level jabatan berdasarkan KPI.
            2. Terapkan bobot koreksi distribusi berdasarkan gap (%)
            3. Pemetaan kurva normalisasi (skewed/normal)
            4. Tetapkan kuota dan kategori akhir sesuai distribusi normal ke unit kerja terkecil
            Sertakan insight dan rekomendasi pembagian kuota kinerja yang adil dan berbasis data.
            """
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            st.markdown(response.choices[0].message.content)

    st.subheader("📌 Analisis Per Pekerja")
    selected_nipp = st.selectbox("Pilih NIPP", df["NIPP_Pekerja"].unique())
    selected_row = df[df["NIPP_Pekerja"] == selected_nipp].iloc[0]

    st.markdown(
        f"**Nama Posisi**: {selected_row['Nama_Posisi']}  \n"
        f"**Skor KPI Final**: {selected_row['Skor_KPI_Final']}  \n"
        f"**Skor Assessment**: {selected_row['Skor_Assessment']}  \n"
        f"**Skor Kinerja Individu**: {selected_row['Skor_Kinerja_Individu']}  \n"
    )

    if openai.api_key:
        with st.expander("🔍 Narasi Pelindo AI untuk Pekerja Ini"):
            prompt = f"""
            Anda adalah analis SDM PT Pelabuhan Indonesia (Persero) yang melakukan evaluasi performa tahunan berbasis standar resmi perusahaan.
            Gunakan referensi: 80% KPI + 20% Perilaku (AKHLAK) — Delivery, Leadership, Communication, Teamwork
            Evaluasilah pekerja ini berdasarkan posisinya: {selected_row['Nama_Posisi']} dengan skor:
            - KPI: {selected_row['Skor_KPI_Final']}
            - Assessment: {selected_row['Skor_Assessment']}
            - Kinerja Individu: {selected_row['Skor_Kinerja_Individu']}
            Tuliskan narasi performa, kekuatan, area pengembangan, dan rekomendasi intervensi (coaching/CMC/rutin).
            """
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            st.markdown(response.choices[0].message.content)
