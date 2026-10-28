"""Schema vs content validator for every Meilleurtaux story.

Flags: fields not declared in the schema (render but invisible in the editor),
option values not in the option list, bloks outside the whitelist, maximum
breaches, missing required fields, unpublished stories.
"""
from sb import api, all_pages

comps = {c["name"]: c for c in all_pages("/components/", "components")}
groups = {}
for c in comps.values():
    groups.setdefault(c.get("component_group_uuid"), set()).add(c["name"])
problems = []


def check(blok, where):
    name = blok.get("component")
    comp = comps.get(name)
    if not comp:
        problems.append(f"{where}: unknown component {name}")
        return
    schema = comp.get("schema") or {}
    for k, v in blok.items():
        if k in ("component", "_uid", "_editable") or k.startswith("_"):
            continue
        f = schema.get(k)
        if not f:
            problems.append(f"{where}/{name}: field '{k}' not in schema")
            continue
        t = f.get("type")
        if t == "option" and v not in ("", None) and v not in [o["value"] for o in f.get("options", [])]:
            problems.append(f"{where}/{name}.{k}: '{v}' not an option")
        if t == "bloks":
            allowed = set(f.get("component_whitelist") or [])
            for g in f.get("component_group_whitelist") or []:
                allowed |= groups.get(g, set())
            if f.get("maximum") and len(v or []) > int(f["maximum"]):
                problems.append(f"{where}/{name}.{k}: {len(v)} > max {f['maximum']}")
            for i, child in enumerate(v or []):
                if allowed and child.get("component") not in allowed:
                    problems.append(f"{where}/{name}.{k}[{i}]: {child.get('component')} not allowed")
                check(child, f"{where}/{name}.{k}[{i}]")
        if t == "text" and f.get("max_length") and isinstance(v, str) and len(v) > int(f["max_length"]):
            problems.append(f"{where}/{name}.{k}: longer than {f['max_length']}")
    for k, f in schema.items():
        if f.get("required") and not blok.get(k):
            problems.append(f"{where}/{name}: required '{k}' empty")


stories = [s for s in all_pages("/stories/?story_only=0", "stories") if not s.get("is_folder") and not s["full_slug"].startswith("_starter-template")]
for s in stories:
    full = api("GET", f"/stories/{s['id']}")["story"]
    if not full["published"] or full.get("unpublished_changes"):
        problems.append(f"{full['full_slug']}: not published / unpublished changes")
    check(full["content"], full["full_slug"])
print(len(stories), "stories checked")
print("\n".join(problems) or "no problems")
