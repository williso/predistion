
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
        'Niche', 'Color', 'Message Content', 'Style Design',
        'Tone Design', 'Motif Design', 'Product Type', '7 Day Conversion Rate'
    ]].dropna()
    df['7 Day Conversion Rate'] = pd.to_numeric(df['7 Day Conversion Rate'], errors='coerce')
    df.dropna(subset=['7 Day Conversion Rate'], inplace=True)
    return df

# Train model and encoder
def train_model(df):
    X_cat = df.drop(columns='7 Day Conversion Rate')
    y = df['7 Day Conversion Rate']
    encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
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
model, encoder, input_cols = train_model(df)

with st.form("input_form"):
    user_input = {
        'Niche': st.selectbox("Niche", sorted(df['Niche'].unique())),
        'Color': st.selectbox("Color", sorted(df['Color'].unique())),
        'Message Content': st.selectbox("Message Content", sorted(df['Message Content'].unique())),
        'Style Design': st.selectbox("Style Design", sorted(df['Style Design'].unique())),
        'Tone Design': st.selectbox("Tone Design", sorted(df['Tone Design'].unique())),
        'Motif Design': st.selectbox("Motif Design", sorted(df['Motif Design'].unique())),
        'Product Type': st.selectbox("Product Type", sorted(df['Product Type'].unique())),
    }

    submitted = st.form_submit_button("Predict")

if submitted:
    result = predict_conversion(model, encoder, user_input)
    st.success(f"Predicted Conversion Rate: {result * 100:.2f}%")
