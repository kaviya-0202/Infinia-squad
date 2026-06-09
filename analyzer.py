import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def analyze_ticket(ticket_text):
    prompt = f"""
    Analyze the following customer support ticket and return:
    - Sentiment (Positive/Negative/Neutral)
    - Urgency Level (High/Medium/Low)
    - Churn Risk (High/Medium/Low)

    Ticket: {ticket_text}

    Respond in this exact format:
    Sentiment: <value>
    Urgency: <value>
    Churn Risk: <value>
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content