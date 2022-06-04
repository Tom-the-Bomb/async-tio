from __future__ import annotations

from typing import TYPE_CHECKING, Any, Tuple, TypedDict, Union
from dataclasses import dataclass

if TYPE_CHECKING:

    class LanguageData(TypedDict):
        name: str
        categories: list[str]
        encoding: str
        link: str
        prettyify: str
        tests: dict[str, dict[str, dict[str, str]]]
        unmask: list[str]
        updates: str


__all__: Tuple[str, ...] = (
    'TioResponse',
    'Language',
)

class TioResponse:
    """A model representing the response returned from TIO

    Attributes
    ----------
    token : str
        the token of the execution session
    output : str
        the formatted full output with stdout/stderr and the execution stats
    provided_language : str
        the programming language that was used for the execution
    stdout : str
        the pure stdout of the execution (without execution stats)
    real_time : float
        the total time of execution
    user_time : float
        the user time of execution
    sys_time : float
        the system time of execution
    cpu_usage : float
        the CPU usage taken during execution (as a percentage)
    exit_status : int
        the exit status for the program
    """
    def __init__(self, data: str, language: str) -> None:

        self.stdout: str = ''
        self.real_time: float = float('NaN')
        self.user_time: float = float('NaN')
        self.sys_time: float = float('NaN')
        self.cpu_usage: float = float('NaN')
        self.exit_status: int = 0

        self.token: str = data[:16]
        self.output: str = data.replace(self.token, '')
        self.provided_language: str = language

        stats = self.output.split('\n')

        try:
            self.stdout = '\n'.join(stats[:-5])
            self.real_time = float(self._parse_line(stats[-5]))
            self.user_time = float(self._parse_line(stats[-4]))
            self.sys_time = float(self._parse_line(stats[-3]))
            self.cpu_usage = float(self._parse_line(stats[-2]))
            self.exit_status = int(self._parse_line(stats[-1]))
        except IndexError:
            pass

    def __repr__(self):
        return f"<TioResponse status={self.exit_status}>"

    def __str__(self) -> str:
        """returns the full formated output of the execution"""
        return self.output

    def __int__(self) -> int:
        """returns the exit status of the execution"""
        return self.exit_status

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TioResponse):
            return self.stdout == other.stdout
        else:
            return self.stdout == other
        
    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def _parse_line(self, line: str) -> str:
        return line.split(':')[-1].strip().split()[0]


class Language:
    """A model class representing a language available in TIO

    Attributes
    ----------
    tio_name : str
        the name of the language TIO expects us to provide for execution
    name : str
        the actual, raw name of the language
    categories : list[str]
        some tags for the programming language
    encoding : str
        the encoding format of the language, e.g. utf-8
    link : str
        the link to the home page of the language
    alias : str
        a shortened alias for the name of the language
    """
    __slots__ = (
        'tio_name',
        'name',
        'categories',
        'encoding',
        'link',
        'alias',
    )

    def __init__(self, name: str, data: Union[LanguageData, dict[str, Any]]) -> None:
        self.tio_name: str = name
        self.name = data.get('name')
        self.categories = data.get('categories', [])
        self.encoding = data.get('encoding')
        self.link = data.get('link')
        self.alias = data.get('prettyify')

    def __repr__(self) -> str:
        return f'<Language name="{self.tio_name}" alias="{self.alias}">'

    def __str__(self) -> str:
        return self.tio_name

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Language):
            return self.tio_name == other.tio_name
        else:
            return other in {self.tio_name, self.name, self.alias}