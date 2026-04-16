import time
import asyncio 
def get_data(name,delay):
    print(f"Fethcing {name}")
    time.sleep(delay)
    print("Data.....")
    print(f"Finished")

start = time.perf_counter() 
get_data("API 1",2)
get_data("API 2",2)
get_data("API 3",2)
end = time.perf_counter()

print(f"time taken in Sync Function is : {end-start:.2f}")

async def get_data_async(name,delay):
    print(f"Fethcing {name}")
    await asyncio.sleep(delay)
    print("Data.....")
    print(f"Finished")

async def main():
    start = time.perf_counter() 
    await asyncio.gather(get_data_async("API 1",2),get_data_async("API 2",2),get_data_async("API 3",2))
    end = time.perf_counter()
    print(f"time taken in Async Function is : {end-start:.2f}")

asyncio.run(main())

