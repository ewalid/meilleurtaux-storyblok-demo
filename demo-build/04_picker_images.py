"""Upload block screenshots (one PNG per component, named <component>.png) and set
them as the component's preview image in the block picker.

Usage: python3 04_picker_images.py <dir-with-pngs>
Screenshots come from the component library page (headless Chrome, header hidden).
"""
import os
import sys

from sb import api, all_pages
import importlib

assets = importlib.import_module("01_assets")


def main(folder):
    fid = assets.folder_id()
    comps = {c["name"]: c for c in all_pages("/components/", "components")}
    for f in sorted(os.listdir(folder)):
        name = f[:-4]
        if not f.endswith(".png") or name not in comps:
            continue
        a = assets.upload(os.path.join(folder, f), f"picker-{f}", fid, f"{name} preview")
        comp = comps[name]
        keep = {k: comp[k] for k in ("name", "schema", "display_name", "is_root", "is_nestable", "component_group_uuid",
                                     "icon", "color", "preview_field", "description", "preset_id") if k in comp}
        api("PUT", f"/components/{comp['id']}", {"component": {**keep, "image": a["filename"].replace("s3.amazonaws.com/", "")}})
        print("picker image", name)


if __name__ == "__main__":
    main(sys.argv[1])
