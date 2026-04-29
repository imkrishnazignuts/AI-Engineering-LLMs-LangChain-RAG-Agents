from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0
)

from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template("""
You are a corporate email compliance assistant.

Your task is to review an outgoing email and detect only REAL compliance, legal, privacy, business, or professionalism risks.

Check for:
- unrealistic promises or guarantees
- pricing mistakes or unauthorized discounts
- NDA/confidential information leaks
- personal data exposure
- insulting, abusive, threatening, or clearly unprofessional language
- legal or contractual commitments
- misleading claims

Important rules:
- Do NOT flag normal greetings like "Hi", "Hello", "Dear team", or "Thanks" as risks.
- Do NOT invent risks.
- Only report a risk if the email text clearly contains one.
- If the email is normal and professional, mark it as safe.
- Severity rating must be an integer from 1 to 10.
- 1 means very low risk.
- 10 means very high risk.

Return JSON only in this format:

{{
  "risk_detected": true,
  "severity_rating": 1,
  "issues": [
    {{
      "risk_type": "type of risk",
      "why_it_is_a_risk": "clear explanation",
      "suggested_alternative_wording": "safer rewrite"
    }}
  ],
  "final_summary": "short overall summary"
}}

If no issue is found, return:
- "risk_detected": false
- "severity_rating": 1
- "issues": []
- "final_summary": "No major compliance risk detected."

Email body:
{email_body}
""")

parser = JsonOutputParser()

chain = prompt | llm | parser


email_body = input("paste or type Email body: ")
result = chain.invoke({"email_body":email_body})

print('\n')

for key, value in result.items():
    print(f"{key} : {value}")