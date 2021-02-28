import time


class Logger:
    def __init__(self, log_to_console=True, log_to_file=True, log_file=''):
        self.log_to_console = log_to_console
        self.log_to_file = log_to_file
        if self.log_to_file:
            if log_file == '':
                log_file = f'{time.strftime("%x %X")}.log'
        self.log_file = log_file

    async def log(self, text, method_name=''):
        log_string = f'[{time.strftime("%x %X")}]{("["+method_name+"]") if method_name != "" else ""}\n{text}\n\n'
        if self.log_to_console:
            print(log_string)
        if self.log_to_file:
            async with open(self.log_file, 'a', 1) as log:
                log.write(log_string)
