from .lib import WindowCommand

class ClearConsoleCommand(WindowCommand):
    def run(self) -> None:
        print('\n' * 256)
