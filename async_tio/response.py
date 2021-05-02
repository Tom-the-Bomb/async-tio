
from async_tio.exceptions import LanguageNotFound

class TioResponse:

    def __init__(self, data: str):

        self.token = data[:16]
        
        data = data.replace(data[:16], "")
        self.output = data

        if data.startswith("The language") and data.endswith("could not be found on the server."):
            raise LanguageNotFound(self.output)

        stats = data.split("\n")
        parse_line = lambda line: line.split(":")[-1].strip().split(" ")[0]

        try:
            self.stdout      = "\n".join(stats[:-6])
            self.real_time   = parse_line(stats[-6])
            self.user_time   = parse_line(stats[-5])
            self.sys_time    = parse_line(stats[-4])
            self.cpu_usage   = parse_line(stats[-3])
            self.exit_status = parse_line(stats[-2])
        except IndexError:
            pass

    def __repr__(self):
        return f"<TioResponse status={self.exit_status}>"

    def __str__(self):
        return self.output

    def __int__(self):
        return self.exit_status

    def __eq__(self, o):
        if isinstance(o, TioResponse):
            return self.output == o.output
        else:
            return self.output == o
        
    def __ne__(self, o):
        return not self.__eq__(o)