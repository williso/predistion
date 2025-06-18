import streamlit as st
import pandas as pd

# -------------------------
# 1. Load và xử lý dữ liệu
# -------------------------
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

# ------------------------
# 2. Giao diện Streamlit
# ------------------------
st.title("📊 Tổng hợp tổ hợp thiết kế theo ASIN và CR")

df = load_data()

# ---------------------------------------
# 3. Chọn Niche và Product Type phù hợp
# ---------------------------------------
selected_niche = st.selectbox("🔍 Chọn Niche", sorted(df['Niche'].unique()))
filtered_product_types = df[df['Niche'] == selected_niche]['Product Type'].unique()
selected_product_type = st.selectbox("📦 Chọn Product Type", sorted(filtered_product_types))

# Lọc theo Niche và Product Type
filtered_df = df[(df['Niche'] == selected_niche) & (df['Product Type'] == selected_product_type)]

# ------------------------------------------
# 4. Tổng hợp tổ hợp thiết kế
# ------------------------------------------
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
        Count=('ASIN', 'count')
    )
    .reset_index()
    .sort_values(by='Avg_CR', ascending=False)
)

# Hiển thị bảng tổng hợp tổ hợp
st.subheader("📈 Tổng hợp tất cả tổ hợp thiết kế")
selected_row = st.dataframe(summary_df, use_container_width=True, hide_index=True)

# ------------------------------------------
# 5. Lọc và hiển thị ASIN theo tổ hợp chọn
# ------------------------------------------
# Cho phép chọn tổ hợp từ bảng bằng dropdown
with st.expander("📌 Xem danh sách ASIN theo tổ hợp thiết kế"):
    st.markdown("### 🧩 Chọn một tổ hợp:")

    # Tạo tuple định danh tổ hợp
    summary_df["Tổ hợp"] = summary_df[group_cols].astype(str).agg(" | ".join, axis=1)
    option = st.selectbox("Chọn tổ hợp thiết kế:", summary_df["Tổ hợp"].tolist())

    # Lấy đúng dòng tổ hợp được chọn
    selected_combo_row = summary_df[summary_df["Tổ hợp"] == option].iloc[0]

    # Tạo điều kiện lọc tương ứng
    condition = True
    for col in group_cols:
        condition &= (filtered_df[col] == selected_combo_row[col])

    asin_df = filtered_df[condition].sort_values(by='7 Day Conversion Rate', ascending=False)

    # Hiển thị danh sách ASIN
    st.markdown("### 📋 Danh sách ASIN trong tổ hợp đã chọn")
    st.dataframe(asin_df[['ASIN', '7 Day Conversion Rate']], use_container_width=True)
