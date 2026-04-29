from langchain.agents import create_agent
from dotenv import load_dotenv
import requests
import os
from duckduckgo_search import DDGS

load_dotenv()

API_KEY = "4639a6a74439152614b1a5f12df9a53d"


def search_web(query, max_results=5):
    """use this when user said search on browser """
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=max_results)
        return list(results)

def get_weather(city_name: str) -> str:
    """Get current weather for a given city."""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data

agent = create_agent(
    model="groq:openai/gpt-oss-120b",
    tools=[get_weather],
    system_prompt=(
        "You are a helpful assistant. "
        "For any weather-related question, you must use the get_weather tool. "
    )
)

response = agent.invoke({
    "messages": [
        {"role": "user", "content": "search on browser latest news today india ?"}
    ]
})

for msg in response["messages"]:
    print(msg.content)


    print("-" * 50)