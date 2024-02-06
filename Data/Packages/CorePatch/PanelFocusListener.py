from .lib import EventListener, View
from .lib import panel as PanelUtils

class PanelFocusListener(EventListener):
    def on_activated(self, view: View):
        w = view.window()
        if view.element() is None or w is None:
            return

        panel = w.active_panel()
        if panel is None:
            return

        ignores = {'find', 'find_in_files', 'replace'}
        if panel in ignores:
            return

        PanelUtils.set_last_panel(w, panel, view)

        if panel == 'console':
            PanelUtils.set_console_view(w, view)

        state = PanelUtils.last_panel(w)
        subs = PanelUtils.fetch_subscribers()
        for callback in subs:
            callback(state)
