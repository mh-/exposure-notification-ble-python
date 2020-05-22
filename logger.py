# Singleton Logger
# Suppresses repeating log lines

# noinspection PyAttributeOutsideInit


class Logger(object):
    __instance = None

    def __new__(cls):
        if Logger.__instance is None:
            Logger.__instance = object.__new__(cls)
            Logger.__instance.last_logged_line = None
        return Logger.__instance

    def log(self, text, end='\n', flush=False):
        if (not text == self.last_logged_line) or (end == ''):
            print(text, end=end, flush=flush)
            self.last_logged_line = text
