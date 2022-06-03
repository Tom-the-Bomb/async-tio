from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from aiohttp import ClientResponse

__all__: Tuple[str, ...] = (
    'LanguageNotFound',
    'ApiError',
)


class LanguageNotFound(Exception):
    pass

class ApiError(Exception):
    
    def __init__(self, response: ClientResponse) -> None:
        self.response = response

        self.status: int = response.status
        self.reason: str = response.reason
        
    @property
    def message(self) -> str:
        return f'The Api Raised an Error: {self.status}, {self.reason}'

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.message}')"