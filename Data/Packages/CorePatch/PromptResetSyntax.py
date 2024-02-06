from .lib import Syntax, QuickPanelItem, WindowCommand
from .lib import list_syntaxes

class PromptResetSyntaxCommand(WindowCommand):
    def fetch_and_sync(self):
        satisfied = lambda e: not e.hidden
        self.syntax_list = list(filter(satisfied, list_syntaxes()))

    def make_item(self, syntax: Syntax) -> QuickPanelItem:
        return QuickPanelItem(syntax.name, '', syntax.scope)

    def run(self):
        self.fetch_and_sync()
        syntaxes = list(map(self.make_item, self.syntax_list))
        self.window.show_quick_panel(syntaxes, self.reset_syntax)

    def reset_syntax(self, index: int):
        view = self.window.active_view()
        if index == -1 or view is None:
            return
        view.assign_syntax(self.syntax_list[index])
