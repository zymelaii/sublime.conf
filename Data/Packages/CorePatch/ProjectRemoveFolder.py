from .lib import ListInputHandler, WindowCommand, ListInputItem
from .lib import KindId
from typing import Optional, Dict, Any, List
from os.path import basename

KIND_FOLDER = [KindId.COLOR_YELLOWISH, "📁", "Folder"]

def project_folders(project: Optional[Dict[str, Any]]) -> List[str]:
    return (project or {}).get("folders", [])

def display_name(folder: Dict[str, Any]) -> str:
    return folder.get("name") or basename(folder["path"])

def make_item(folder: Dict[str, Any]) -> ListInputItem:
    return ListInputItem(
        text=display_name(folder),
        annotation=folder["path"],
        value=folder["path"],
        kind=KIND_FOLDER,
        )

class FolderInputHandler(ListInputHandler):
    def __init__(self, folders):
        super().__init__()
        self.folders = folders

    def name(self):
        return "folder"

    def placeholder(self):
        return "Folder Name"

    def list_items(self):
        return list(map(make_item, self.folders))

class ProjectRemoveFolderCommand(WindowCommand):
    def is_enabled(self, folder: Optional[str] = None) -> bool:
        return project_folders(self.window.project_data()) is not None

    def is_visible(self, folder: Optional[str] = None) -> bool:
        return self.is_enabled(folder)

    def input(self, args: Dict[str, Any]) -> Optional[str]:
        if not args.get('folder'):
            folders = project_folders(self.window.project_data())
            if folders:
                return FolderInputHandler(folders)
        return None

    def input_description(self) -> str:
        return 'Remove'

    def run(self, folder: str):
        project = self.window.project_data()
        if not project:
            return None

        folders = project_folders(project)
        project['folders'] = list(filter(lambda d: d['path'] != folder, folders))

        self.window.set_project_data(project)
