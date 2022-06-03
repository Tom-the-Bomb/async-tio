
import asyncio

from async_tio import Tio

async def main():
    async with Tio() as tio:
        return await tio.execute('print(1+2/3); print("bob")', language='python3')

print(asyncio.run(main()))