import streamlit as st
import pandas as pd

# -------------------------
# 1. Load và xử lý dữ liệu
# -------------------------
@st.cache_data
def load_data():
    # Đọc file CSV
    df = pd.read_csv("Merged_ASIN_Data.csv")
    
    # Giữ lại các cột cần thiết và loại bỏ hàng thiếu dữ liệu
    df = df[[
        'ASIN', 'Niche', 'Product Type', 'Layout ( Text and Image)', 'Number of Colors', 'Trend Quote',
        'Recipient/Sender in the Message', 'Color', 'Message Content', 'Style Design',
        'Tone Design', 'Motif Design', '7 Day Conversion Rate'
    ]].dropna()
    
    # Chuyển cột Conversion Rate sang dạng số và loại bỏ hàng lỗi
    df['7 Day Conversion Rate'] = pd.to_numeric(df['7 Day Conversion Rate'], errors='coerce')
    df.dropna(subset=['7 Day Conversion Rate'], inplace=True)
    
    return df

# ------------------------
# 2. Giao diện Streamlit
# ------------------------
st.title("📊 Tổng hợp tổ hợp thiết kế theo ASIN và CR")

# Tải dữ liệu
df = load_data()

# ---------------------------------------
# 3. Chọn Niche và Product Type phù hợp
# ---------------------------------------
selected_niche = st.selectbox("🔍 Chọn Niche", sorted(df['Niche'].unique()))

# Lọc danh sách Product Type theo Niche đã chọn
filtered_product_types = df[df['Niche'] == selected_niche]['Product Type'].unique()
selected_product_type = st.selectbox("📦 Chọn Product Type", sorted(filtered_product_types))

# Lọc dữ liệu theo lựa chọn
filtered_df = df[(df['Niche'] == selected_niche) & (df['Product Type'] == selected_product_type)]

# ------------------------------------------
# 4. Hiển thị bảng tổng hợp theo thiết kế
# ------------------------------------------
if filtered_df.empty:
    st.warning("⚠️ Không có dữ liệu cho tổ hợp Niche và Product Type này.")
else:
    # Các yếu tố thiết kế để nhóm dữ liệu
    group_cols = [
        'Layout ( Text and Image)', 'Number of Colors', 'Trend Quote',
        'Recipient/Sender in the Message', 'Color', 'Message Content',
        'Style Design', 'Tone Design', 'Motif Design'
    ]

    # Tính toán:
    # - CR trung bình (Avg_CR)
    # - Số lượng ASIN có tổ hợp thiết kế đó (Count)
    # - Danh sách ASIN tương ứng (ASINs)
    summary_df = (
        filtered_df
        .groupby(group_cols)
        .agg(
            Avg_CR=('7 Day Conversion Rate', 'mean'),
            Count=('ASIN', 'count'),
            ASINs=('ASIN', lambda x: ', '.join(sorted(set(x))))
        )
        .reset_index()
        .sort_values(by='Avg_CR', ascending=False)
    )

    # Hiển thị kết quả
    st.subheader("📈 Bảng tổng hợp tổ hợp thiết kế theo ASIN")
    st.dataframe(summary_df, use_container_width=True)
