# This generator uses the CommonMark C reference implementation
# to convert Markdown into HTML. The CommonMark Python bindings
# need to be installed in order to use this generator:
#
# pip install paka.cmark
#

from pathlib import Path
from typing import Dict, Tuple, List
from subprocess import run
from time import perf_counter
from paka.cmark import to_html
import re

def die(msg: str):
    import sys
    print("Error:", msg, file=sys.stderr)
    sys.exit(1)

def extract_frontmatter(cont: str) -> Tuple[str, Dict[str, str]]:
    if not cont.startswith("---\n"):
        return (cont, {})
    end_idx = cont.find("\n---", 4) # End of the front matter
    front_matter = { k: v for k, v in (map(str.strip, line.split(": ", maxsplit=1)) for line in cont[4:end_idx].splitlines()) }
    return (cont[end_idx + 4:], front_matter)

###########
# Layouts #
###########

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

########
# Site #
########

def link_footnotes(md: str) -> str:
    md = re.sub(r"\[\^([^\]]+)\]:\s?", lambda m: f"<sup id=\"footnote-{m.group(1)}\"><a href=\"#footnode-back-{m.group(1)}\">{m.group(1)}</a></sup>: ", md)
    md = re.sub(r"\[\^([^\]]+)\]", lambda m: f"<sup id=\"footnode-back-{m.group(1)}\"><a href=\"#footnote-{m.group(1)}\">{m.group(1)}</a></sup>", md)
    return md

def md_to_html(name: str, md: str) -> str:
    start_time = perf_counter()
    md = link_footnotes(md)
    html = to_html(md, safe=False)
    end_time = perf_counter()
    elapsed = end_time - start_time
    print(f"Converted {name}.md to HTML in {elapsed:.4f} second(s)")
    return html

def load_src(src_dir: Path) -> Dict[str, Tuple[str, str, Dict[str, str]]]:
    src = {}
    for ent in src_dir.iterdir():
        if not ent.is_file():
            for name, (cont, suffix, front_matter) in load_src(ent).items():
                src[ent.stem + "/" + name] = (cont, suffix, front_matter)
        else:
            cont = ent.read_text(encoding="utf-8")
            cont, front_matter = extract_frontmatter(cont)
            src[ent.stem] = (cont, ent.suffix, front_matter)
    return src

if __name__ == "__main__":
    start_time = perf_counter()
    layouts = preload_layouts(Path("layouts/"))
    src = load_src(Path("site/"))
    out_dir = Path("build/")

    run(["rm", "-rf", str(out_dir)], check=True)

    for name, (cont, suffix, front_matter) in src.items():
        if suffix == ".md":
            cont = md_to_html(name, cont)
        if front_matter.get("layout") in layouts:
            layout = layouts[front_matter["layout"]]
            cont = layout[0] + cont + layout[1]
        output_path = (out_dir / name).with_suffix(".html")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(cont, encoding="utf-8")

    run(["cp", "-r", "public/", "build/"], check=True)

    end_time = perf_counter()
    elapsed = end_time - start_time
    print(f"Done generating after {elapsed:.4f} second(s)")
