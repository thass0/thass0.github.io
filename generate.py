from pathlib import Path
from typing import Dict, Tuple, List
import sys
import re

def die(msg: str):
    print("Error:", msg, file=sys.stderr)
    sys.exit(1)

def extract_frontmatter(cont: str) -> Tuple[str, Dict[str, str]]:
    if not cont.startswith("---\n"):
        return (cont, {})
    end_idx = cont.find("\n---", 4) # End of the front matter
    front_matter = { k: v for k, v in (map(str.strip, line.split(": ", maxsplit=1)) for line in cont[4:end_idx].splitlines()) }
    return (cont[end_idx + 4:], front_matter)

def topo_sort(deps: Dict[str, str]) -> List[str]:
    dep_graph = {} # Map of nodes (the parent) to a set of nodes that depend on them (the children)
    no_deps = [] # Nodes that don't depend on any other keys
    for node, parent in deps.items():
        dep_graph.setdefault(node, set()) # Ensure key exists
        if parent:
            dep_graph.setdefault(parent, set()).add(node)
        else:
            no_deps.append(node)

    sorted = []

    while no_deps:
        current = no_deps.pop()
        sorted.append(current)

        for dependent in list(dep_graph.get(current, [])):
            dep_graph[current].remove(dependent)
            if not any(dependent in deps for deps in dep_graph.values()):
                no_deps.append(dependent)

    if any(dep_graph.values()):
        die("Circular dependency detected, topo sort failed")

    return sorted

def preload_layouts(layouts_dir: Path) -> Dict[str, Tuple[str, str]]:
    pattern = re.compile(r"\{\{\s*content\s*\}\}")
    layouts = {}
    deps = {}
    for layout in layouts_dir.iterdir():
        if not layout.is_file():
            print(f"Layout '{layout}' is not a file, skipping ...")
            continue
        cont = layout.read_text(encoding="utf-8")
        cont, front_matter = extract_frontmatter(cont)
        parts = pattern.split(cont, maxsplit=1)
        name = layout.stem
        if not len(parts) == 2:
            die(f"Layout '{name}' doesn't contain '{{ content }}' exactly once, invalid")
        deps[name] = front_matter.get("layout")
        layouts[name] = (parts[0], parts[1])

    sorted_layouts = topo_sort(deps)

    # The topological sorting means the parent layout will already be completely
    # processed before the current layout is procssed. This way we don't run into
    # dependency issues.
    for name in sorted_layouts:
        parent = deps[name]
        if parent:
            layouts[name] = (layouts[parent][0] + layouts[name][0], layouts[name][1] + layouts[parent][1])

    return layouts

if __name__ == "__main__":
    layouts = preload_layouts(Path("layouts/"))
    for name, (before, after) in layouts.items():
        print("Name:", name)
        print("Before:\n", before)
        print("After:\n", after)
        print()
