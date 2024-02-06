from . import View, Window
from typing import Tuple, Dict, Optional, List, Callable
from threading import Lock

PanelEntry = Tuple[str, View]
OnPanelGotFocus = Callable[[PanelEntry], None]

# record last panel for specific window
_last_panel: Dict[Window, PanelEntry] = {}

# view of `console` panel
_console_view: Dict[Window, View] = {}

# subscribers of panel focus event
_panel_focus_subscribers: List[OnPanelGotFocus] = []
_subscribe_lock = Lock()

def set_last_panel(w: Window, panel: str, view: Optional[View]):
    global _last_panel
    _last_panel[w] = (panel, view)

def last_panel(w: Window) -> Optional[PanelEntry]:
    global _last_panel
    return _last_panel.get(w)

def set_console_view(w: Window, view: View):
    global _console_view
    _console_view[w] = view

def console_view(w: Window) -> Optional[View]:
    global _console_view
    return _console_view[w]

def subscribe_panel_focus_event_once(callback: OnPanelGotFocus):
    _subscribe_lock.acquire()
    _panel_focus_subscribers.append(callback)
    _subscribe_lock.release()

def fetch_subscribers() -> List[OnPanelGotFocus]:
    _subscribe_lock.acquire()
    subscribers = _panel_focus_subscribers[:]
    _panel_focus_subscribers.clear()
    _subscribe_lock.release()
    return subscribers

def show_panel(w: Window, panel: str):
    w.run_command('show_panel', args={'panel': panel})

def hide_panel(w: Window):
    w.run_command('hide_panel')
