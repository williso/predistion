import streamlit as st
import pandas as pd

# Load and preprocess data
@st.cache_data
def load_data():
    df = pd.read_csv("Merged_ASIN_Data.csv")
    df = df[[
        'ASIN', 'Niche', 'Product Type', 'Layout ( Text and Image)', 'Number of Colors', 'Trend Quote',
        'Recipient/Sender in the Message', 'Color', 'Message Content', 'Style Design',
        'Tone Design', 'Motif Design', '7 Day Conversion Rate'
    ]].dropna()
    df['7 Day Conversion Rate'] = pd.to_numeric(df['7 Day Conversion Rate'], errors='coerce')
    df.dropna(subset=['7 Day Conversion Rate'], inplace=True)
    return df

# Streamlit app
st.title("📊 Tổng hợp tổ hợp thiết kế theo ASIN và CR")

df = load_data()

selected_niche = st.selectbox("Chọn Niche", sorted(df['Niche'].unique()))
filtered_product_types = df[df['Niche'] == selected_niche]['Product Type'].unique()
selected_product_type = st.selectbox("Chọn Product Type", sorted(filtered_product_types))

filtered_df = df[(df['Niche'] == selected_niche) & (df['Product Type'] == selected_product_type)]

if filtered_df.empty:
    st.warning("Không có dữ liệu cho tổ hợp Niche và Product Type này.")
else:
    group_cols = [
        'Layout ( Text and Image)', 'Number of Colors', 'Trend Quote',
        'Recipient/Sender in the Message', 'Color', 'Message Content',
        'Style Design', 'Tone Design', 'Motif Design'
    ]

    summary_df = (
        filtered_df
        .groupby(group_cols)
        .agg(
            Avg_CR=('7 Day Conversion Rate', 'mean'),
            Count=('ASIN', 'count'),
            ASINs=('ASIN', lambda x: ', '.join(sorted(x.unique())))
        )
        .reset_index()
        .sort_values(by='Avg_CR', ascending=False)
    )

    st.subheader("📈 Bảng tổng hợp tổ hợp thiết kế theo ASIN")
    st.dataframe(summary_df, use_container_width=True)
