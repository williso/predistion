import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data
def load_data():
    df = pd.read_csv("Merged_ASIN_Data.csv")
    df = df[[
        'ASIN', 'Niche', 'Product Type', 'Layout ( Text and Image)', 'Number of Colors', 'Trend Quote',
        'Recipient/Sender in the Message', 'Color', 'Message Content', 'Style Design',
        'Tone Design', 'Motif Design', '7 Day Conversion Rate',
        # thêm các chỉ số ads nếu có, ví dụ:
        'Impressions', 'Clicks', 'Orders', 'Spend', 'Sales'  # (tuỳ theo file bạn có)
    ]].dropna()
    df['7 Day Conversion Rate'] = pd.to_numeric(df['7 Day Conversion Rate'], errors='coerce')
    df.dropna(subset=['7 Day Conversion Rate'], inplace=True)
    return df

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
    
    grouped = filtered_df.groupby(group_cols).agg(
        Avg_Conversion_Rate=('7 Day Conversion Rate', 'mean'),
    ).reset_index()

    grouped['ASINs'] = filtered_df.groupby(group_cols)['ASIN'].apply(lambda x: sorted(set(x))).values

    top_10 = grouped.sort_values(by='Avg_Conversion_Rate', ascending=False).head(10)
    bottom_10 = grouped.sort_values(by='Avg_Conversion_Rate', ascending=True).head(10)

    def show_combinations(df_grouped, title):
        st.subheader(title)
        for idx, row in df_grouped.iterrows():
            with st.expander(f"{row['Style Design']} | {row['Tone Design']} | CR: {row['Avg_Conversion_Rate']:.2%}"):
                asin_list = row['ASINs']
                st.markdown(f"**ASINs:** {', '.join(asin_list)}")
                
                asin_data = filtered_df[filtered_df['ASIN'].isin(asin_list)]
                numeric_cols = ['Impressions', 'Clicks', 'Orders', 'Spend', 'Sales']  # nếu không có cột nào thì xóa dòng này
                summary = asin_data.groupby('ASIN')[numeric_cols + ['7 Day Conversion Rate']].mean().reset_index()
                st.dataframe(summary)

    show_combinations(top_10, "📈 Tổ hợp thiết kế có tỷ lệ chuyển đổi cao nhất")
    show_combinations(bottom_10, "🔻 Tổ hợp thiết kế có tỷ lệ chuyển đổi thấp nhất")
