import streamlit as st
import pandas as pd
import numpy as np

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
st.title("📊 Design Combination Conversion Stats")

df = load_data()

# Chọn nhiều Niche và Product Type
selected_niches = st.multiselect("Select Niche(s)", sorted(df['Niche'].unique()))
if selected_niches:
    filtered_product_types = df[df['Niche'].isin(selected_niches)]['Product Type'].unique()
    selected_product_types = st.multiselect("Select Product Type(s)", sorted(filtered_product_types))
else:
    selected_product_types = []

# Lọc theo Niche và Product Type
filtered_df = df[
    (df['Niche'].isin(selected_niches)) &
    (df['Product Type'].isin(selected_product_types))
]

if filtered_df.empty:
    st.warning("⚠️ Không có dữ liệu cho tổ hợp Niche và Product Type đã chọn.")
else:
    group_cols = [
        'Layout ( Text and Image)', 'Number of Colors', 'Trend Quote',
        'Recipient/Sender in the Message', 'Color', 'Message Content',
        'Style Design', 'Tone Design', 'Motif Design'
    ]
    grouped = filtered_df.groupby(group_cols).agg(
        Avg_Conversion_Rate=('7 Day Conversion Rate', 'mean'),
        ASINs=('ASIN', lambda x: sorted(set(x)))
    ).reset_index()

    grouped_no_duplicates = grouped.drop_duplicates(subset=['Avg_Conversion_Rate'])

    top_10 = grouped_no_duplicates.sort_values(by='Avg_Conversion_Rate', ascending=False).head(10)
    bottom_10 = grouped_no_duplicates.sort_values(by='Avg_Conversion_Rate', ascending=True).head(10)

    def show_combinations(df_grouped, title):
        st.subheader(title)
        for idx, row in df_grouped.iterrows():
            with st.expander(f"{row['Style Design']} | {row['Tone Design']} | CR: {row['Avg_Conversion_Rate']:.2%}"):
                asin_list = row['ASINs']
                st.markdown(f"**ASINs:** {', '.join(asin_list)}")

                asin_data = filtered_df[filtered_df['ASIN'].isin(asin_list)]
                if not asin_data.empty:
                    summary = asin_data.groupby('ASIN')[['7 Day Conversion Rate']].mean().reset_index()
                    st.dataframe(summary)

    show_combinations(top_10, "📈 Tổ hợp thiết kế có tỷ lệ chuyển đổi cao nhất")
    show_combinations(bottom_10, "🔻 Tổ hợp thiết kế có tỷ lệ chuyển đổi thấp nhất")
