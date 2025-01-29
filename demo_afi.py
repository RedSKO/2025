import streamlit as st
import openai
from streamlit_chat import message
import datetime
import random
import pandas as pd
import base64

# Set up the OpenAI API key (replace with your own API key)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Helper function to create a chatbot icon
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

# Invoice simulation data
INVOICES = [
    {
        "Invoice ID": f"INV-{i+1:03}",
        "Amount": round(random.uniform(500, 5000), 2),
        "Due Date": datetime.date.today() + datetime.timedelta(days=random.randint(1, 60)),
        "Payment Condition": random.choice(["2% discount if paid within 10 days", "Standard payment", "5% surcharge after 30 days"])
    }
    for i in range(50)
]

# Convert invoices to DataFrame for easy analysis
invoices_df = pd.DataFrame(INVOICES)

# Main UI
def main():
    st.set_page_config(page_title="AI Invoice Agent", layout="centered")
    chatbot_icon()
    
    st.markdown("# AI-Powered Invoice Insights")
    st.write("This agent provides recommendations based on invoice data extracted by ABBYY Vantage.")
    
    st.markdown("### Ask the AI Agent")
    user_input = st.text_input("Your question about the invoices")

    if user_input:
        # Simple response generation using OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI agent providing financial recommendations."},
                {"role": "user", "content": user_input}
            ]
        )
        response_text = response["choices"][0]["message"]["content"]
        message(response_text)

    # Display simulated data
    st.markdown("---")
    st.markdown("## Uploaded Invoices")
    with st.expander("Show uploaded invoices"):
        st.dataframe(invoices_df)

    st.markdown("### Automated Recommendations")
    recommendations = []
    urgent_invoices = invoices_df[invoices_df["Due Date"] < (datetime.date.today() + datetime.timedelta(days=10))]

    for _, row in urgent_invoices.iterrows():
        due_in_days = (row["Due Date"] - datetime.date.today()).days
        recommendations.append(f"Invoice {row['Invoice ID']} is due in {due_in_days} days. Payment recommended.")
    
    for rec in recommendations:
        st.warning(rec)

    # Automatic payment simulation example
    if recommendations:
        if st.button("Start Payment Process for First Urgent Invoice"):
            st.success(f"Payment process initiated for Invoice {urgent_invoices.iloc[0]['Invoice ID']}.")

    # Generate PDF Report
    st.markdown("### Generate Report")
    if st.button("Download PDF Report"):
        generate_pdf_report(invoices_df, recommendations)

# Function to generate a PDF report
def generate_pdf_report(df, recommendations):
    import io
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "AI Invoice Insights Report")

    # Add recommendations
    c.drawString(100, 730, "Recommendations:")
    y = 710
    for rec in recommendations:
        c.drawString(100, y, f"- {rec}")
        y -= 20
        if y < 50:
            c.showPage()
            y = 750

    c.save()

    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="Invoice_Insights_Report.pdf">Download Report</a>'
    st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
