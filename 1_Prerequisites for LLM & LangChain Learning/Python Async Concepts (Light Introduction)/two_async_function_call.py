import asyncio
import httpx

async def get_users(client):
    response = await client.get("https://jsonplaceholder.typicode.com/users")
    return response.json()
    

async def get_posts(client):
    response = await client.get("https://jsonplaceholder.typicode.com/posts")
    return response.json()

async def main():
    async with httpx.AsyncClient() as client:
        users,posts = await asyncio.gather(get_users(client),get_posts(client))
        print(users[0:2])
        print(posts[:2])


asyncio.run(main())