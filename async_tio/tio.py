
from zlib    import compress
from functools import partial
from typing import Optional

from aiohttp import ClientSession
from asyncio import get_event_loop, AbstractEventLoop

from src.response import TioResponse
from src.exceptions import ApiError

class Tio:

    def __init__(self, loop: Optional[AbstractEventLoop] = None):
        self.API_URL = "https://tio.run/cgi-bin/run/api/"

        if loop:
            self._loop = loop
        else:
            self._loop = get_event_loop()

        self._loop.create_task(self.__ainit__())

    async def __ainit__(self):
        self.session = ClientSession()

    async def __aenter__(self):
        self.session = ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self.session.close()

    def _format_payload(self, pair: tuple):
        name, obj = pair
        to_bytes  = partial(bytes, encoding='utf-8')
        if not obj:
            return b''
        elif isinstance(obj, list):
            content = ['V' + name, str(len(obj))] + obj
            return to_bytes('\x00'.join(content) + '\x00')
        else:
            return to_bytes(f"F{name}\x00{len(to_bytes(obj))}\x00{obj}\x00")
    
    async def execute(
        self, code: str, *, 
        language  : str, 
        inputs    : Optional[str] = "",
        compiler_flags: Optional[list] = [], 
        Cl_options: Optional[list] = [], 
        arguments : Optional[list] = [], 
    ):

        data = {
            "lang"       : [language],
            ".code.tio"  : code,
            ".input.tio" : inputs,
            "TIO_CFLAGS" : compiler_flags,
            "TIO_OPTIONS": Cl_options,
            "args"       : arguments,
        }

        bytes_ = b''.join(map(self._format_payload, data.items())) + b'R'
        data   = compress(bytes_, 9)[2:-4]

        async with self.session.post(self.API_URL, data=data) as r:

            if r.ok:
                data = await r.read()
                data = data.decode("utf-8")
                return TioResponse(data)
            else:
                raise ApiError(f"Error {r.status} {r.reason}")