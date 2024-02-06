from .lib import Window, View, WindowCommand
from .lib import status_message, yes_no_cancel_dialog
from .lib import DIALOG_CANCEL, DIALOG_YES, DIALOG_NO
from .lib.view_edit import ViewEdit
from .lib.path_completer import PathCompleter
from .lib import panel as PanelUtils
from typing import Optional, Tuple
from os import rename
from os.path import normpath, basename, dirname
from os.path import splitext, isdir, exists
from os.path import join as path_join
from random import choice
from difflib import SequenceMatcher

import re

def random_string(length: int) -> str:
    return ''.join(choice('0123456789abcdef') for _ in range(length))

# remove tabs and record index of the first one
def tab_filter(text: str) -> Tuple[str, int]:
    text = re.sub(r'\t+', '\t', text)
    parts = text.split('\t')
    parts[0] = parts[0].lstrip()

    if len(parts) == 1:
        return (parts[0], -1)

    return (''.join(parts), len(parts[0]))

class IntelliMoveCommand(WindowCommand):
    def __init__(self, window: Window):
        super().__init__(window)
        self.completer = PathCompleter()
        self.reset()

    def reset(self):
        self.view: Optional[View] = None
        self.modifiable: bool = True
        self.last_edit: Optional[str] = None
        self.this: Optional[ViewEdit] = None

    def run(self):
        view = self.window.active_view()
        if self.view == view:
            return

        self.view = view
        self.is_file = self.view.file_name() is not None
        self.origin = self.view.file_name() or self.view.name()

        name = basename(self.origin)
        default_untitled_name = f'untitled {random_string(6)}'

        self.window.show_input_panel(
            'Move To' if self.is_file else 'Rename To',
            name if name.strip() != '' else default_untitled_name,
            self.on_done,
            self.on_change,
            self.reset,
            )

    def move_file(self, url: str):
        path = self.completer.url2path(url)
        if path is None:
            path = path_join(dirname(self.origin), url)
        if isdir(path):
            path = path_join(path, basename(self.origin))
        path = normpath(path)

        should_rename = False
        if exists(path):
            resp = yes_no_cancel_dialog(
                '目标文件已存在，是否覆盖？',
                '覆盖',
                '重命名',
                'FileUtils: Move',
                )
            if resp == DIALOG_CANCEL:
                return
            if resp == DIALOG_NO:
                should_rename = True

        if should_rename:
            stem, ext = splitext(path)
            i = 1
            while True:
                path = f'{stem} ({i}){ext}'
                if not exists(path):
                    break
                i += 1

        try:
            rename(self.origin, path)
            self.view.retarget(path)
            status_message(f'{basename(self.origin)} moved to {self.completer.path2url(path)}')
        except Exception as e:
            status_message(f'failed to move: {e}')

    def rename_title(self, text: str):
        title = text.strip()
        if title != '':
            self.view.set_name(title)

    def edit_to(self, dst: str):
        src = self.this.text()
        while src != dst:
            matcher = SequenceMatcher(None, src, dst)
            diffs = matcher.get_opcodes()
            for tag, i1, i2, j1, j2 in diffs:
                if tag == 'delete':
                    self.this.select(i1, i2)
                    self.this.delete_sels()
                elif tag == 'insert':
                    self.this.set_pos(i1)
                    self.this.insert(dst[j1:j2])
                elif tag == 'replace':
                    self.this.select(i1, i2)
                    self.this.insert(dst[j1:j2])
                src = self.this.text()
                if tag != 'equal':
                    break

    def format_input_path(self, text: str):
        text, tab_at = tab_filter(text)
        if text.strip() == '' and tab_at != -1:
            text = basename(self.origin)
        else:
            text = self.completer.complete(dirname(self.origin), text, tab_at)
        return text

    def on_got_focus(self, state: PanelUtils.PanelEntry):
        that = self.window.active_panel()
        this, this_view = state
        if that != 'input' or this != that:
            PanelUtils.subscribe_panel_focus_event_once(self.on_got_focus)
            return

        self.this = ViewEdit(this_view)

        folders = self.window.project_data()['folders']
        self.completer.set_roots(map(lambda e: e.get('path'), folders))

        # add selection on stem
        stem, ext = splitext(self.last_edit)
        self.this.select(0, len(stem))

    def on_change(self, text: str):
        # input panel not become active yet
        if self.last_edit is None:
            self.last_edit = text
            PanelUtils.subscribe_panel_focus_event_once(self.on_got_focus)
            return

        if self.this is None:
            raise RuntimeError("failed to track view of input")

        # begin exclusive edit
        if self.modifiable:
            self.modifiable = False
        else:
            return

        if self.is_file:
            new_text = self.format_input_path(text)
            self.edit_to(new_text)

        # end edit
        self.last_edit = self.this.text()
        self.modifiable = True

    def on_done(self, text: str):
        if self.is_file:
            self.move_file(text)
        else:
            self.rename_title(text)
        self.reset()
