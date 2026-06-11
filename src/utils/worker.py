# fsQCA Pro
# Copyright (C) 2026 ImmortalSoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
