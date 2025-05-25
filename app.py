import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import skew, norm
import numpy as np

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("Penilaian_Kinerja.csv")

df = load_data()

st.title("Analisis Perbandingan KPI Atasan dan Bawahan")

# Pilih NIPP Atasan dan NIPP Pegawai
col1, col2 = st.columns(2)
with col1:
    nipp_atasan = st.selectbox("Pilih NIPP Atasan:", sorted(df['NIPP_Pekerja'].dropna().unique()))
with col2:
    nipp_bawahan = st.selectbox("Pilih NIPP Pegawai (Bawahan):", sorted(df['NIPP_Pekerja'].dropna().unique()))

# Filter data
atasan_df = df[df['NIPP_Pekerja'] == nipp_atasan]
bawahan_df = df[(df['NIPP_Pekerja'] == nipp_bawahan) & (df['NIPP_Atasan'] == nipp_atasan)]
bawahan_group_df = df[df['NIPP_Atasan'] == nipp_atasan]

if atasan_df.empty or bawahan_group_df.empty:
    st.warning("Data atasan atau bawahan tidak ditemukan.")
else:
    skor_atasan = atasan_df.iloc[0]['Skor_KPI_Final']
    skor_bawahan = bawahan_group_df['Skor_KPI_Final'].dropna()

    if skor_bawahan.empty:
        st.warning("Tidak ada data bawahan untuk NIPP atasan ini.")
    else:
        # Distribusi Normal
        st.subheader("Distribusi Normal Skor KPI Bawahan")
        mean = skor_bawahan.mean()
        std = skor_bawahan.std()
        x = np.linspace(skor_bawahan.min() - 5, skor_bawahan.max() + 5, 100)
        y = norm.pdf(x, mean, std)

        fig, ax = plt.subplots()
        sns.histplot(skor_bawahan, bins=10, kde=False, stat="density", color='skyblue', ax=ax)
        ax.plot(x, y, color='red', label='Kurva Normal')
        ax.axvline(skor_atasan, color='green', linestyle='--', label=f'Skor Atasan ({skor_atasan})')
        ax.axvline(mean, color='blue', linestyle='--', label=f'Rata-rata ({mean:.2f})')
        ax.legend()
        st.pyplot(fig)

        # Skewness
        skewness = skew(skor_bawahan)
        if skewness < -0.5:
            skew_category = "Skew Kiri (Left Skewed)"
        elif skewness > 0.5:
            skew_category = "Skew Kanan (Right Skewed)"
        else:
            skew_category = "Normal / Simetris"
        st.markdown(f"**Skewness**: {skewness:.2f} → {skew_category}")

        # Gap KPI dalam persen
        gap_percent = ((skor_atasan - mean) / mean) * 100
        st.markdown(f"**Rata-rata Skor KPI Bawahan**: {mean:.2f}")
        st.markdown(f"**Skor KPI Atasan**: {skor_atasan:.2f}")
        st.markdown(f"**Gap Atasan vs Rata-rata Bawahan**: {gap_percent:.2f}%")

