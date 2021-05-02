
class TioResponse:

    def __init__(self, data: bytes):

        self.token = data[:16]
        
        data = data.replace(data[:16], "")
        self.output = data

        stats = data.split("\n")
        parse_line = lambda line: line.split(":")[-1].split(" ")[0]

        try:
            self.real_time   = parse_line(stats[-5])
            self.user_time   = parse_line(stats[-4])
            self.sys_time    = parse_line(stats[-3])
            self.cpu_usage   = parse_line(stats[-2])
            self.exit_status = parse_line(stats[-1])
        except IndexError:
            pass

    def __repr__(self):
        return f"<TioResponse status={self.exit_status}>"

    def __str__(self):
        return self.output

    def __int__(self):
        return self.exit_status