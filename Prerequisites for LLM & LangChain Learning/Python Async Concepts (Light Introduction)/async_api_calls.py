import httpx
import asyncio

async def fetch(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()


async def main():
    data = await fetch("https://randomuser.me/api/")
    print(data)

asyncio.run(main())

