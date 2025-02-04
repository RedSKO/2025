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
            position: fixed;
            top: 15px;
            left: 15px;
            background-image: url('https://i.imgur.com/7ybfu5A.png');
            background-size: cover;
            width: 40px;
            height: 40px;
            z-index: 999;
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

invoices_df = pd.DataFrame(INVOICES)

# Analyze invoices for payment priority
def prioritize_invoices(df):
    urgent = df[df["Due Date"] < (datetime.date.today() + datetime.timedelta(days=10))]
    high_value = df[df["Amount"] > 3000]
    return urgent, high_value

def generate_recommendations():
    urgent_invoices, high_value_invoices = prioritize_invoices(invoices_df)
    
    recommendations = []
    if not urgent_invoices.empty:
        recommendations.append(f"Invoice {urgent_invoices.iloc[0]['Invoice ID']} is due in {(urgent_invoices.iloc[0]['Due Date'] - datetime.date.today()).days} days.")
    if not high_value_invoices.empty:
        recommendations.append(f"High-value Invoice {high_value_invoices.iloc[0]['Invoice ID']} requires review for an amount of {high_value_invoices.iloc[0]['Amount']}.")
    
    return recommendations, urgent_invoices, high_value_invoices

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

def main():
    st.set_page_config(page_title="AI Invoice Agent", layout="centered")
    chatbot_icon()

    st.markdown("# AI-Powered Invoice Agent 🤖")
    st.write("This agent provides intelligent financial recommendations and automates workflows based on ABBYY Vantage-extracted data.")

    st.markdown("## Uploaded Invoices")
    with st.expander("View Invoices"):
        st.dataframe(invoices_df)

    recommendations, urgent_invoices, high_value_invoices = generate_recommendations()

    st.markdown("### Automated AI Recommendations")
    if recommendations:
        st.warning(recommendations[0])
        if st.button("View Full List of Recommendations"):
            for rec in recommendations:
                st.info(rec)

    st.markdown("### Ask the AI Agent 🧠")
    user_input = st.text_input("Ask about invoice insights, risks, or payment advice")

    if user_input:
        invoice_summary = "\n".join([
            f"Invoice {row['Invoice ID']} with amount {row['Amount']} due on {row['Due Date']} (Condition: {row['Payment Condition']})"
            for _, row in invoices_df.iterrows()
        ])
        ai_response = ask_ai_agent(user_input, invoice_summary)
        message(ai_response)

    st.markdown("### Generate PDF Report")
    if st.button("Download AI Report"):
        generate_pdf_report(invoices_df, recommendations)

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

