'''
call with
cd ecephys_toolbox
python tools/update_readme.py
'''
import ast
from pathlib import Path
import ecetools

from ecetools.scripts_registry import SCRIPTS
from ecetools.file_registry import FILES
from ecetools.config_registry import CONFIGS

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_DIR = Path(ecetools.__file__).resolve().parent
README = REPO_ROOT / 'README.md'

MARKERS = {
    'COMMANDS': ('<!-- COMMANDS:START -->', '<!-- COMMANDS:END -->'),
    'FILETAGS': ('<!-- FILETAGS:START -->', '<!-- FILETAGS:END -->'),
    'CONFIGS': ('<!-- CONFIGS:START -->', '<!-- CONFIGS:END -->'),
}

def summary(path):
    doc = ast.get_docstring(ast.parse(path.read_text())) or ''
    return doc.strip().splitlines()[0] if doc.strip() else '(no description)'

# def _link_to_script(name):
#     rel = SCRIPTS[name]['path']
#     return (PACKAGE_DIR / rel).relative_to(REPO_ROOT).as_posix()

def _resolve_produces(text):
    '''Tagged outputs link to their row in the File tags table; free text passed through.'''
    if not text:
        return ''
    parts = [p.strip() for p in text.split(',')]
    return ', '.join(f'[`{p}`](#tag-{p})' if p in FILES else p for p in parts)

def _resolve_requires(text):
    '''Tagged requirements shown as plain code, no link.'''
    if not text:
        return ''
    parts = [p.strip() for p in text.split(',')]
    return ', '.join(f'`{p}`' if p in FILES else p for p in parts)

def build_commands_table():
    #needs to be run after build_filetags! otherwise the anchors wont work!
    rows = ['| Command | Produces | Requires | Description |', '|---|---|---|---|']
    for name, info in SCRIPTS.items():
        script_path = PACKAGE_DIR / info['path']
        link = script_path.relative_to(REPO_ROOT).as_posix()
        rows.append(
            f'| [`ecetools {name}`]({link}) '
            f'| {_resolve_produces(info.get('produces'))} '
            f'| {_resolve_requires(info.get('requires'))} '
            f'| {summary(script_path)} |'
        )
    return '\n'.join(rows)

# def build_filetags_table():
#     rows = ['| Tag | File | Produced by | Description |', '|---|---|---|---|']
#     for tag, info in FILES.items():
#         rows.append(
#             f'| `{tag}` | `<recid>__{info['suffix']}` '
#             f'| `ecetools {info['produced_by']}` | {info['description']} |'
#         )
#     return '\n'.join(rows)

def build_filetags_table():
    rows = ['| Tag | File | Produced by | Description |', '|---|---|---|---|']
    for tag, info in FILES.items():
        rows.append(
            f'| <a id=\'tag-{tag}\'></a>`{tag}` | `<nwbstem>__{info['suffix']}` '
            f'| `ecetools {info['produced_by']}` | {info['description']} |'
        )
    return '\n'.join(rows)

def replace_section(text, key, body):
    start, end = MARKERS[key]
    before, _, rest = text.partition(start)
    _, _, after = rest.partition(end)
    return f'{before}{start}\n{body}\n{end}{after}'

def build_configs_table():
    rows = ["| Tag | File | Used by | Description |", "|---|---|---|---|"]
    for tag, info in CONFIGS.items():
        cfg_link = f"SETTINGS/config/{info['filename']}"
        used_by = ", ".join(f"`ecephys {c}`" for c in info.get('used_by', [])) or "—"
        rows.append(
            f"| <a id=\"cfg-{tag}\"></a>`{tag}` | [`{info['filename']}`]({cfg_link}) "
            f"| {used_by} | {info['description']} |"
        )
    return "\n".join(rows)

def main():
    text = README.read_text()
    text = replace_section(text, 'FILETAGS', build_filetags_table())
    text = replace_section(text, 'COMMANDS', build_commands_table())
    text = replace_section(text, 'CONFIGS', build_configs_table())

    README.write_text(text)
    print('README.md updated.')

if __name__ == '__main__':
    main()