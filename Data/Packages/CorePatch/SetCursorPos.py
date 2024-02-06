from .lib import Region, Edit, TextCommand

class SetCursorPosCommand(TextCommand):
    def run(self, edit: Edit, pos: int):
        self.view.sel().clear()
        self.view.sel().add(Region(pos, pos))
