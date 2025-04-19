import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from fpdf import FPDF
import numpy as np
import os

# Load Dataset
def load_data(csv_file):
    if not os.path.exists(csv_file):
        print(f"Error: The file '{csv_file}' was not found.")
        exit(1)
    df = pd.read_csv(csv_file)
    return df

# Preprocess Data
def preprocess_data(df):
    label_encoder = LabelEncoder()
    categorical_cols = ['location', 'device', 'payment_type', 'beneficiary']

    for col in categorical_cols:
        if col in df.columns:
            df[col] = label_encoder.fit_transform(df[col])

    if 'change_in_personal_info' in df.columns:
        df['change_in_personal_info'] = df['change_in_personal_info'].astype(int)

    if 'time' in df.columns:
        try:
            df['time'] = pd.to_datetime(df['time'], errors='coerce').dt.hour.fillna(0).astype(int)
        except Exception as e:
            print(f"Error processing time column: {e}")

    if 'ip_address' in df.columns:
        df['ip_address'] = df['ip_address'].astype(str).apply(
            lambda x: sum([int(i) for i in x.split('.') if i.isdigit()])
        )

    if 'fraudulent' not in df.columns:
        df['fraudulent'] = np.random.randint(0, 2, size=len(df))

    return df

# Classify Fraud Type with Abbreviations
def classify_fraud(row):
    fraud_types = []

    if row['amount'] > 2000 and row['multi_login_attempts'] > 1:
        fraud_types.append("TF")  # Transaction Fraud
    if row['amount'] > 10000 or row['multi_login_attempts'] > 2:
        fraud_types.append("CF")  # Credit Card Fraud
    if row['beneficiary'] > 0 and row['amount'] > 5000:
        fraud_types.append("PF")  # Phishing-Based Transactions Fraud
    if row['multi_login_attempts'] > 3 or row['change_in_personal_info'] == 1:
        fraud_types.append("IF")  # Identity Theft

    return ", ".join(fraud_types) if fraud_types else "Low Risk"

# Train Machine Learning Model
def train_model(df):
    features = ['amount', 'location', 'multi_login_attempts', 'time', 'ip_address', 
                'device', 'change_in_personal_info', 'payment_type', 'beneficiary']

    missing_features = [col for col in features if col not in df.columns]
    if missing_features:
        print(f"Error: Missing required columns: {missing_features}")
        exit(1)

    X = df[features]
    y = df['fraudulent']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))

    return model

# Generate PDF Report
def generate_pdf_report(df, model, pdf_file):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Fraud Risk Evaluation Report", ln=True, align='C')
    pdf.ln(10)

    # Add fraud type legend on the first page
    pdf.set_font("Arial", style='B', size=10)
    pdf.cell(200, 10, txt="Fraud Type short forms we have used :", ln=True, align='L')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="- CF: Credit Card Fraud", ln=True, align='L')
    pdf.cell(200, 10, txt="- PF: Phishing-Based Transactions Fraud", ln=True, align='L')
    pdf.cell(200, 10, txt="- IF: Identity Theft", ln=True, align='L')
    pdf.cell(200, 10, txt="- TF: Transaction Fraud", ln=True, align='L')
    pdf.ln(10)

    df['Fraud Type'] = df.apply(classify_fraud, axis=1)

    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="| User ID | Probability | Prediction | Fraud Type | Risk Level |", ln=True, align='C')
    pdf.ln(5)
    pdf.cell(200, 10, txt="-----------------------------------------------------------------", ln=True, align='C')

    for index, row in df.iterrows():
        features = [[row.get('amount', 0), row.get('location', 0), row.get('multi_login_attempts', 0),
                     row.get('time', 0), row.get('ip_address', 0), row.get('device', 0),
                     row.get('change_in_personal_info', 0), row.get('payment_type', 0),
                     row.get('beneficiary', 0)]]

        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0][1] * 100
        fraud_type = row['Fraud Type']
        risk_level = "Low Risk"
        if 50 <= probability <= 62:
            risk_level = "Moderate Risk"
        elif 62 < probability <= 75:
            risk_level = "High Risk"
        elif probability > 75:
            risk_level = "Ultra High Risk"

        pdf.cell(40, 10, txt=f"{row.get('userid', 'N/A')}", border=1, align='C')
        pdf.cell(40, 10, txt=f"{probability:.2f}%", border=1, align='C')
        pdf.cell(40, 10, txt=f"{'Fraud' if prediction == 1 else 'Legit'}", border=1, align='C')
        pdf.cell(40, 10, txt=fraud_type, border=1, align='C')
        pdf.cell(40, 10, txt=risk_level, border=1, align='C')
        pdf.ln()

    pdf.output(pdf_file)
    print(f"PDF Report Generated: {pdf_file}")

# Main Execution
def main():
    csv_file = 'dataset.csv'
    pdf_file = 'Fraud_Risk_Report.pdf'

    df = load_data(csv_file)
    df = preprocess_data(df)
    model = train_model(df)
    generate_pdf_report(df, model, pdf_file)

if _name_ == "_main_":
    main()