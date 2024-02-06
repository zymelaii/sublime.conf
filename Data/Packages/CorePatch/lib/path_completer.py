from .path import fmtpath, get_windows_drivers
from typing import Optional, Tuple, List, Iterator
from os import listdir
from os.path import normpath, basename, dirname, relpath
from os.path import splitext, isdir
from os.path import join as path_join

class PathCompleter:
    def __init__(self):
        self._roots: List[str] = []

    def set_roots(self, roots: Iterator[str]):
        self._roots = list(map(normpath, roots))

    def roots(self) -> List[str]:
        return list(map(basename, self._roots))

    def find_root(self, path: str) -> Optional[str]:
        satisfied = lambda root: path.lower().startswith(root.lower())
        return next((root for root in self._roots if satisfied(root)), None)

    def find_root_by_name(self, name: str) -> Optional[str]:
        satisfied = lambda root: basename(root.lower()) == name.lower()
        return next((root for root in self._roots if satisfied(root)), None)

    def path2url(self, path: str) -> str:
        path = dirname(normpath(path))
        root = self.find_root(path)
        if root is None:
            return fmtpath(path)
        else:
            rel_path = relpath(path, root)
            rel_path = fmtpath('' if rel_path == '.' else rel_path)
            return f':/{basename(root)}/{rel_path}'

    def url2path(self, url: str) -> Optional[str]:
        if url.startswith('/'):
            if url == '/':
                return None
            pos = url.find('/', 1)
            if pos != -1 and pos != 2:
                return None
            return normpath(f'{url[1]}:/{url[3:]}')
        if url.startswith(':/'):
            pos = url.find('/', 2)
            pos = len(url) if pos == -1 else pos
            folder = url[2:pos]
            for ws_folder in self._roots:
                if folder.lower() != basename(ws_folder).lower():
                    continue
                return normpath(path_join(dirname(ws_folder), url[2:]))
            return None
        return None

    def list_subdirs(self, path: str) -> List[str]:
        if not path.startswith('/'):
            return []
        if path == '/':
            return get_windows_drivers()
        end = path.find('/', 1)
        if end != -1 and end != 2:
            return []
        driver = path[1]
        path = normpath(f'{driver}:/{path[3:]}')
        if not isdir(path):
            return []
        try:
            satisfied = lambda d: isdir(path_join(path, d))
            return list(filter(satisfied, listdir(path)))
        except:
            return []

    def prefix_match(self, prefix: str, keys: List[str]) -> Tuple[int, bool]:
        index = -1
        total_matched = 0
        for i in range(len(keys)):
            if not keys[i].lower().startswith(prefix.lower()):
                continue
            if index == -1:
                index = i
            total_matched += 1
            if total_matched > 1:
                break
        if index == -1:
            return (-1, True)
        return (index, total_matched == 1)

    def complete_relpath(self, cwd: str, path: str, index: int) -> str:
        return path

    def complete(self, cwd: str, path: str, index: int) -> str:
        """
        RULES

        `$` is where the completion occurs

        1. <prefix>/<dir>$
            <subdir> := first subdir prefixed with <dir> under the <prefix>
            if not found <subdir>
                no completion
            if <subdir> eq <dir>
                complete `<dir>$` with `<subdir>/`
            if <subdir> is the single match
                complete `<dir>$` with `<subdir>/`
            otherwise
                complete `<dir>$` with `<subdir>`

        2. <prefix>/<dir>$/<suffix>
            <subdir> := first subdir prefixed with <dir> under the <prefix>
            <next-subdir> := subdir after <subdir>
            if not found <subdir>
                no completion
            if <subdir> eq <dir> and suffix is empty
                complete `<dir>$/<suffix>` with `<next-subdir>/`
            otherwise
                complete `<dir>$/<suffix>` with `<subdir>/`

        3. <prefix>/<dir-prefix>$<dir-suffix><suffix>
            <subdir> := first subdir prefixed with <dir-prefix> under the <prefix>
            if not found <subdir>
                no completion
            if <subdir> is the single matchr
                complete `<dir-prefix>$<dir-suffix><suffix>` with `<subdir>/`
            otherwise
                complete `<dir-prefix>$<dir-suffix>/<suffix>` with `<subdir>`
        """

        if index == -1 or path == '':
            return path

        if path == ':':
            return ':/'

        if not path.startswith('/') and not path.startswith(':/'):
            return self.complete_relpath(cwd, path, index)

        begin = path.rfind('/', 0, index)
        if begin == -1:
            return path
        begin += 1
        end = path.find('/', index)
        if end == -1:
            end = len(path)

        parent = path[:begin]
        dir_prefix = path[begin:index]
        dir_suffix = path[index:end]
        suffix = path[end:]

        subdirs = []

        # absolute path
        if path.startswith('/'):
            subdirs = self.list_subdirs(parent)

        # workspace path
        if path.startswith(':/'):
            if parent == ':/':
                subdirs = self.roots()
            else:
                prefix = self.url2path(parent)
                print(prefix)
                subdirs = self.list_subdirs(fmtpath(prefix))

        index, only_match = self.prefix_match(dir_prefix, subdirs)

        if index == -1:
            return path

        subdir = subdirs[index]

        # <prefix>/<dir-prefix>$<dir-suffix><suffix>
        if dir_suffix != '':
            if only_match:
                return f'{parent}{subdir}/'
            return f'{parent}{subdir}'

        # <prefix>/<dir>$
        if suffix == '':
            if subdir.lower() == dir_prefix.lower():
                return f'{parent}{subdir}/'
            if only_match:
                return f'{parent}{subdir}/'
            return f'{parent}{subdir}'

        # <prefix>/<dir>$/<suffix>
        if subdir.lower() == dir_prefix.lower() and suffix == '/':
            subdir = subdirs[(index + 1) % len(subdirs)]
        return f'{parent}{subdir}/'
