from .lib import Edit, TextCommand

class QuickSelectCommand(TextCommand):
	def is_enabled(self) -> bool:
		return len(self.view.sel()) == 1

	def run(self, edit: Edit):
		sel = self.view.sel()[0]
		if sel.begin() == sel.end():
			sel = self.view.word(sel)
		text = self.view.substr(sel)
		result = self.view.find_all(text)
		self.view.sel().clear()
		self.view.sel().add_all(result)
