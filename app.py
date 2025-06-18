@st.cache_data
def load_data():
    df = pd.read_csv("Merged_ASIN_Data.csv")

    # Chỉ chọn các cột cần thiết
    df = df[[
        'ASIN', 'Niche', 'Product Type', 'Layout ( Text and Image)', 'Number of Colors', 'Trend Quote',
        'Recipient/Sender in the Message', 'Color', 'Message Content', 'Style Design',
        'Tone Design', 'Motif Design', '7 Day Conversion Rate'
    ]]

    # Chuyển đổi CR sang số, loại bỏ các dòng không thể chuyển được
    df['7 Day Conversion Rate'] = pd.to_numeric(df['7 Day Conversion Rate'], errors='coerce')
    df.dropna(subset=['7 Day Conversion Rate'], inplace=True)

    # Các cột tổ hợp thiết kế — điền "Unknown" nếu thiếu
    group_cols = [
        'Layout ( Text and Image)', 'Number of Colors', 'Trend Quote',
        'Recipient/Sender in the Message', 'Color', 'Message Content',
        'Style Design', 'Tone Design', 'Motif Design'
    ]
    df[group_cols] = df[group_cols].fillna("Unknown")

    return df
