import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder

# Load and preprocess data
@st.cache_data
def load_data():
    df = pd.read_csv("Merged_ASIN_Data.csv")
    df = df[[
        'Niche', 'Product Type', 'Color', 'Message Content', 'Style Design',
        'Tone Design', 'Motif Design', '7 Day Conversion Rate'
    ]].dropna()
    df['7 Day Conversion Rate'] = pd.to_numeric(df['7 Day Conversion Rate'], errors='coerce')
    df.dropna(subset=['7 Day Conversion Rate'], inplace=True)
    return df

# Train model and encoder for a specific niche and product type
def train_model(df, selected_niche, selected_product_type):
    df_filtered = df[(df['Niche'] == selected_niche) & (df['Product Type'] == selected_product_type)]
    if df_filtered.empty:
        return None, None, None

    X_cat = df_filtered.drop(columns='7 Day Conversion Rate')
    y = df_filtered['7 Day Conversion Rate']

    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    X_encoded = encoder.fit_transform(X_cat)
    model = RandomForestRegressor(random_state=42)
    model.fit(X_encoded, y)
    return model, encoder, X_cat.columns.tolist()

# Predict conversion rate
def predict_conversion(model, encoder, user_input):
    df_input = pd.DataFrame([user_input])
    encoded_input = encoder.transform(df_input)
    prediction = model.predict(encoded_input)
    return round(prediction[0], 4)

# Streamlit app
st.title("🎨 Conversion Rate Predictor for Design Combinations")

df = load_data()

with st.form("input_form"):
    selected_niche = st.selectbox("Niche", sorted(df['Niche'].unique()))
    filtered_product_types = df[df['Niche'] == selected_niche]['Product Type'].unique()
    selected_product_type = st.selectbox("Product Type", sorted(filtered_product_types))

    design_df = df[(df['Niche'] == selected_niche) & (df['Product Type'] == selected_product_type)]

    user_input = {
        'Niche': selected_niche,
        'Product Type': selected_product_type,
        'Color': st.selectbox("Color", sorted(design_df['Color'].unique())),
        'Message Content': st.selectbox("Message Content", sorted(design_df['Message Content'].unique())),
        'Style Design': st.selectbox("Style Design", sorted(design_df['Style Design'].unique())),
        'Tone Design': st.selectbox("Tone Design", sorted(design_df['Tone Design'].unique())),
        'Motif Design': st.selectbox("Motif Design", sorted(design_df['Motif Design'].unique())),
    }

    submitted = st.form_submit_button("Predict")

if submitted:
    model, encoder, input_cols = train_model(df, selected_niche, selected_product_type)
    if model is None:
        st.error("Không đủ dữ liệu cho tổ hợp Niche và Product Type này.")
    else:
        result = predict_conversion(model, encoder, user_input)
        st.success(f"Predicted Conversion Rate: {result * 100:.2f}%")
