
import asyncio

from async_tio import Tio

async def main():
    async with Tio() as tio:
        return await tio.execute('fn main () { loop { println!("bomb") } }', language='rust')

resp = asyncio.run(main())
print(resp.output)