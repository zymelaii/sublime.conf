from . import View, Region, Edit, TextCommand
from typing import List

class ViewEdit(View):
    def __init__(self, view: View):
        super().__init__(view.view_id)

    def run(self, command: str, **kwargs):
        self.run_command(command, args=kwargs)

    def move_and_extend(self, forward: bool, extend: bool):
        self.run('move', by='characters', forward=forward, extend=extend)

    def move_to_and_extend(self, loc: str, extend: bool):
        if loc not in ['bof', 'bol', 'eof', 'eol']:
            return
        self.run('move_to', to=loc, extend=extend)

    def extend(self, offset: int):
        forward = offset >= 0
        for _ in range(abs(offset)):
            self.move_and_extend(forward, True)

    def move(self, offset: int):
        forward = offset >= 0
        for _ in range(abs(offset)):
            self.move_and_extend(forward, False)

    def move_to(self, loc: str):
        self.move_to_and_extend(loc, False)

    def extend_to(self, loc: str):
        self.move_to_and_extend(loc, True)

    def set_pos(self, pos: int):
        self.run('set_cursor_pos', pos=pos)

    def get_pos(self) -> List[int]:
        return list(map(lambda r: r.end(), self.sel()))

    def select(self, begin: int, end: int):
        self.set_pos(end)
        self.sel().add(Region(begin, end))

    def select_line(self):
        self.move_to('bol')
        self.extend_to('eol')

    def select_all(self):
        self.run('select_all')

    def delete(self, backward: bool):
        self.run('left_delete' if backward else 'right_delete')

    def delete_sels(self):
        if len(self.sel()) == 0:
            return
        if len(self.sel()) == 1:
            sel_from, sel_to = self.sel()[0]
            if sel_from == sel_to:
                return
        self.delete(True)

    def delete_line(self):
        self.select_line()
        self.delete_sels()

    def clear(self):
        self.select_all()
        self.delete(True)

    def insert(self, text: str):
        self.run('insert', characters=text)

    def text(self):
        return self.substr(Region(0, self.size()))
