import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import skew

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("Penilaian_Kinerja.csv")

df = load_data()

st.title("Analisis Perbandingan KPI Atasan dan Bawahan")

# Pilih Atasan
atasan_options = df['NIPP_Atasan'].dropna().unique()
nipp_atasan = st.selectbox("Pilih NIPP Atasan:", sorted(atasan_options))

# Filter data
bawahan_df = df[df['NIPP_Atasan'] == nipp_atasan]
atasan_df = df[df['NIPP_Pekerja'] == nipp_atasan]

if atasan_df.empty:
    st.warning("Data atasan tidak ditemukan.")
else:
    skor_atasan = atasan_df.iloc[0]['Skor_KPI_Final']
    skor_bawahan = bawahan_df['Skor_KPI_Final'].dropna()

    if skor_bawahan.empty:
        st.warning("Tidak ada data bawahan untuk NIPP atasan ini.")
    else:
        # Histogram distribusi normal
        st.subheader("Distribusi Skor KPI Bawahan")
        fig, ax = plt.subplots()
        sns.histplot(skor_bawahan, kde=True, bins=10, ax=ax)
        ax.axvline(skor_atasan, color='red', linestyle='--', label=f'Skor Atasan ({skor_atasan})')
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
        avg_bawahan = skor_bawahan.mean()
        gap_percent = ((skor_atasan - avg_bawahan) / avg_bawahan) * 100
        st.markdown(f"**Rata-rata Skor KPI Bawahan**: {avg_bawahan:.2f}")
        st.markdown(f"**Skor KPI Atasan**: {skor_atasan:.2f}")
        st.markdown(f"**Gap Atasan vs Bawahan**: {gap_percent:.2f}%")

