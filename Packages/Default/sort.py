import random

import sublime
import sublime_plugin


def permute_selection(f, v, e):
    regions = [s for s in v.sel() if not s.empty()]
    regions.sort()
    txt = [v.substr(s) for s in regions]
    txt = f(txt)

    # no sane way to handle this case
    if len(txt) != len(regions):
        return

    # Do the replacement in reverse order, so the character offsets don't get
    # invalidated
    combined = list(zip(regions, txt))
    combined.sort(key=lambda x: x[0], reverse=True)

    for x in combined:
        [r, t] = x
        v.replace(e, r, t)


def case_insensitive_sort(txt):
    txt.sort(key=lambda x: x.lower())
    return txt


def case_sensitive_sort(txt):
    txt.sort()
    return txt


def reverse_list(l):
    l.reverse()
    return l


def shuffle_list(l):
    random.shuffle(l)
    return l


def uniquealise_list(l):
    table = {}
    res = []
    for x in l:
        if x not in table:
            table[x] = x
            res.append(x)
    return res


permute_funcs = {
    "reverse": reverse_list,
    "shuffle": shuffle_list,
    "unique": uniquealise_list,
}


def unique_selection(v, e):
    regions = [s for s in v.sel() if not s.empty()]
    regions.sort()

    dupregions = []
    table = {}
    for r in regions:
        txt = v.substr(r)
        if txt not in table:
            table[txt] = r
        else:
            dupregions.append(r)

    dupregions.reverse()
    for r in dupregions:
        v.erase(e, r)


def shrink_wrap_region(view, region):
    a, b = region.begin(), region.end()

    for a in range(a, b):
        if not view.substr(a).isspace():
            break

    for b in range(b - 1, a, -1):
        if not view.substr(b).isspace():
            b += 1
            break

    return sublime.Region(a, b)


def shrinkwrap_and_expand_non_empty_selections_to_entire_line(v):
    regions = []

    for sel in v.sel():
        if not sel.empty():
            regions.append(v.line(shrink_wrap_region(v, v.line(sel))))
            v.sel().subtract(sel)

    for r in regions:
        v.sel().add(r)

    return [s for s in v.sel() if not s.empty()]


def permute_lines(f, v, e):
    regions = shrinkwrap_and_expand_non_empty_selections_to_entire_line(v)

    if not regions:
        v.sel().add(sublime.Region(0, v.size()))
        regions = shrinkwrap_and_expand_non_empty_selections_to_entire_line(v)

    regions.sort(reverse=True)

    for r in regions:
        txt = v.substr(r)
        lines = txt.split('\n')
        lines = f(lines)

        v.replace(e, r, u"\n".join(lines))


def has_multiple_non_empty_selection_region(v):
    return len([s for s in v.sel() if not s.empty()]) > 1


class SortLinesCommand(sublime_plugin.TextCommand):
    def run(self, edit, case_sensitive=False, reverse=False, remove_duplicates=False):
        view = self.view

        if case_sensitive:
            permute_lines(case_sensitive_sort, view, edit)
        else:
            permute_lines(case_insensitive_sort, view, edit)

        if reverse:
            permute_lines(reverse_list, view, edit)

        if remove_duplicates:
            permute_lines(uniquealise_list, view, edit)


class SortSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit, case_sensitive=False, reverse=False, remove_duplicates=False):

        view = self.view

        permute_selection(
            case_sensitive_sort if case_sensitive else case_insensitive_sort,
            view, edit)

        if reverse:
            permute_selection(reverse_list, view, edit)

        if remove_duplicates:
            unique_selection(view, edit)

    def is_enabled(self, **kw):
        return has_multiple_non_empty_selection_region(self.view)


class PermuteLinesCommand(sublime_plugin.TextCommand):
    def run(self, edit, operation='shuffle'):
        permute_lines(permute_funcs[operation], self.view, edit)


class PermuteSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit, operation='shuffle'):
        view = self.view

        if operation == "reverse":
            permute_selection(reverse_list, view, edit)

        elif operation == "shuffle":
            permute_selection(shuffle_list, view, edit)

        elif operation == "unique":
            unique_selection(view, edit)

    def is_enabled(self, **kw):
        return has_multiple_non_empty_selection_region(self.view)
