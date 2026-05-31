from PyQt6.QtCore import QThread, pyqtSignal
import threading

class AnalysisWorker(QThread):
    finished_signal = pyqtSignal(object)
    error_signal = pyqtSignal(str)
    tie_break_signal = pyqtSignal(list)

    def __init__(self, target_func, *args, **kwargs):
        super().__init__()
        self.target_func = target_func
        self.args = args
        self.kwargs = kwargs
        self.wait_event = threading.Event()
        self.tie_break_result = []

    def run(self):
        try:
            result = self.target_func(*self.args, **self.kwargs)
            self.finished_signal.emit(result)
        except Exception as e:
            self.error_signal.emit(str(e))

    def handle_tie_break(self, tied_pis):
        """
        Pauses the worker thread and emits a signal to the UI to resolve a tie.
        Returns the selection made by the user.
        """
        self.wait_event.clear()
        self.tie_break_signal.emit(tied_pis)
        self.wait_event.wait() # Block until resolve_tie_break is called
        return self.tie_break_result

    def resolve_tie_break(self, selected_pis):
        """
        Called from the UI thread to resume the worker thread with a result.
        """
        self.tie_break_result = selected_pis
        self.wait_event.set()
