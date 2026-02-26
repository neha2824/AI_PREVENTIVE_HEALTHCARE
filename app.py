from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
import tensorflow as tf
import streamlit as st
import joblib
import numpy as np

# ================= LOAD MODELS =================
image_model = load_model(r"C:\Users\dheer\OneDrive\Desktop\AI_PREVENTIVE_HEALTHCARE\image_model.keras")
model = joblib.load("Data/best_model.pkl")
scaler = joblib.load("Data/scaler.pkl")

# ================= TITLE =================
st.title("AI Preventive Healthcare Risk Predictor")

st.markdown("""
### 🏥 AI-Driven Preventive Healthcare Intelligence Platform
• Structured health risk prediction (ML)  
• Chest X-ray classification (Deep Learning)  

⚠ Preventive decision-support system — not medical diagnosis
""")

# ================= HEALTH INPUT =================
st.write("Enter patient health details below:")

age = st.number_input("Age", 20, 100)
bmi = st.number_input("BMI", 10.0, 50.0)
bp = st.number_input("Blood Pressure", 80.0, 200.0)
glucose = st.number_input("Glucose Level", 50.0, 300.0)
hemoglobin = st.number_input("Hemoglobin", 5.0, 20.0)
cholesterol = st.number_input("Cholesterol", 100.0, 400.0)

# ================= RISK PREDICTION =================
if st.button("Predict Risk"):

    input_data = np.array([[age, bmi, bp, glucose, hemoglobin, cholesterol]])
    input_scaled = scaler.transform(input_data)

    prediction = model.predict(input_scaled)
    probability = model.predict_proba(input_scaled)[0][1]

    # ----- Hybrid Risk Adjustment -----
    risk_score = probability

    if bmi < 25 and bp < 120 and glucose < 110 and cholesterol < 200 and hemoglobin >= 12:
        risk_score = risk_score * 0.3

    st.write(f"Adjusted Risk Probability: {risk_score*100:.2f}%")

    if risk_score > 0.75:
        st.warning("🔴 Risk Level: HIGH")
    elif risk_score > 0.40:
        st.info("🟠 Risk Level: MODERATE")
    else:
        st.success("🟢 Risk Level: LOW")

# ================= IMAGE SECTION =================
st.markdown("## Chest X-Ray Image Classification")

uploaded_file = st.file_uploader(
    "Upload Chest X-Ray Image",
    type=["jpg", "png", "jpeg"]
)

if uploaded_file is not None:

    img = Image.open(uploaded_file).convert("RGB")
    st.image(img, caption="Uploaded Image", use_column_width=True)

    # Preprocess
    img = img.resize((224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = tf.expand_dims(img_array, 0)

    # Predict
    prediction_img = image_model.predict(img_array)[0][0]

    st.write(f"Model Output Score: {prediction_img:.3f}")

    # ----- Final Decision -----
    if prediction_img < 0.5:
        st.error("⚠ Abnormal (Pneumonia Detected)")
    else:
        st.success("✅ Normal Chest X-Ray")

# ================= FOOTER =================
st.markdown("---")
st.caption("Developed as Final Year Engineering Project | AI in Healthcare Domain")
