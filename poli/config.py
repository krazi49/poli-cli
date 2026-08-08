"""Config file loading — ~/.config/poli/config.json"""
import json
import os

DEFAULTS = {"aur_depth_limit": 10, "colors": True, "makepkg_flags": "-sirc --noconfirm"}

def _path():
    return os.path.join(os.path.expanduser("~"), ".config", "poli", "config.json")

def load():
    cfg = dict(DEFAULTS)
    p = _path()
    if os.path.exists(p):
        try:
            with open(p) as f:
                cfg.update(json.load(f))
        except Exception:
            pass
    return cfg

def save(cfg):
    p = _path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        json.dump(cfg, f, indent=2)
