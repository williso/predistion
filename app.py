import streamlit as st
import pandas as pd

# -------------------------
# 1. Load và xử lý dữ liệu
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Merged_ASIN_Data.csv", encoding='Windows-1252')
    
    # Đổi tên cột để thống nhất
    df.rename(columns={'Conversion Rate (%)': '7 Day Conversion Rate'}, inplace=True)
    
    # Chọn các cột cần thiết
    df = df[[
        'ASIN', 'Niche', 'Product Type', 'Layout ( Text and Image)', 'Number of Colors', 'Trend Quote',
        'Recipient/Sender in the Message', 'Color', 'Message Content', 'Style Design',
        'Tone Design', 'Motif Design', '7 Day Conversion Rate', 'Image_URL'
    ]].dropna(subset=['ASIN', 'Image_URL'])

    # Xử lý kiểu dữ liệu
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
# 5. Chia ASIN theo nhóm CR và hiển thị ảnh
# ------------------------------------------
with st.expander("📌 Xem phân loại hình ảnh ASIN theo nhóm CR trong tổ hợp đã chọn"):
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

    # --------------------------
    # Hàm hiển thị hình ảnh lưới
    # --------------------------
    def show_images_by_group(df, group_label, color_emoji, images_per_row=4):
        st.markdown(f"#### {color_emoji} Nhóm {group_label}")
        group_df = df[df['CR Group'] == group_label].drop_duplicates(subset='ASIN')

        image_urls = group_df['Image_URL'].tolist()
        asins = group_df['ASIN'].tolist()

        for i in range(0, len(image_urls), images_per_row):
            cols = st.columns(images_per_row)
            for j, col in enumerate(cols):
                if i + j < len(image_urls):
                    with col:
                        st.image(image_urls[i + j], width=150)
                        st.caption(asins[i + j])  # Hiển thị ASIN dưới ảnh

    # Hiển thị từng nhóm
    show_images_by_group(asin_df, 'Top', '🟢')
    show_images_by_group(asin_df, 'Trung bình', '🟡')
    show_images_by_group(asin_df, 'Dưới trung bình', '🔴')
