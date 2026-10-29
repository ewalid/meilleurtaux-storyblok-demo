"""Space roles for the governance beat (idempotent by role name).

MCP gap: the Storyblok MCP has no space-role operations, so this uses the Management API.
The workflow itself is created through the MCP (createWorkflow / createWorkflowStage).

- Marketing: creates and edits pages, offers and news; cannot publish.
- Conformité: reviews and publishes.
- Traduction NL: edits the Dutch version only (allowed_languages = nl).
"""
from sb import api

ROLES = [
    ("Marketing", "Crée et modifie les pages, offres et actualités. Ne publie pas : envoie en Conformité.",
     ["save_stories", "edit_image", "move_story", "view_composer"], []),
    ("Conformité", "Relit les contenus réglementés (crédit, assurance) et publie.",
     ["save_stories", "publish_stories", "edit_image", "move_story", "view_composer"], []),
    ("Traduction NL", "Traduit et relit la version néerlandaise uniquement.",
     ["save_stories", "view_composer"], ["nl"]),
]


def main():
    have = {r["role"]: r for r in api("GET", "/space_roles/")["space_roles"]}
    for name, subtitle, permissions, languages in ROLES:
        body = {"space_role": {"role": name, "subtitle": subtitle, "permissions": permissions,
                               "allowed_languages": languages, "allowed_paths": []}}
        if name in have:
            r = api("PUT", f"/space_roles/{have[name]['id']}", body)["space_role"]
            print("updated", name, r["id"], r.get("permissions"), r.get("allowed_languages"))
        else:
            r = api("POST", "/space_roles/", body)["space_role"]
            print("created", name, r["id"], r.get("permissions"), r.get("allowed_languages"))


if __name__ == "__main__":
    main()
