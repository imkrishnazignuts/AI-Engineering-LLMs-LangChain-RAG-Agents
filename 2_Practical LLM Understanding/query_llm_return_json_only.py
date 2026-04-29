"""import openai



inp_text = "Hi team, I'm unable to log in since yesterday. My email is john.doe@example.com. I need this resolved urgently. "

response = client.responses.create(
    model="gpt-3.5-turbo-0125",
    input=[
        {
            "role":"developer",
            "content":("Strictly give response in valid JSON only" 
                "Extract information like username,email, issue_summary, urgency_level. "
                "urgency_level must be one of: High, Medium, Low. "
                "If a field is missing, return null.")
        },{
            "role":"user",
            "content":inp_text
        }
    ]
)

print(response.output_text)"""


from google import genai
import json

client = genai.Client(api_key= "")

ticket = """
Hi team, I'm unable to log in since yesterday.
My email is john.doe@example.com.
I need this resolved urgently.
"""

prompt = f"""
Extract the following fields from the support ticket.

Return valid JSON only with exactly these keys:
- user_name
- email
- issue_summary
- urgency_level

Rules:
- Use null if user_name or email is missing
- urgency_level must be exactly one of: High, Medium, Low
- Keep issue_summary short and clear
- Do not add extra keys

Support ticket:
{ticket}
"""

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=prompt,
    config={
        "temperature": 0.1
    }
)

print(response.text)

