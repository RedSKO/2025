import streamlit as st
import openai
from streamlit_chat import message
import datetime
import random
import pandas as pd
import base64

# Set OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Helper to add chatbot icon
def chatbot_icon():
    st.markdown(
        """
        <style>
        .chat-icon {
            position: absolute;
            top: 10px;
            right: 15px;
            background-image: url('https://i.imgur.com/7ybfu5A.png');
            background-size: contain;
            background-repeat: no-repeat;
            width: 50px;
            height: 50px;
        }
        </style>
        <div class='chat-icon'></div>
        """,
        unsafe_allow_html=True,
    )

# Simulate 50 invoice records
INVOICES = [
    {
        "Invoice ID": f"INV-{i+1:03}",
        "Amount": round(random.uniform(500, 5000), 2),
        "Due Date": datetime.date.today() + datetime.timedelta(days=random.randint(1, 60)),
        "Payment Condition": random.choice(["2% discount if paid within 10 days", "Standard payment", "5% surcharge after 30 days"])
    }
    for i in range(50)
]

# Convert invoices to DataFrame
invoices_df = pd.DataFrame(INVOICES)

# Analyze invoices for payment priority
def prioritize_invoices(df):
    urgent = df[df["Due Date"] < (datetime.date.today() + datetime.timedelta(days=10))]
    high_value = df[df["Amount"] > 3000]

    return urgent, high_value

# Generate intelligent recommendations
def generate_recommendations():
    urgent_invoices, high_value_invoices = prioritize_invoices(invoices_df)

    recommendations = []
    if not urgent_invoices.empty:
        for _, row in urgent_invoices.iterrows():
            days_remaining = (row["Due Date"] - datetime.date.today()).days
            recommendations.append(f"Invoice {row['Invoice ID']} is due in {days_remaining} days. Prioritize payment.")

    if not high_value_invoices.empty:
        for _, row in high_value_invoices.iterrows():
            recommendations.append(f"High-value Invoice {row['Invoice ID']} requires review due to an amount of {row['Amount']}.")

    return recommendations

# ChatGPT-powered insights
def ask_ai_agent(user_input, invoice_summary):
    prompt = f"Here are 50 invoices summarized:\n{invoice_summary}\nUser question: {user_input}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a financial assistant AI agent analyzing invoices."},
                {"role": "user", "content": prompt}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error querying AI: {e}"

# UI for app
def main():
    st.set_page_config(page_title="AI Invoice Agent", layout="centered")
    chatbot_icon()

    st.markdown("# AI-Powered Invoice Agent 🚀")
    st.write("This agent provides intelligent financial recommendations and automates workflows based on ABBYY Vantage-extracted data.")

    # Show invoice data
    st.markdown("## Uploaded Invoices")
    with st.expander("View Invoices"):
        st.dataframe(invoices_df)

    # Proactive recommendations
    recommendations = generate_recommendations()
    st.markdown("### Automated AI Recommendations")
    for rec in recommendations:
        st.warning(rec)

    if recommendations and st.button("Initiate Payment for First Recommendation"):
        st.success(f"Payment process initiated for Invoice {recommendations[0].split()[1]}.")

    # AI Chat Agent Section
    st.markdown("### Ask the AI Agent 🧠")
    user_input = st.text_input("Ask about invoice insights, risks, or payment advice")

    if user_input:
        invoice_summary = "\n".join([
            f"Invoice {row['Invoice ID']} with amount {row['Amount']} due on {row['Due Date']} (Condition: {row['Payment Condition']})"
            for _, row in invoices_df.iterrows()
        ])
        ai_response = ask_ai_agent(user_input, invoice_summary)
        message(ai_response)

    # Generate Report Button
    st.markdown("### Generate PDF Report")
    if st.button("Download AI Report"):
        generate_pdf_report(invoices_df, recommendations)

# PDF report generation
def generate_pdf_report(df, recommendations):
    import io
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "AI Invoice Insights Report")
    c.drawString(100, 730, "---")
    c.drawString(100, 710, "Recommendations:")
    y = 690

    for rec in recommendations:
        c.drawString(100, y, f"- {rec}")
        y -= 20
        if y < 50:
            c.showPage()
            y = 750

    c.save()

    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="AI_Invoice_Report.pdf">Download Report</a>'
    st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
