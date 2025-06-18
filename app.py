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
st.dataframe(summary_df, use_container_width=True, hide_index=True)

# ------------------------------------------
# 5. Chia ASIN theo nhóm CR
# ------------------------------------------
with st.expander("📌 Xem phân loại ASIN theo nhóm CR trong tổ hợp đã chọn"):
    st.markdown("### 🧩 Chọn một tổ hợp:")

    # Tạo chuỗi mô tả tổ hợp
    summary_df["Tổ hợp"] = summary_df[group_cols].astype(str).agg(" | ".join, axis=1)
    option = st.selectbox("Chọn tổ hợp thiết kế:", summary_df["Tổ hợp"].tolist())

    # Lấy dòng tương ứng
    selected_combo_row = summary_df[summary_df["Tổ hợp"] == option].iloc[0]

    # Lọc ASIN thuộc tổ hợp đó
    condition = True
    for col in group_cols:
        condition &= (filtered_df[col] == selected_combo_row[col])
    asin_df = filtered_df[condition].copy()

    # Tính phân vị cho CR
    q33 = asin_df['7 Day Conversion Rate'].quantile(0.33)
    q66 = asin_df['7 Day Conversion Rate'].quantile(0.66)

    # Phân nhóm
    asin_df['CR Group'] = pd.cut(
        asin_df['7 Day Conversion Rate'],
        bins=[-float('inf'), q33, q66, float('inf')],
        labels=['Dưới trung bình', 'Trung bình', 'Top']
    )

    # Hiển thị từng nhóm
    st.markdown("#### 🟢 Nhóm Top")
    st.dataframe(asin_df[asin_df['CR Group'] == 'Top'][['ASIN']], use_container_width=True, hide_index=True)

    st.markdown("#### 🟡 Nhóm Trung bình")
    st.dataframe(asin_df[asin_df['CR Group'] == 'Trung bình'][['ASIN']], use_container_width=True, hide_index=True)

    st.markdown("#### 🔴 Nhóm Dưới trung bình")
    st.dataframe(asin_df[asin_df['CR Group'] == 'Dưới trung bình'][['ASIN']], use_container_width=True, hide_index=True)
