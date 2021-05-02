# Async-Tio
This is a simple unofficial async Api-wrapper for [tio.run](https://tio.run/#)

**Installation**
```bash
$ pip install git+https://github.com/Tom-the-Bomb/async-tio.git
```

**Usage**
```py
import asyncio
import async_tio

async def main():
    async with async_tio.Tio() as tio:
        return await tio.execute("print('hello world')", language="python3")

output = asyncio.run(main())

print(str(output)) #the formatted output along with the stats
print(int(output)) #returns the exit status

print(vars(output).keys())
# dict_keys(["token", "output", "real_time", "user_time", "sys_time", "cpu_usage", "exit_status"])
# all the attributes of the response object

```
