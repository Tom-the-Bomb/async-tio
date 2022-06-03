from __future__ import annotations

import re
import zlib
from typing import (
    TYPE_CHECKING,
    ClassVar, 
    Optional, 
    Union,
    Type,
    List,
    Any,
)

from aiohttp import ClientSession

from .response import TioResponse
from .exceptions import ApiError, LanguageNotFound

if TYPE_CHECKING:
    from types import TracebackType
    from typing_extensions import Self, TypeAlias

    PayloadType: TypeAlias = Union[str, List[str]]

class Tio:
    API_URL: ClassVar[str] = 'https://tio.run/cgi-bin/run/api/'
    LANGUAGES_URL: ClassVar[str] = 'https://tio.run/languages.json'
    _http_session: ClientSession

    def __init__(self, *, session: Optional[ClientSession] = None) -> None:
        self._languages: list[str] = []

        if session:
            self._http_session = session
        else:
            self._http_session = ClientSession()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self, 
        exc_type: Optional[Type[BaseException]], 
        exc_val: Optional[BaseException], 
        exc_tb: Optional[TracebackType],
    ) -> None:
        return await self.close()

    async def close(self) -> None:
        """closes the internal http session"""
        if session := self._http_session:
            await session.close()

    async def get_languages(self) -> list:
        if not self._languages:
            async with self._http_session.get(self.LANGUAGES_URL) as response:
                if response.ok:
                    data: dict[str, Any] = await response.json()
                    self._languages = list(data.keys())
        
        return self._languages

    def _format_payload(self, key: str, value: PayloadType) -> bytes:
        """encodes the payload into bytes for tio execution"""
        if not value:
            return b''
            
        if isinstance(value, (tuple, list)):
            values = '\x00'.join(value)
            byt = f'V{key}\x00{len(value)}\x00{values}\x00'
        else:
            byt = f'F{key}\x00{len(value.encode())}\x00{value}\x00'
        return byt.encode(errors='ignore')
    
    async def execute(
        self, 
        code: str,
        *,
        language: str, 
        inputs: str = '',
        compiler_flags: Optional[list[str]] = None, 
        cli_options: Optional[list[str]] = None, 
        arguments: Optional[list[str]] = None, 
    ) -> TioResponse:
        """|coro|
        
        makes an execution to `TIO`

        Parameters
        ----------
        code : str
            the code to execute
        language : str
            the language of the executed code (see `Tio.languages`)
        inputs : str, optional
            stdin inputs for the program, by default ''
        compiler_flags : Optional[list[str]], optional
            compiler flags, by default None
        cli_options : Optional[list[str]], optional
            command line options, by default None
        arguments : Optional[list[str]], optional
            additional arguments, by default None

        Returns
        -------
        TioResponse
            the response for the execution

        Raises
        ------
        LanguageNotFound
            The provided language is unavailable
        ApiError
            The API returned a non OK status code
        """
        data: dict[str, PayloadType] = {
            'lang': [language],
            '.code.tio': code,
            '.input.tio': inputs,
            'TIO_CFLAGS': compiler_flags or [],
            'TIO_OPTIONS': cli_options or [],
            'args': arguments or [],
        }

        byt: bytes = b''.join([
            self._format_payload(key, value) for key, value in data.items()
        ]) + b'R'

        data = zlib.compress(byt, zlib.Z_BEST_COMPRESSION)[2:-4]

        async with self._http_session.post(self.API_URL, data=data) as response:
            if response.ok:
                resp_data = await response.read()
                resp_data = resp_data.decode(errors='ignore')

                if re.search(r"The language '.+' could not be found on the server", resp_data):
                    raise LanguageNotFound(resp_data[16:])
                else:
                    return TioResponse(resp_data, language)
            else:
                raise ApiError(response)