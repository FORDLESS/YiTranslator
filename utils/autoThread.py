import Global
from concurrent.futures import ThreadPoolExecutor


class Autowork:
    def __init__(self, root):
        self.root = root
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.source_task = None
        self.result_task = None
        self.source = None
        self.result = None

    def start_source_task(self):
        if self.source_task is None or self.source_task.done():
            self.source_task = self.executor.submit(self.get_source)

    def start_result_task(self):
        if self.result_task is None or self.result_task.done():
            self.result_task = self.executor.submit(self.get_result)

    def get_source(self):
        Global.getsourceRunning = True
        self.source = self.root.inputCase.gettext()
        Global.getsourceRunning = False

    def get_result(self):
        Global.getresultRunning = True
        self.result = self.root.tsaCase.translate(self.root.source_text, Global.language)
        Global.getresultRunning = False

    def getSource(self):
        return self.source

    def getResult(self):
        return self.result

