
# Async-TIO

This is a simple unofficial async Api-wrapper for [tio.run](https://tio.run/#)

## Installation (PyPI)

```bash
py -m pip install async_tio
```

## Install Latest

```bash
py -m pip install git+https://github.com/Tom-the-Bomb/async-tio.git
```

## Basic Example

```py
# assuming you are already inside an async environment and have already imported everything
# to instantiate:
#
# - It is recommended to have a global class if you are going to run `execute()` more than 1 time throughout the program
#
# - Alternatively you can use the async context manager if it's a one time use:
#   `async with async_tio.Tio() as tio: ...`
tio = async_tio.Tio() # Optional 'loop' and 'session' kwargs etc. if needed

# to execute
output = await tio.execute("print('')", language="python3") # pass in additional optional kwargs if needed

print(str(output)) # the formatted output along with the stats
print(output.stdout) # the output by itself
print(int(output)) # returns the exit status

# print(vars(output).keys())
# > dict_keys(['token', 'output', 'stdout', 'real_time', 'user_time', 'sys_time', 'cpu_usage', 'exit_status'])
# all the attributes of the response object you can access
```
