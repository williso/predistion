import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Load and preprocess data
@st.cache_data
def load_data():
    df = pd.read_csv("Merged_ASIN_Data.csv")
    df = df[[
        'Niche', 'Product Type', 'Layout ( Text and Image)', 'Number of Colors', 'Trend Quote',
        'Recipient/Sender in the Message', 'Color', 'Message Content', 'Style Design',
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
    group_cols = [
        'Layout ( Text and Image)', 'Number of Colors', 'Trend Quote',
        'Recipient/Sender in the Message', 'Color', 'Message Content',
        'Style Design', 'Tone Design', 'Motif Design'
    ]
    summary = filtered_df.groupby(group_cols).agg(
        Avg_Conversion_Rate=('7 Day Conversion Rate', 'mean'),
        Count=('7 Day Conversion Rate', 'count')
    ).reset_index().sort_values(by='Avg_Conversion_Rate', ascending=False)

    st.subheader("📈 Tổ hợp thiết kế có tỷ lệ chuyển đổi cao nhất")
    st.dataframe(summary)

    st.subheader("🔝 Top 10 tổ hợp có CR cao nhất")
    top10 = summary.head(10).copy()
    top10['Design Combo'] = top10['Style Design'] + ' | ' + top10['Color'] + ' | ' + top10['Tone Design']
    fig_top = px.bar(top10, x='Design Combo', y='Avg_Conversion_Rate', title='Top 10 Design Combos')
    st.plotly_chart(fig_top)

    st.subheader("🔻 Bottom 10 tổ hợp có CR thấp nhất")
    bottom10 = summary.tail(10).copy()
    bottom10['Design Combo'] = bottom10['Style Design'] + ' | ' + bottom10['Color'] + ' | ' + bottom10['Tone Design']
    fig_bottom = px.bar(bottom10, x='Design Combo', y='Avg_Conversion_Rate', title='Bottom 10 Design Combos')
    st.plotly_chart(fig_bottom)

    st.subheader("📊 Phân bố CR theo từng yếu tố")
    selected_factor = st.selectbox(
        "Chọn yếu tố để phân tích",
        [
            'Layout ( Text and Image)', 'Number of Colors', 'Trend Quote',
            'Recipient/Sender in the Message', 'Color', 'Message Content',
            'Style Design', 'Tone Design', 'Motif Design'
        ]
    )
    fig_box = px.box(filtered_df, x=selected_factor, y='7 Day Conversion Rate', points='all', title=f'CR theo {selected_factor}')
    st.plotly_chart(fig_box)
