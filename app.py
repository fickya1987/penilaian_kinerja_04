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

# Pilih NIPP Atasan
nipp_atasan = st.selectbox("Pilih NIPP Atasan:", sorted(df['NIPP_Pekerja'].dropna().unique()))

# Filter data
atasan_df = df[df['NIPP_Pekerja'] == nipp_atasan]
bawahan_group_df = df[df['NIPP_Atasan'] == nipp_atasan]

if atasan_df.empty or bawahan_group_df.empty:
    st.warning("Data atasan atau bawahan tidak ditemukan.")
else:
    skor_atasan = atasan_df.iloc[0]['Skor_KPI_Final']
    skor_bawahan = bawahan_group_df['Skor_KPI_Final'].dropna()

    if skor_bawahan.empty:
        st.warning("Tidak ada data bawahan untuk NIPP atasan ini.")
    else:
        # Distribusi Normal + Bar Chart per NIPP
        st.subheader("Distribusi Skor KPI Bawahan (dengan NIPP)")
        mean = skor_bawahan.mean()
        std = skor_bawahan.std()

        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Bar chart KPI Bawahan
        nipp_labels = bawahan_group_df['NIPP_Pekerja'].astype(str).values
        ax1.bar(nipp_labels, skor_bawahan, color='skyblue', label='Skor KPI Bawahan')
        ax1.axhline(skor_atasan, color='green', linestyle='--', linewidth=2, label=f'Skor Atasan ({skor_atasan:.3f})')
        ax1.axhline(mean, color='blue', linestyle='--', linewidth=2, label=f'Rata-rata ({mean:.2f})')
        ax1.set_ylabel("Skor KPI")
        ax1.set_xlabel("NIPP Pekerja")
        ax1.set_xticklabels(nipp_labels, rotation=45, ha='right')

        # Distribusi Normal Overlay
        ax2 = ax1.twinx()
        x = np.linspace(min(skor_bawahan)-5, max(skor_bawahan)+5, 200)
        y = norm.pdf(x, mean, std)
        ax2.plot(x, y, color='red', label='Kurva Normal')
        ax2.set_ylabel("Density", color='red')
        ax2.tick_params(axis='y', labelcolor='red')

        fig.tight_layout()
        fig.legend(loc='upper left', bbox_to_anchor=(0.01, 0.99))
        st.pyplot(fig)

        # Tampilkan daftar NIPP Bawahan
        st.markdown("**Daftar NIPP Bawahan yang Dinaungi oleh Atasan Ini:**")
        st.write(bawahan_group_df['NIPP_Pekerja'].dropna().unique())

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
