from __future__ import annotations

import re
import zlib
import difflib
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

from .models import *
from .exceptions import ApiError, LanguageNotFound

if TYPE_CHECKING:
    from types import TracebackType
    from typing_extensions import Self, TypeAlias

    PayloadType: TypeAlias = Union[str, List[str]]


class Tio:
    """The Object for code execution to Tio

    Attributes
    ----------
    API_URL : str
        a constant classvar representing the URL to the TIO API API
    LANGUAGES_URL : str
        a constant classvar representing the URL to the TIO languages endpoint

    Methods
    -------
    find_language
        a helper method to search for a closest language match that is valid to TIO
    execute
        makes an execution to TIO
    """
    API_URL: ClassVar[str] = 'https://tio.run/cgi-bin/run/api/'
    LANGUAGES_URL: ClassVar[str] = 'https://tio.run/languages.json'
    _http_session: ClientSession

    def __init__(self, *, session: Optional[ClientSession] = None) -> None:
        self._languages: list[Language] = []

        if session is None:
            self._http_session = ClientSession()
        else:
            self._http_session = session

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

    async def find_language(self, inp_lang: str) -> str:
        """|coro|
        
        a helper method that finds the closest language match with an input.
        E.g. TIO wants "python3" for python but a user may want to input "py" instead for example

        this method is by default also called in `execute` but can be disabled
        if you want by specifying the kwarg `find_closest_lang` as False

        Parameters
        ----------
        inp_lang : str
            the input language "query"

        Returns
        -------
        str
            returns the name of the found language
        """
        languages = await self.get_languages()
        lang_aliases = [lang.alias for lang in languages]

        if inp_lang in languages:
            return inp_lang
        
        try:
            return languages[lang_aliases.index(inp_lang)].tio_name
        except ValueError:
            try:
                return next(lang.tio_name for lang in languages if inp_lang in lang.name)
            except StopIteration:
                lang_names = [lang.tio_name for lang in languages]
                if matches := difflib.get_close_matches(inp_lang, lang_names):
                    return matches[0]
                else:
                    return inp_lang

    async def get_languages(self) -> list[Language]:
        """|coro|

        returns the languages cache, if empty, it lazily
        makes a GET request to tio to fetch all the languages and stores them in the cache

        Returns
        -------
        list[Language]
            returns a list of all the available languages

        Raises
        ------
        ApiError
            The API returned a non OK status code
        """
        if not self._languages:
            async with self._http_session.get(self.LANGUAGES_URL) as response:
                if response.ok:
                    data: dict[str, Any] = await response.json()
                    self._languages = [
                        Language(name, data) for name, data in data.items()
                    ]
                else:
                    raise ApiError(response)
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
        find_closest_lang: bool = True,
    ) -> TioResponse:
        """|coro|
        
        makes an execution to TIO

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
        find_closest_lang : bool
            specifies whether or not to lazily search for a closest language match that is valid to TIO, by default True

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

        if find_closest_lang:
            language = await self.find_language(language)

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

        data = zlib.compress(byt, level=zlib.Z_BEST_COMPRESSION)

        async with self._http_session.post(self.API_URL, data=data[2:-4]) as response:
            if response.ok:
                resp_data = await response.read()
                resp_data = resp_data.decode(errors='ignore')

                if re.search(r"The language '.+' could not be found on the server", resp_data):
                    raise LanguageNotFound(resp_data[16:])
                else:
                    return TioResponse(resp_data, language)
            else:
                raise ApiError(response)