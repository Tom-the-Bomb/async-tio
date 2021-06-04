from __future__ import annotations

import re

from zlib import compress
from typing import Optional, Tuple
from asyncio import get_event_loop, get_running_loop, AbstractEventLoop

from aiohttp import ClientSession

from .response import TioResponse
from .exceptions import ApiError, LanguageNotFound


class Tio:

    def __init__(
        self, 
        session: Optional[ClientSession] = None, 
        loop: Optional[AbstractEventLoop] = None
    ) -> None:

        self.API_URL       = "https://tio.run/cgi-bin/run/api/"
        self.LANGUAGES_URL = "https://tio.run/languages.json"
        self.languages = []

        if loop:
            self.loop = loop
        else:
            try:
                self.loop = get_running_loop()
            except RuntimeError:
                self.loop = get_event_loop()
        
        if session:
            self.session = session
        else:
            self.session = None

        self.loop.run_until_complete(self._initialize())

    async def __aenter__(self) -> Tio:
        await self._initialize()
        return self

    async def __aexit__(self, *_) -> None:
        await self.close()

    async def close(self):
        await self.session.close()

    async def _initialize(self) -> None:
        self.session = ClientSession()
        async with self.session.get(self.LANGUAGES_URL) as r:
            if r.ok:
                data = await r.json()
                self.languages = list(data.keys())
            return None

    def _format_payload(self, name: str, obj: str) -> bytes:
        if not obj:
            return b''
        elif isinstance(obj, list):
            content = ['V' + name, str(len(obj))] + obj
            return bytes('\x00'.join(content) + '\x00', encoding='utf-8')
        else:
            return bytes(
                f"F{name}\x00{len(bytes(obj, encoding='utf-8'))}\x00{obj}\x00", 
                encoding='utf-8'
            )
    
    async def execute(
        self, code: str, *, 
        language  : str, 
        inputs    : Optional[str] = "",
        compiler_flags: Optional[list] = [], 
        Cl_options: Optional[list] = [], 
        arguments : Optional[list] = [], 
    ) -> Optional[TioResponse]:

        if language not in self.languages:
            match = [l for l in self.languages if language in l]
            if match:
                language = match[0]

        data = {
            "lang"       : [language],
            ".code.tio"  : code,
            ".input.tio" : inputs,
            "TIO_CFLAGS" : compiler_flags,
            "TIO_OPTIONS": Cl_options,
            "args"       : arguments,
        }

        bytes_ = b''.join(
            map(self._format_payload, data.keys(), data.values())
        ) + b'R'

        data = compress(bytes_, 9)[2:-4]

        async with self.session.post(self.API_URL, data=data) as r:

            if r.ok:
                data = await r.read()
                data = data.decode("utf-8")

                if re.search(r"The language ?'.+' ?could not be found on the server.", data):
                    raise LanguageNotFound(data[16:])
                else:
                    return TioResponse(data, language)
            else:
                raise ApiError(f"Error {r.status}, {r.reason}")