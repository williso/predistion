import streamlit as st
import pandas as pd
import plotly.express as px

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
    
    for idx, row in summary.iterrows():
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
            display_cols = ['ASIN', '7 Day Conversion Rate'] if 'ASIN' in asin_subset.columns else ['7 Day Conversion Rate']
            st.dataframe(asin_subset[display_cols])

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
        group_cols
    )
    fig_box = px.box(filtered_df, x=selected_factor, y='7 Day Conversion Rate', points='all', title=f'CR theo {selected_factor}')
    st.plotly_chart(fig_box)
