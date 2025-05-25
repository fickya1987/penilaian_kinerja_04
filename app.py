import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import openai
import os
from dotenv import load_dotenv
import scipy.stats as stats

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

    # Pastikan skor numerik
    score_cols = ["Skor_KPI_Final", "Skor_Assessment", "Skor_Kinerja_Individu"]
    for col in score_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Distribusi 3 grafik
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

    # Skewness info
    skewness_result = {col: stats.skew(df[col].dropna()) for col in score_cols}
    st.subheader("📈 Analisis Skewness Distribusi")
    for col, skew in skewness_result.items():
        arah = "kanan (positif)" if skew > 0.5 else "kiri (negatif)" if skew < -0.5 else "simetris/tengah"
        st.markdown(f"**{col}**: Skewness = {skew:.2f} → Distribusi cenderung ke **{arah}**")

    # Perbandingan KPI atasan vs bawahan
    st.subheader("📊 Perbandingan KPI Atasan vs Bawahan")
    if "NIPP_Atasan" in df.columns and "NIPP_Pekerja" in df.columns:
        df_compare = df.dropna(subset=["NIPP_Atasan", "NIPP_Pekerja"] + score_cols)
        df_compare = df_compare.merge(
            df, left_on="NIPP_Atasan", right_on="NIPP_Pekerja", suffixes=('_bawahan', '_atasan')
        )
        for col in score_cols:
            df_compare[f"Gap_{col}"] = (
                (df_compare[f"{col}_bawahan"] - df_compare[f"{col}_atasan"]) / df_compare[f"{col}_atasan"]
            ) * 100

        selected_gap_col = st.selectbox("Pilih Skor untuk Lihat Gap %", [f"Gap_{col}" for col in score_cols])
        fig, ax = plt.subplots()
        sns.histplot(df_compare[selected_gap_col].dropna(), kde=True, ax=ax, color="purple")
        ax.set_title(f"Distribusi {selected_gap_col}")
        st.pyplot(fig)

        st.dataframe(df_compare[[
            "NIPP_Pekerja_bawahan", "Nama_Posisi_bawahan", "NIPP_Atasan"
        ] + score_cols + [f"Gap_{col}" for col in score_cols]])
    else:
        st.warning("Kolom 'NIPP_Atasan' atau 'NIPP_Pekerja' tidak ditemukan di file Anda.")

    # Narasi otomatis dengan GPT-4o
    if openai.api_key:
        with st.expander("🧠 Narasi Analisis dari Pelindo AI"):
            prompt = f"""
            Anda adalah Analis Senior SDM PT Pelabuhan Indonesia (Persero).

            Berdasarkan data distribusi berikut:
            - Skor KPI Final: min {df['Skor_KPI_Final'].min():.2f}, max {df['Skor_KPI_Final'].max():.2f}, mean {df['Skor_KPI_Final'].mean():.2f}
            - Skor Assessment: min {df['Skor_Assessment'].min():.2f}, max {df['Skor_Assessment'].max():.2f}, mean {df['Skor_Assessment'].mean():.2f}
            - Skor Kinerja Individu: min {df['Skor_Kinerja_Individu'].min():.2f}, max {df['Skor_Kinerja_Individu'].max():.2f}, mean {df['Skor_Kinerja_Individu'].mean():.2f}

            Skewness:
            - Skor KPI Final: {skewness_result['Skor_KPI_Final']:.2f}
            - Skor Assessment: {skewness_result['Skor_Assessment']:.2f}
            - Skor Kinerja Individu: {skewness_result['Skor_Kinerja_Individu']:.2f}

            Tulis analisis menyeluruh terkait kecenderungan distribusi, perbedaan kinerja antara atasan dan bawahan, dan rekomendasi pengembangan SDM.
            """
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            st.markdown(response.choices[0].message.content)
    else:
        st.warning("OPENAI_API_KEY belum tersedia di file .env.")
