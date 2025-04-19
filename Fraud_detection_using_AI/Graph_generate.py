import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from io import BytesIO

# Generate Synthetic Fraud Data
np.random.seed(42)
num_samples = 150

df = pd.DataFrame({
    "Transaction ID": np.arange(1, num_samples + 1),
    "Amount": np.random.randint(100, 100000, num_samples),
    "Fraud Probability": np.random.uniform(0, 1, num_samples)
})

# Categorization Functions
def risk_category(prob):
    if prob < 0.25: return "Low Risk"
    elif prob < 0.50: return "Moderate Risk"
    elif prob < 0.75: return "High Risk"
    else: return "Ultra High Risk"

df["Risk Level"] = df["Fraud Probability"].apply(risk_category)

def fraud_probability_category(prob):
    if prob < 0.25: return "Likely Legit"
    elif prob < 0.50: return "Needs Review"
    elif prob < 0.75: return "Potentially Fraudulent"
    else: return "Immediate Attention"

df["Fraud Probability Category"] = df["Fraud Probability"].apply(fraud_probability_category)
df["Fraud Outcome"] = df["Fraud Probability"].apply(lambda x: "Fraud" if x > 0.5 else "Legit")
fraud_types = ["CF (Card Fraud)", "PF (Phishing Fraud)", "IF (Identity Fraud)", "TF (Transaction Fraud)"]
df["Fraud Type"] = np.random.choice(fraud_types, num_samples)
df["Risk + Fraud Type"] = df["Risk Level"] + " + " + df["Fraud Type"]

def user_behavior(prob):
    if prob < 0.25: return "Normal Behavior"
    elif prob < 0.75: return "Suspicious Behavior"
    else: return "Confirmed Fraud"

df["User Behavior"] = df["Fraud Probability"].apply(user_behavior)

def financial_impact(amount):
    if amount <= 5000: return "Small Transaction (<= Rs.5,000)"
    elif amount <= 50000: return "Medium Transaction (Rs.5,001 - Rs.50,000)"
    else: return "High-Value Transaction (> Rs.50,000)"

df["Financial Impact"] = df["Amount"].apply(financial_impact)
fraud_attempts = ["First-time Fraud", "Repeat Offender", "Multiple Fraud Attempts"]
df["Fraud Frequency"] = np.random.choice(fraud_attempts, num_samples)

# Generate Modern Styled Graphs
sns.set_style("darkgrid")

# Generate PDF Report
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)

# Title Page
pdf.add_page()
pdf.set_font("Arial", "B", 16)
pdf.cell(200, 10, "Fraud Analysis Report", ln=True, align="C")

# Function to add graph to PDF directly (no extra_info parameter)
def add_graph_to_pdf(fig, title, description):
    img_buffer = BytesIO()
    fig.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)
    plt.close(fig)

    pdf.add_page()
    pdf.image(img_buffer, x=10, y=20, w=160)  # Kept w=160 to ensure no overlap
    pdf.set_font("Arial", size=10)
    pdf.set_xy(10, 200)  # Description starts at y=200
    pdf.multi_cell(0, 5, description)
    print(f"Added to PDF: {title}")

# Descriptions without "extra" lines
descriptions = {
    "Risk Level Distribution": """1. Risk Level Distribution
This bar chart represents the Risk Level Distribution across transactions based on their fraud probability.

Categories & Meaning:
  - Low Risk (0 - 0.25) -> Transactions with minimal fraud probability.
  - Moderate Risk (0.26 - 0.50) -> Might need further review.
  - High Risk (0.51 - 0.75) -> Significant chance of fraud.
  - Ultra High Risk (0.76 - 1.00) -> Requires urgent attention.

Insights:
- A higher number of low-risk transactions suggests that most are legitimate.
- The distribution of high-risk and ultra-high-risk transactions helps prioritize fraud investigations.
- A balanced risk level distribution suggests the fraud detection system is working well.""",

    "Fraud Probability Distribution": """2. Fraud Probability Distribution
This histogram represents the Fraud Probability Distribution of transactions. Here's what it signifies:

X-Axis (Fraud Probability): Ranges from 0 to 1, where:
  - 0.0 - 0.25 -> Low probability of fraud (Likely Legit).
  - 0.26 - 0.50 -> Medium probability (Needs Review).
  - 0.51 - 0.75 -> High probability (Potentially Fraudulent).
  - 0.76 - 1.00 -> Very high probability (Immediate Attention).
Y-Axis (Count): The number of transactions falling into each fraud probability range.
KDE Curve (Smooth Line): Represents the density estimate, showing where most transactions are concentrated.""",

    "Fraud Outcome": """3. Fraud Outcome 
This pie chart displays the distribution of fraud outcomes.

Categories & Meaning:
  - Legit (<= 0.5 Fraud Probability) -> Transactions deemed non-fraudulent.
  - Fraud (> 0.5 Fraud Probability) -> Transactions flagged as fraudulent.

Insights:
- If fraudulent transactions make up a large percentage, this may indicate widespread fraud attempts.
- A lower fraud percentage suggests effective fraud prevention or fewer fraudulent attempts.""",

    "Fraud Type Distribution": """4. Fraud Type Distribution 
This bar chart shows the different types of fraud detected.

Fraud Categories:
  - CF (Card Fraud) -> Stolen credit/debit card use.
  - PF (Phishing Fraud) -> Fake emails or websites deceiving users.
  - IF (Identity Fraud) -> Unauthorized identity use.
  - TF (Transaction Fraud) -> Manipulated transaction details.

Insights:
- If a particular fraud type is dominant, security measures should focus on mitigating that risk.
- A diverse fraud type distribution suggests multiple attack vectors are in use.""",

    "User Behavior Anomalies": """5. User Behavior Anomalies 
This bar chart categorizes user behavior based on fraud probability.

Categories & Meaning:
  - Normal Behavior (<= 0.25) -> Typical transaction patterns.
  - Suspicious Behavior (0.26 - 0.75) -> May indicate fraudulent tendencies.
  - Confirmed Fraud (> 0.75) -> Strong fraud indicators.

Insights:
- A higher number of suspicious users suggests increased fraud risks.
- A lower number of confirmed fraud users indicates a low false positive rate.""",

    "Financial Impact Distribution": """6. Financial Impact Distribution 
This bar chart classifies transactions by monetary value.

Categories & Meaning:
  - Small Transaction (<= Rs.5,000) -> Low financial risk.
  - Medium Transaction (Rs.5,001 - Rs.50,000) -> Moderate risk.
  - High-Value Transaction (> Rs.50,000) -> High risk.

Insights:
- If most fraud occurs in high-value transactions, financial losses could be severe.
- A high number of small fraudulent transactions may indicate bot-driven fraud attempts.""",

    "Fraud Frequency": """7. Fraud Frequency 
This bar chart shows how often fraud occurs per user.

Categories & Meaning:
  - First-time Fraud -> Users flagged as fraudulent for the first time.
  - Repeat Offender -> Users with multiple past fraud attempts.
  - Multiple Fraud Attempts -> High-risk users committing fraud frequently.

Insights:
- A high percentage of repeat offenders suggests the need for stronger security policies.
- Many first-time frauds could indicate a rise in new fraudsters.""",

    "Top 10 Risk & Fraud Type Combinations": """8. Top 10 Risk & Fraud Type Combinations 
This bar chart displays the most frequent fraud-risk level pairings.

Example Categories:
  - Ultra High Risk + Card Fraud
  - High Risk + Identity Fraud
  - Moderate Risk + Phishing Fraud

Insights:
- The most common high-risk fraud types should be investigated first.
- If a particular fraud type dominates at ultra-high risk, then security measures must be tailored accordingly."""
}

# Generate and Add Graphs Directly to PDF
fig, ax = plt.subplots(figsize=(7,5))
sns.countplot(y=df["Risk Level"], palette="coolwarm", ax=ax)
plt.title("Risk Level Distribution")
add_graph_to_pdf(fig, "Risk Level Distribution", descriptions["Risk Level Distribution"])

fig, ax = plt.subplots(figsize=(7,5))
sns.histplot(df["Fraud Probability"], bins=20, kde=True, color='purple')
plt.title("Fraud Probability Distribution")
add_graph_to_pdf(fig, "Fraud Probability Distribution", descriptions["Fraud Probability Distribution"])

fig, ax = plt.subplots(figsize=(7,5))
df["Fraud Outcome"].value_counts().plot(kind="pie", autopct='%1.1f%%', colors=['green', 'red'])
plt.title("Fraud Outcome")
plt.ylabel("")
add_graph_to_pdf(fig, "Fraud Outcome", descriptions["Fraud Outcome"])

fig, ax = plt.subplots(figsize=(7,5))
sns.countplot(y=df["Fraud Type"], palette="viridis", ax=ax)
plt.title("Fraud Type Distribution")
add_graph_to_pdf(fig, "Fraud Type Distribution", descriptions["Fraud Type Distribution"])

fig, ax = plt.subplots(figsize=(7,5))
sns.countplot(y=df["User Behavior"], palette="plasma", ax=ax)
plt.title("User Behavior Anomalies")
add_graph_to_pdf(fig, "User Behavior Anomalies", descriptions["User Behavior Anomalies"])

fig, ax = plt.subplots(figsize=(7,5))
sns.countplot(y=df["Financial Impact"], palette="magma", ax=ax)
plt.title("Financial Impact Distribution")
add_graph_to_pdf(fig, "Financial Impact Distribution", descriptions["Financial Impact Distribution"])

fig, ax = plt.subplots(figsize=(7,5))
sns.countplot(y=df["Fraud Frequency"], palette="inferno", ax=ax)
plt.title("Fraud Frequency")
add_graph_to_pdf(fig, "Fraud Frequency", descriptions["Fraud Frequency"])

fig, ax = plt.subplots(figsize=(7,5))
df["Risk + Fraud Type"].value_counts().head(10).plot(kind="barh", color='blue', ax=ax)
plt.title("Top 10 Risk & Fraud Type Combinations")
add_graph_to_pdf(fig, "Top 10 Risk & Fraud Type Combinations", descriptions["Top 10 Risk & Fraud Type Combinations"])

# Save PDF
pdf.output("fraud_analysis_report.pdf")
print("✅ Fraud Analysis Report Generated Successfully!")