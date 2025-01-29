import pandas as pd
import streamlit as st
import openai
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Title and Instructions
st.title("AI Agent for Invoice Management")
st.write("Upload a dataset of invoices, and the AI agent will help with recommendations, anomaly detection, and reporting.")

# Sidebar API key input
api_key = st.sidebar.text_input("Enter your OpenAI API key", type="password")
if not api_key:
    st.warning("Please enter your OpenAI API key in the sidebar.")
    st.stop()

openai.api_key = api_key

# Sample invoice data generation
def generate_sample_data():
    data = {
        "Invoice Number": ["INV-001", "INV-002", "INV-003", "INV-004", "INV-005"],
        "Supplier Name": ["Supplier A", "Supplier B", "Supplier C", "Supplier D", "Supplier E"],
        "Invoice Amount": [5000, 12000, 7000, 3000, 9500],
        "Due Date": [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in [5, 15, 25, 10, 20]],
        "Payment Terms": ["2/10 Net 30", "Net 15", "Net 30", "2/10 Net 30", "Net 45"]
    }
    return pd.DataFrame(data)

# Show sample dataset if user requests
if st.button("Generate Sample Invoice Data"):
    sample_data = generate_sample_data()
    st.dataframe(sample_data)
    sample_data.to_csv("sample_invoices.csv", index=False)

# Upload invoice dataset
uploaded_file = st.file_uploader("Upload your CSV file with invoice data", type="csv")

if uploaded_file:
    invoices = pd.read_csv(uploaded_file)
    st.dataframe(invoices)

    # Process and analyze invoice data
    def generate_recommendations(df):
        recommendations = []

        for _, row in df.iterrows():
            due_date = datetime.strptime(row["Due Date"], '%Y-%m-%d')
            days_remaining = (due_date - datetime.now()).days
            payment_terms = row["Payment Terms"]

            # Proactive recommendation logic
            if "2/10 Net 30" in payment_terms and days_remaining <= 10:
                recommendations.append(f"Consider paying {row['Invoice Number']} (Supplier: {row['Supplier Name']}) early for a 2% discount.")
            elif days_remaining <= 5:
                recommendations.append(f"Urgent: {row['Invoice Number']} (Supplier: {row['Supplier Name']}) is due in {days_remaining} days.")
            else:
                recommendations.append(f"No urgent action required for {row['Invoice Number']}.")

        return recommendations

    def detect_anomalies(df):
        anomalies = []
        for _, row in df.iterrows():
            if row["Invoice Amount"] > 10000:  # Example threshold for large invoices
                anomalies.append(f"Anomaly detected: {row['Invoice Number']} (Amount: {row['Invoice Amount']}) exceeds typical limits.")
            if not row["Payment Terms"]:
                anomalies.append(f"Missing payment terms for {row['Invoice Number']}.")

        return anomalies

    # Generate report for invoices
    def generate_report(df):
        st.write("### Invoice Report")

        # Summary statistics
        total_invoices = len(df)
        total_amount = df["Invoice Amount"].sum()
        avg_invoice = df["Invoice Amount"].mean()

        st.write(f"- Total number of invoices: {total_invoices}")
        st.write(f"- Total amount payable: {total_amount}")
        st.write(f"- Average invoice amount: {avg_invoice:.2f}")

        # Plotting payment terms distribution
        st.write("#### Payment Terms Distribution")
        payment_terms_counts = df["Payment Terms"].value_counts()
        fig, ax = plt.subplots()
        payment_terms_counts.plot(kind='bar', ax=ax, color='skyblue')
        plt.title("Payment Terms Distribution")
        plt.xlabel("Payment Terms")
        plt.ylabel("Count")
        st.pyplot(fig)

    # Display AI chat-like interaction
    user_query = st.text_input("Ask the AI agent a question (e.g., 'Which invoices are due soon?')")

    if user_query:
        prompt = f"Here are the invoices: {invoices.to_dict()}. User question: {user_query}"
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            ai_reply = response["choices"][0]["message"]["content"]
            st.write("### AI Agent Response")
            st.write(ai_reply)
        except Exception as e:
            st.error(f"Error querying OpenAI: {e}")
