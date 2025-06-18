import streamlit as st
import pandas as pd

# -------------------------
# 1. Load và xử lý dữ liệu
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Merged_ASIN_Data.csv", encoding='Windows-1252')
    df.rename(columns={'Conversion Rate (%)': '7 Day Conversion Rate'}, inplace=True)

    df = df[[
        'ASIN', 'Niche', 'Product Type', 'Layout ( Text and Image)', 'Number of Colors', 'Trend Quote',
        'Recipient/Sender in the Message', 'Color', 'Message Content', 'Style Design',
        'Tone Design', 'Motif Design', '7 Day Conversion Rate', 'Image_URL'
    ]].dropna(subset=['ASIN', 'Image_URL'])

    df['7 Day Conversion Rate'] = pd.to_numeric(df['7 Day Conversion Rate'], errors='coerce')
    df.dropna(subset=['7 Day Conversion Rate'], inplace=True)

    return df

# ------------------------
# 2. Giao diện Streamlit
# ------------------------
st.title("📊 Tổng hợp tổ hợp thiết kế theo ASIN và CR")
st.caption("Lọc theo Niche bắt buộc — Product Type có thể bỏ trống để hiển thị tất cả")

df = load_data()

# ---------------------------------------
# 3. Chọn Niche và Product Type (optional)
# ---------------------------------------
selected_niche = st.selectbox("🔍 Chọn Niche", sorted(df['Niche'].unique()))

# Danh sách Product Type theo Niche
filtered_product_types = df[df['Niche'] == selected_niche]['Product Type'].dropna().unique()
product_type_options = ["-- Tất cả --"] + sorted(filtered_product_types.tolist())
selected_product_type = st.selectbox("📦 Chọn Product Type (tuỳ chọn)", product_type_options)

# Lọc theo lựa chọn
if selected_product_type == "-- Tất cả --":
    filtered_df = df[df['Niche'] == selected_niche]
else:
    filtered_df = df[(df['Niche'] == selected_niche) & (df['Product Type'] == selected_product_type)]

# ------------------------------------------

# 4. Hiển thị tổ hợp thiết kế có highlight
# ------------------------------------------

# Tính trung bình toàn bộ tổ hợp
avg_of_all = summary_df['Avg_CR'].mean()

# Hàm để tô đậm dòng có Avg_CR > trung bình
def highlight_full_row(row):
    if row['Avg_CR'] > avg_of_all:
        return ['color: #bbdebf; font-weight: bold' for _ in row]
    else:
        return ['' for _ in row]

# Áp dụng style
styled_df = summary_df.style.apply(highlight_full_row, axis=1)

# Hiển thị bảng có styling
st.subheader("📈 Tổng hợp tất cả tổ hợp thiết kế")
st.dataframe(styled_df, use_container_width=True, hide_index=True)
# ------------------------------------------
# 5. Phân loại CR và hiển thị ảnh theo nhóm
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

    # Tính CR trung bình trong tổ hợp
    mean_cr = asin_df['7 Day Conversion Rate'].mean()

    # Gán nhãn nhóm CR
    def categorize_cr(cr, mean):
        if cr > mean:
            return 'Trên trung bình'
        elif cr < mean:
            return 'Dưới trung bình'
        else:
            return 'Trung bình'

    asin_df['CR Group'] = asin_df['7 Day Conversion Rate'].apply(lambda x: categorize_cr(x, mean_cr))

    # --------------------------
    # Hiển thị ảnh theo nhóm CR
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
                        st.caption(asins[i + j])

    show_images_by_group(asin_df, 'Trên trung bình', '🟢')
    show_images_by_group(asin_df, 'Trung bình', '🟡')
    show_images_by_group(asin_df, 'Dưới trung bình', '🔴')
