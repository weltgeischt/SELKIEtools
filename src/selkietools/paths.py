from pathlib import Path
import os, yaml

PACKAGE_DIR = Path(__file__).resolve().parent        # .../SELKIEtools/src/selkietools
REPO_ROOT   = PACKAGE_DIR.parent.parent               # .../SELKIEtools
DEFAULT_SETTINGS_PATH = REPO_ROOT / "SETTINGS" / "PATHS" / "general_paths.yml"


def load_settings(pathpath=None):
    candidates = [
        pathpath,
        os.environ.get("SELKIE_SETTINGS"),
        DEFAULT_SETTINGS_PATH,
        Path.home() / ".selkietools" / "general_paths.yml",
    ]

    for c in candidates:
        if c and Path(c).expanduser().is_file():
            print('Using settings file',c)
            with open(Path(c).expanduser()) as f:
                return yaml.safe_load(f)
    raise FileNotFoundError(
        "No settings file found. Pass --pathpath, set SELKIE_SETTINGS, "
        f"or create {DEFAULT_SETTINGS_PATH}"
    )


def resolve_file(value, recid, datadir):
    """value is either an existing path, or a tag like 'lfp_dehum'."""
    if value is None:
        return None
    p = Path(value).expanduser()
    if p.is_file():
        return p                                   # explicit path given, use as-is
    if value in SUFFIXES:
        #print('issuff')
        candidate = Path(datadir) / f"{recid}__{SUFFIXES[value]}"
        #if candidate.is_file():
            #print('is_cand',candidate)
        return candidate
        # else: raise FileNotFoundError(
        #     f"No '{value}' file for {recid} in {datadir} "
        #     f"(expected {candidate.name}). Pass the path explicitly, "
        #     f"or create it first."
        # )
    raise FileNotFoundError(
        f"'{value}' is neither an existing file nor a known tag "
        f"({', '.join(SUFFIXES)})."
    )

def resolve_dict_fallbacks(pdict,args,key):
    '''key can be a single key or list of keys so you can retrieve several at once,
    arg is an argument object with key as attributes,\
    pdict: is a default dictionary.
    if args.key = default, the value will be retieved from the dictionary'''
    if type(key) == type([]):
        return [pdict.get(subkey) if getattr(args,subkey) == 'default' else getattr(args,subkey) for subkey in key]
    else:
        return pdict.get(key) if getattr(args,key) == 'default' else getattr(args,key)

