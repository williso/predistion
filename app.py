import streamlit as st
import pandas as pd
import numpy as np

# Load and preprocess data
@st.cache_data
def load_data():
    df = pd.read_csv("Merged_ASIN_Data.csv")
    df = df[[
        'Niche', 'Product Type', 'Color', 'Message Content', 'Style Design',
        'Tone Design', 'Motif Design', '7 Day Conversion Rate'
    ]].dropna()
    df['7 Day Conversion Rate'] = pd.to_numeric(df['7 Day Conversion Rate'], errors='coerce')
    df.dropna(subset=['7 Day Conversion Rate'], inplace=True)
    return df

# Streamlit app
st.title("📊 Design Combination Conversion Stats")

df = load_data()

selected_niche = st.selectbox("Select Niche", sorted(df['Niche'].unique()))
filtered_product_types = df[df['Niche'] == selected_niche]['Product Type'].unique()
selected_product_type = st.selectbox("Select Product Type", sorted(filtered_product_types))

filtered_df = df[(df['Niche'] == selected_niche) & (df['Product Type'] == selected_product_type)]

if filtered_df.empty:
    st.warning("Không có dữ liệu cho tổ hợp Niche và Product Type này.")
else:
    group_cols = ['Color', 'Message Content', 'Style Design', 'Tone Design', 'Motif Design']
    summary = filtered_df.groupby(group_cols).agg(
        Avg_Conversion_Rate=('7 Day Conversion Rate', 'mean'),
        Count=('7 Day Conversion Rate', 'count')
    ).reset_index().sort_values(by='Avg_Conversion_Rate', ascending=False)

    st.subheader("📈 Tổ hợp thiết kế có tỷ lệ chuyển đổi cao nhất")
    st.dataframe(summary)

    st.bar_chart(summary.set_index('Style Design')['Avg_Conversion_Rate'])
