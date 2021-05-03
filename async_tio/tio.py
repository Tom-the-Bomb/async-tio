import re

from zlib    import compress
from functools import partial
from typing import Optional
from inspect import isawaitable

from aiohttp import ClientSession
from asyncio import get_event_loop, AbstractEventLoop

from .response import TioResponse
from .exceptions import ApiError, LanguageNotFound

class AsyncMeta(type):

    async def __call__(self, *args, **kwargs):

        obb = object.__new__(self)
        fn  = obb.__init__(*args, **kwargs)

        if isawaitable(fn):
            await fn
        return obb

class Tio(metaclass=AsyncMeta):

    async def __init__(self, session: Optional[ClientSession] = None, loop: Optional[AbstractEventLoop] = None):
        self.API_URL       = "https://tio.run/cgi-bin/run/api/"
        self.LANGUAGES_URL = "https://tio.run/languages.json"
        self.languages = []

        if loop:
            self.loop = loop
        else:
            self.loop = get_event_loop()
        
        if session:
            self.session = session
        else:
            self.session = ClientSession()

        await self._update_languages

    async def __aenter__(self):
        self.session = ClientSession()
        await self._update_languages
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self.session.close()

    async def _update_languages(self):

        async with self.session.get(self.LANGUAGES_URL) as r:
            if r.ok:
                data = await r.json()
                self.languages = list(data.keys())

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

                if re.search(r"The language ?'.+' ?could not be found on the server.", data):
                    raise LanguageNotFound(data[16:])
                else:
                    return TioResponse(data)
            else:
                raise ApiError(f"Error {r.status} {r.reason}")