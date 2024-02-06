from .lib import Region, Edit, TextCommand
from .lib import status_message
from .lib import panel as PanelUtils
from typing import Optional

class PyEvalCommand(TextCommand):
    def run(self, edit: Edit):
        transform = lambda r: self.fmt2py(self.text_in_region(r))
        sources = list(map(transform, self.view.sel()))

        total = len(sources)
        if total == 0:
            return

        w = self.view.window()
        con = PanelUtils.console_view(w)
        if con is None or con.window() is None:
            PanelUtils.show_panel(w, 'console')
            PanelUtils.subscribe_panel_focus_event_once(self.revert_focus)

        failed = 0
        for source in sources:
            if source is None:
                failed += 1
                continue
            print('>>> ' + source.replace('\n', '\n... '))
            try:
                try:
                    print(eval(source))
                except SyntaxError as e:
                    exec(source)
            except Exception as e:
                failed += 1
                print(f'{type(e).__name__}: {e}')

        status_message(f'eval {total} times, {failed} failed')

    def revert_focus(self, state: PanelUtils.PanelEntry):
        panel, _ = state
        if panel != 'console':
            PanelUtils.subscribe_panel_focus_event_once(self.revert_focus)
        self.view.window().focus_view(self.view)

    def text_in_region(self, region: Region) -> str:
        regions = self.view.lines(region)
        region = Region(regions[0].begin(), regions[-1].end())
        return self.view.substr(region)

    def fmt2py(self, source: str) -> Optional[str]:
        src_lines = [s.rstrip() for s in source.split('\n')]
        indent = 0
        indent_char = '\0'
        for c in src_lines[0]:
            if c != ' ' and c != '\t':
                break
            if indent_char == '\0':
                indent_char = c
            elif indent_char != c:
                return None
            indent += 1
        for i, src_line in enumerate(src_lines):
            if len(src_line) - len(src_line.lstrip()) < indent:
                continue
            src_lines[i] = src_line[indent:]
        return '\n'.join(src_lines)
