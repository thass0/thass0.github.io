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

def is_valid_name(name: str) -> bool:
    if not name:
        return False
    if not (name[0].isalpha() or name[0] == '_'):
        return False
    return all(c.isalnum() or c == '_' for c in name[1:])


def extract_frontmatter(cont: str) -> Tuple[str, Dict[str, str]]:
    if not cont.startswith("---\n"):
        return (cont, {})

    end_idx = cont.find("\n---", 4)
    if end_idx == -1:
        raise Exception("Unterminated frontmatter")

    frontmatter = {}
    for line in cont[4:end_idx].splitlines():
        parts = line.split(": ", maxsplit=1)
        if len(parts) != 2:
            raise Exception(f"Malformed frontmatter line: {line!r}")
        name = parts[0].strip()
        value = parts[1].strip()
        if not is_valid_name(name):
            raise Exception(f"Invalid frontmatter variable name: {name!r}")
        frontmatter[name] = value

    return (cont[end_idx + 4:], frontmatter)


###########
# Layouts #
###########

def render_layout(layout: str, ignore_undefined=False, **variables: str) -> str:
    """Render a layout string by substituting variables and expanding quotes.

    Variables are referenced as {{ name }} and replaced with their value.
    Quoted blocks start with {{" and end with the first "}} encountered;
    their content is emitted verbatim without any parsing.
    """

    out = []
    i = 0
    while i < len(layout):
        if layout[i] == '{' and i + 1 < len(layout) and layout[i + 1] == '{':
            if i + 2 < len(layout) and layout[i + 2] == '"':
                end = layout.find('"}}', i + 3)
                if end == -1:
                    raise Exception('Unterminated quote block')
                out.append(layout[i + 3 : end])
                i = end + 3
            else:
                end = layout.find('}}', i + 2)
                if end == -1:
                    raise Exception('Unterminated variable block')
                name = layout[i + 2 : end].strip()
                if name not in variables:
                    if ignore_undefined:
                        out.append(layout[i : end + 2])
                        i = end + 2
                        continue
                    raise Exception(f'Undefined variable: {name!r}')
                if name not in variables:
                    raise Exception(f'Undefined variable: {name!r}')
                out.append(variables[name])
                i = end + 2
        else:
            out.append(layout[i])
            i += 1

    return ''.join(out)


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
        raise Exception("Circular dependency detected, topo sort failed")

    return sorted


def load_layouts(layouts_dir: Path) -> Dict[str, Tuple[str, str]]:
    raw_layouts = {}
    frontmatters = {}
    deps = {}
    layouts = {}

    for ent in layouts_dir.iterdir():
        if not ent.is_file():
            print(f"Layout '{ent}' is not a file, skipping ...")
            continue
        cont = ent.read_text(encoding="utf-8")
        cont, frontmatter = extract_frontmatter(cont)
        if (parent := frontmatter.get("layout")) is not None:
            del frontmatter["layout"]
        name = ent.stem
        deps[name] = parent
        raw_layouts[name] = cont
        frontmatters[name] = frontmatter

    # The topological sorting means the parent layout will already be completely
    # processed before the current layout is processed. This way we don't run into
    # dependency issues.
    for name in topo_sort(deps):
        parent_name = deps[name]
        if parent_name:
            layouts[name] = render_layout(layouts[parent_name], ignore_undefined=True, content=raw_layouts[name], **frontmatter)
        else:
            layouts[name] = raw_layouts[name]

    return layouts


#########
# Pages #
#########

def link_footnotes(md: str) -> str:
    md = re.sub(r"\[\^([^\]]+)\]:\s?", lambda m: f"<sup id=\"footnote-{m.group(1)}\"><a href=\"#footnode-back-{m.group(1)}\">{m.group(1)}</a></sup>: ", md)
    md = re.sub(r"\[\^([^\]]+)\]", lambda m: f"<sup id=\"footnode-back-{m.group(1)}\"><a href=\"#footnote-{m.group(1)}\">{m.group(1)}</a></sup>", md)
    return md


def md_to_html(name: str, md: str) -> str:
    start_time = perf_counter()
    md = link_footnotes(md)
    html = to_html(md, safe=False, smart=True)
    end_time = perf_counter()
    elapsed = end_time - start_time
    print(f"Converted {name} to HTML in {elapsed:.4f} second(s)")
    return html


def load_pages(pages_dir: Path) -> Dict[str, Tuple[str, str, Dict[str, str]]]:
    pages = {}
    for ent in pages_dir.iterdir():
        if not ent.is_file():
            for name, (cont, frontmatter) in load_pages(ent).items():
                pages[ent.name + '/' + name] = (cont, frontmatter)
        else:
            cont = ent.read_text(encoding="utf-8")
            cont, frontmatter = extract_frontmatter(cont)
            pages[ent.name] = (cont, frontmatter)
    return pages


def generate_redirect(redirect_from: str, redirect_to: str, out_dir: Path):
    redirect_html = (
        f'<!DOCTYPE html>\n'
        f'<html>\n'
        f'<head>\n'
        f'    <meta http-equiv="refresh" content="0; url={redirect_to}">\n'
        f'    <link rel="canonical" href="{redirect_to}">\n'
        f'</head>\n'
        f'<body>\n'
        f'    <p>If you are not redirected, <a href="{redirect_to}">click here</a>.</p>\n'
        f'</body>\n'
        f'</html>\n'
    )
    redirect_path = Path(redirect_from.strip("/"))
    if redirect_path.suffix:
        path = out_dir / redirect_path
    else:
        path = out_dir / redirect_path / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(redirect_html, encoding="utf-8")


########
# Main #
########

if __name__ == "__main__":
    start_time = perf_counter()
    layouts = load_layouts(Path("layouts/"))
    pages = load_pages(Path("pages/"))
    out_dir = Path("build/")

    run(["rm", "-rf", str(out_dir)], check=True)

    for name, (cont, frontmatter) in pages.items():
        output_path = out_dir / name
        if output_path.suffix == ".md":
            cont = md_to_html(name, cont)
            output_path = (out_dir / name).with_suffix(".html")
        if layout_name := frontmatter.pop("layout", None):
            cont = render_layout(layouts[layout_name], content=cont, **frontmatter)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(cont, encoding="utf-8")
        if redirect_from := frontmatter.pop("redirect_from", None):
            redirect_to = "/" + str(output_path.relative_to(out_dir))
            generate_redirect(redirect_from, redirect_to, out_dir)

    run(["cp", "-r", "public/", "build/"], check=True)

    end_time = perf_counter()
    elapsed = end_time - start_time
    print(f"Done generating after {elapsed:.4f} second(s)")

