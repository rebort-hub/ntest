import sys


class RedirectPrintLogToMemory:
    """ 重定向print内容到内存中 """

    def __init__(self):
        self.text = ""
        sys.stdout = self

    def write(self, out_stream):
        self.text += out_stream

    def flush(self):
        pass

    def get_text_and_redirect_to_default(self):
        self.redirect_to_default()
        return self.text

    @classmethod
    def redirect_to_default(cls):
        """ 恢复输出到console """
        sys.stdout = sys.__stdout__

    # def __del__(self):
    #     """ 恢复输出到console """
    #     sys.stdout = sys.__stdout__
