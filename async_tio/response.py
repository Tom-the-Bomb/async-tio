
from typing import Any, Tuple

__all__: Tuple[str, ...] = (
    'TioResponse',
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