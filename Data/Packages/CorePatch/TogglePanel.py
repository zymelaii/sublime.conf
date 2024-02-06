from .lib import WindowCommand
from .lib import panel as PanelUtils

class TogglePanelCommand(WindowCommand):
    def detect_and_track_exec_panel(self):
        view = self.window.find_output_panel('exec')
        if view is None:
            return
        if view.window() is None:
            return
        PanelUtils.set_last_panel(self.window, 'output.exec', view)

    def run(self):
        self.detect_and_track_exec_panel()

        last_state = PanelUtils.last_panel(self.window)
        if last_state is None:
            PanelUtils.show_panel(self.window, 'console')
            return

        panel, view = last_state

        # closed or hidden
        if not view.is_valid() or view.window() is None:
            PanelUtils.show_panel(self.window, panel)
            return

        PanelUtils.hide_panel(self.window)
