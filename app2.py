import streamlit as st
import numpy as np
import joblib
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import PyPDF2
import pytesseract
import re
from datetime import datetime

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="AI Healthcare Platform 2.0",
    page_icon="🏥",
    layout="wide"
)
# ================= CUSTOM CSS =================
st.markdown("""
<style>

/* Fix faded number input text in LIGHT theme */
div[data-testid="stNumberInput"] input {
    color: #000000 !important;              /* pure black */
    -webkit-text-fill-color: #000000 !important;
    opacity: 1 !important;
    font-weight: 600 !important;
}

/* Also fix label color */
div[data-testid="stNumberInput"] label {
    color: #000000 !important;
}

</style>
""", unsafe_allow_html=True)
# ================= TESSERACT PATH =================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ================= LOAD MODELS =================
@st.cache_resource
def load_models():
    image_model = load_model("image_model.keras")
    ml_model = joblib.load("Data/best_model.pkl")
    scaler = joblib.load("Data/scaler.pkl")
    return image_model, ml_model, scaler

image_model, ml_model, scaler = load_models()

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "history_data" not in st.session_state:
    st.session_state.history_data = []

# ================= LOGIN =================
if not st.session_state.logged_in:

    st.title("🔐 Login to AI Healthcare Platform")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username.strip().lower() == "admin" and password.strip() == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")

# ================= MAIN APP =================
else:

    st.title("🏥 AI-Driven Preventive Healthcare Platform 2.0")
    st.markdown("---")

    menu = st.sidebar.selectbox(
        "Navigation",
        ["🏠 Home", "🩺 Risk Prediction", "🫁 X-ray AI", "📄 Report Analyzer", "📜 History"]
    )

    # ================= HOME =================
    if menu == "🏠 Home":
        st.success("Welcome to AI Preventive Healthcare System")

        # ================= RISK PREDICTION =================
    elif menu == "🩺 Risk Prediction":

        left, right = st.columns(2)

        with left:
            st.subheader("👤 Patient Information")
            name = st.text_input("Patient Name")

            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Age (years)", 1, 120)
            with col2:
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])

            smoker = st.toggle("Current Smoker")

            st.divider()
            st.subheader("❤️ Vitals")

            col3, col4 = st.columns(2)
            with col3:
                bmi = st.number_input("BMI (kg/m²)", 10.0, 50.0)
            with col4:
                bp = st.number_input("Blood Pressure (mmHg)", 80.0, 200.0)

            st.divider()
            st.subheader("🧪 Lab Results")

            col5, col6 = st.columns(2)
            with col5:
                glucose = st.number_input("Glucose (mg/dL)", 50.0, 300.0)
            with col6:
                hemoglobin = st.number_input("Hemoglobin (g/dL)", 5.0, 20.0)

            cholesterol = st.number_input("Cholesterol (mg/dL)", 100.0, 400.0)

        with right:
            st.subheader("📊 Risk Assessment")

            col_btn1, col_btn2 = st.columns(2)
            calculate = col_btn1.button("Calculate Risk", use_container_width=True)
            reset = col_btn2.button("Reset", use_container_width=True)

            if calculate:
                data = np.array([[age, bmi, bp, glucose, hemoglobin, cholesterol]])
                data_scaled = scaler.transform(data)
                prob = ml_model.predict_proba(data_scaled)[0][1]
                st.session_state.current_prob = prob

            if "current_prob" in st.session_state:
                prob = st.session_state.current_prob
                st.metric("Risk Probability", f"{prob*100:.2f}%")

                precautions = []

                if prob > 0.75:
                    st.error("High Health Risk")
                    precautions += [
                        "Immediate physician consultation",
                        "Strict diet control",
                        "Daily 45 min walking",
                        "Reduce sugar and salt intake",
                        "Regular BP & Glucose monitoring"
                    ]

                elif prob > 0.4:
                    st.warning("Moderate Risk")
                    precautions += [
                        "Balanced diet",
                        "Exercise daily",
                        "Monthly health checkup"
                    ]

                else:
                    st.success("Low Risk")
                    precautions += [
                        "Maintain healthy lifestyle",
                        "Annual health check"
                    ]

                st.markdown("### Recommended Precautions")

                st.markdown(f"""
<div style='background-color:#e6f4ea;
padding:15px;
border-radius:10px;
color:#0f5132;
font-weight:600'>
<ul>
{''.join([f"<li>{p}</li>" for p in precautions])}
</ul>
</div>
""", unsafe_allow_html=True)

                if st.button("💾 Save Record", use_container_width=True):
                    record = {
                        "name": name,
                        "gender": gender,
                        "age": age,
                        "date": datetime.now().strftime("%d/%m/%Y %I:%M:%S %p"),
                        "risk": "High Risk" if prob > 0.75 else "Moderate Risk" if prob > 0.4 else "Low Risk",
                        "score": round(prob*100, 2),
                        "bmi": bmi,
                        "bp": f"{bp} mmHg",
                        "glucose": f"{glucose} mg/dL",
                        "hgb": f"{hemoglobin} g/dL",
                        "chol": f"{cholesterol} mg/dL",
                        "smoker": "Yes" if smoker else "No"
                    }

                    st.session_state.history_data.insert(0, record)
                    st.success("Record Saved Successfully ✅")

            if reset:
                st.session_state.pop("current_prob", None)
                st.rerun()


    # ================= X-RAY AI =================
    elif menu == "🫁 X-ray AI":

        st.markdown("## X-Ray Analysis")
        st.warning("Medical Disclaimer: Simulated results only.")

        left, right = st.columns(2)

        with left:
            file = st.file_uploader("Upload X-ray", type=["jpg", "png", "jpeg"])
            analyze_btn = st.button("Analyze X-Ray", use_container_width=True)

        with right:
            if file and analyze_btn:
                img = Image.open(file).convert("RGB")
                st.image(img, caption="Uploaded X-ray")

                img = img.resize((224, 224))
                img_array = image.img_to_array(img) / 255.0
                img_array = np.expand_dims(img_array, axis=0)

                prediction = image_model.predict(img_array)

                if prediction.shape[-1] == 1:
                    pneumonia_prob = float(prediction[0][0])
                    class_index = 1 if pneumonia_prob > 0.5 else 0
                else:
                    class_index = np.argmax(prediction)
                    pneumonia_prob = float(prediction[0][class_index])

                st.metric("Pneumonia Probability", f"{pneumonia_prob*100:.2f}%")

                if class_index == 1:
                    st.error("⚠ Pneumonia Detected")
                else:
                    st.success("✅ Chest Appears Normal")
            else:
                st.info("Upload and analyze an X-ray to see results.")
    # ================= REPORT ANALYZER =================
    elif menu == "📄 Report Analyzer":

        st.header("AI Medical Report Analyzer")

        uploaded_file = st.file_uploader("Upload Report", type=["pdf", "jpg", "png"])

        if uploaded_file:

            text = ""

            if uploaded_file.type == "application/pdf":
                pdf = PyPDF2.PdfReader(uploaded_file)
                for page in pdf.pages:
                    text += page.extract_text() or ""
            else:
                img = Image.open(uploaded_file)
                text = pytesseract.image_to_string(img)

            st.subheader("Extracted Report")
            st.text_area("", text, height=200)

            text_lower = text.lower()

            diseases = []
            recommendations = []
            readings = []

            st.markdown("---")
            st.subheader("Detected Readings")

            g = re.search(r'(glucose|fbs|fasting)[^\d]*(\d+)', text_lower)
            if g:
                val = int(g.group(2))
                readings.append(f"Glucose: {val} mg/dL")
                if val >= 126:
                    diseases.append("Diabetes")
                    recommendations += ["Reduce sugar intake", "Consult Endocrinologist"]

            c = re.search(r'cholesterol[^\d]*(\d+)', text_lower)
            if c:
                val = int(c.group(1))
                readings.append(f"Cholesterol: {val} mg/dL")
                if val > 240:
                    diseases.append("High Cholesterol")
                    recommendations += ["Avoid fried foods", "Cardio exercise"]

            h = re.search(r'hemoglobin[^\d]*(\d+)', text_lower)
            if h:
                val = int(h.group(1))
                readings.append(f"Hemoglobin: {val} g/dL")
                if val < 12:
                    diseases.append("Anemia")
                    recommendations += ["Iron rich diet"]

            bp = re.search(r'(\d{2,3})\s*/\s*(\d{2,3})', text_lower)
            if bp:
                sys = int(bp.group(1))
                dia = int(bp.group(2))
                readings.append(f"Blood Pressure: {sys}/{dia}")
                if sys > 140 or dia > 90:
                    diseases.append("Hypertension")
                    recommendations += ["Reduce salt intake"]

            if readings:
                st.markdown(f"""
<div style='background-color:#fff3cd;
padding:15px;
border-radius:10px;
color:#664d03;
font-weight:700'>
{''.join([f"• {r}<br>" for r in readings])}
</div>
""", unsafe_allow_html=True)

            st.markdown("---")
            st.subheader("Final Health Summary")

            if diseases:
                st.markdown(f"""
<div style='background-color:#f8d7da;
padding:15px;
border-radius:10px;
color:#842029;
font-weight:700'>
<b>Detected Conditions:</b><br>
{''.join([f"• {d}<br>" for d in set(diseases)])}
</div>
""", unsafe_allow_html=True)
            else:
                st.markdown("""
<div style='background-color:#d1e7dd;
padding:15px;
border-radius:10px;
color:#0f5132;
font-weight:700'>
No major disease detected
</div>
""", unsafe_allow_html=True)

            st.markdown("### Recommended Actions")

            st.markdown(f"""
<div style='background-color:#e6f4ea;
padding:15px;
border-radius:10px;
color:#0f5132;
font-weight:700'>
<ul>
{''.join([f"<li>{r}</li>" for r in set(recommendations)]) if recommendations else "<li>Maintain healthy lifestyle</li>"}
</ul>
</div>
""", unsafe_allow_html=True)


    # ================= HISTORY =================
    elif menu == "📜 History":

        st.markdown("## Prediction History")
        st.write("All past risk assessments, most recent first.")

        if not st.session_state.history_data:
            st.markdown("""
<div style="background:#1f2937;padding:30px;border-radius:15px;margin-top:20px;
border-left:6px solid #f59e0b;color:#e5e7eb;text-align:center;">
No records saved yet.
</div>
""", unsafe_allow_html=True)

        else:
            for record in st.session_state.history_data:
                st.markdown(f"""
<div style="background:#1f2937;padding:25px;border-radius:15px;margin-bottom:25px;
border-left:6px solid #f59e0b;color:#e5e7eb;">

<strong>{record['name']} — {record['gender']}, {record['age']} years old</strong><br>
<small style="color:#9ca3af;">{record['date']}</small><br><br>

Risk: {record['risk']} (Score: {record['score']})<br><br>

BMI: {record['bmi']} |
BP: {record['bp']} |
Glucose: {record['glucose']} |
Hgb: {record['hgb']} |
Chol: {record['chol']} |
Smoker: {record['smoker']}

</div>
""", unsafe_allow_html=True)

            st.caption(f"📈 {len(st.session_state.history_data)} records total")