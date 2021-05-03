# Async-Tio
This is a simple unofficial async Api-wrapper for [tio.run](https://tio.run/#)

**Installation**
```bash
$ pip install async_tio
```

**Examples**
```py
import asyncio
import async_tio

async def main():

    async with await async_tio.Tio() as tio:
        print(tio.languages) #list of all supported languages

        #execute the code
        return await tio.execute("print('hello world')", language="python3")

    #Or you can do
    tio = await async_tio.Tio() #instantiate a Tio object
    ...
    #do stuff
    ...
    #at the end
    await tio.close()

output = asyncio.run(main())

print(str(output)) #the formatted output along with the stats
print(int(output)) #returns the exit status

print(vars(output).keys())
# dict_keys(['token', 'output', 'stdout', 'real_time', 'user_time', 'sys_time', 'cpu_usage', 'exit_status'])
# all the attributes of the response object
```
