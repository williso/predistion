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
st.title("🎯 Top Design Combos by Conversion Rate")

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

    for _, row in summary.head(10).iterrows():  # Chỉ lấy top 10 để không quá dài
        combo_filter = (
            (filtered_df['Layout ( Text and Image)'] == row['Layout ( Text and Image)']) &
            (filtered_df['Number of Colors'] == row['Number of Colors']) &
            (filtered_df['Trend Quote'] == row['Trend Quote']) &
            (filtered_df['Recipient/Sender in the Message'] == row['Recipient/Sender in the Message']) &
            (filtered_df['Color'] == row['Color']) &
            (filtered_df['Message Content'] == row['Message Content']) &
            (filtered_df['Style Design'] == row['Style Design']) &
            (filtered_df['Tone Design'] == row['Tone Design']) &
            (filtered_df['Motif Design'] == row['Motif Design'])
        )
        asin_subset = filtered_df[combo_filter]
        title_text = f"👉 {row['Style Design']} | {row['Color']} | {row['Tone Design']} | CR: {row['Avg_Conversion_Rate']:.2%} | Count: {row['Count']}"
        with st.expander(title_text):
            st.dataframe(asin_subset[['ASIN', '7 Day Conversion Rate']])
