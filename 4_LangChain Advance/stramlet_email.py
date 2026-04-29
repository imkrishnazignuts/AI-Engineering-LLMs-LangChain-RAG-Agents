import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
import json

st.set_page_config(page_title="Email Compliance Checker", page_icon="📧")

st.title("Corporate Email Compliance Assistant")
st.write("Paste the email body below and check for compliance risks.")

email_body = st.text_area("Email Body", height=300, placeholder="Paste outgoing email body here...")

prompt = PromptTemplate.from_template("""
You are a corporate email compliance assistant.

Your task is to review an outgoing email and detect only clear, explicit, evidence-based compliance risks.

You may detect risks only if the email clearly contains one of these:
- unrealistic promises or guarantees
- pricing mistakes or unauthorized discounts
- NDA/confidential/internal information exposure
- personal data exposure
- insulting, abusive, threatening, or clearly unprofessional language
- legal or contractual commitments
- misleading claims

Very important rules:
- Do NOT invent risks.
- Do NOT over-interpret normal business language.
- Normal greetings, thanks, polite wording, proposals, meeting requests, and general business communication are NOT risks.
- Phrases like "Thank you for your interest", "share a proposal", "let us know your availability", and "we would be happy to discuss" are safe.
- Only flag a risk if there is strong direct evidence in the email text.
- If no clear risk exists, return risk_detected as false.
- Keep severity low when no issue exists.

Return JSON only in this exact format:

{{
  "risk_detected": true,
  "severity_rating": 1,
  "issues": [
    {{
      "risk_type": "type of risk",
      "why_it_is_a_risk": "clear explanation based only on the email text",
      "suggested_alternative_wording": "safer rewrite"
    }}
  ],
  "final_summary": "short overall summary"
}}

If no issue exists, return:
{{
  "risk_detected": false,
  "severity_rating": 1,
  "issues": [],
  "final_summary": "No major compliance risk detected."
}}

Email body:
{email_body}
""")

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)

parser = StrOutputParser()
chain = prompt | llm | parser

if st.button("Check Compliance"):
    if not email_body.strip():
        st.warning("Please enter an email body.")
    else:
        with st.spinner("Analyzing email..."):
            try:
                response = chain.invoke({"email_body": email_body})
                result = json.loads(response)

                st.subheader("Analysis Result")
                st.json(result)

                if result["risk_detected"]:
                    st.error(f"Risk Detected | Severity: {result['severity_rating']}/10")
                else:
                    st.success("No major risk detected.")

            except json.JSONDecodeError:
                st.error("Model did not return valid JSON.")
                st.code(response)
            except Exception as e:
                st.error(f"Error: {e}")