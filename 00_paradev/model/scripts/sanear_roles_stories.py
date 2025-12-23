#!/usr/bin/env python3
"""
GORE_OS Role Mapping & Story Sanitation
Mapea roles legacy USR-* a roles formales ROL-* y deriva profunctores inversos
"""

import os
import re
from pathlib import Path
from collections import defaultdict

ATOMS_DIR = Path("/Users/felixsanhueza/fx_felixiando/gore_os/00_paradev/model/atoms")
ROLES_DIR = ATOMS_DIR / "roles"
STORIES_DIR = ATOMS_DIR / "stories"
CAPS_DIR = ATOMS_DIR / "capabilities"


def get_field(file_path, field_name):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                match = re.match(rf'^{field_name}:\s*["\']?(.+?)["\']?\s*$', line)
                if match:
                    val = match.group(1).strip()
                    if val.lower() in ("null", "~", ""):
                        return None
                    return val
    except:
        pass
    return None


def get_urn(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if "urn:goreos:atom:" in line:
                    match = re.search(r'(urn:goreos:atom:[^\s"\']+)', line)
                    if match:
                        return match.group(1).strip()
    except:
        pass
    return None


def build_role_catalog():
    """Build catalog of all roles with their IDs and titles."""
    roles = {}  # id -> {title, urn, file}
    role_by_suffix = {}  # suffix -> id (for fuzzy matching)

    for f in ROLES_DIR.glob("*.yml"):
        rid = get_field(f, "id")
        title = get_field(f, "title")
        urn = get_urn(f)
        if rid:
            roles[rid] = {"title": title, "urn": urn, "file": f}
            # Extract suffix for fuzzy matching
            parts = rid.split("-")
            if len(parts) >= 2:
                suffix = parts[-1]
                role_by_suffix[suffix.upper()] = rid

    return roles, role_by_suffix


def build_capability_story_map():
    """Build reverse map from capability to stories."""
    cap_to_stories = defaultdict(list)
    story_to_cap = {}

    for f in CAPS_DIR.glob("*.yml"):
        cid = get_field(f, "id")
        if not cid:
            continue

        with open(f, "r", encoding="utf-8") as file:
            in_stories = False
            for line in file:
                if "stories:" in line:
                    in_stories = True
                    continue
                if in_stories:
                    if line.strip().startswith("-"):
                        sid = line.replace("-", "").strip().strip("'\"")
                        cap_to_stories[cid].append(sid)
                        story_to_cap[sid.upper()] = cid
                    elif not line.startswith(" ") and line.strip():
                        break

    return story_to_cap


def main():
    roles, role_suffix = build_role_catalog()
    story_to_cap = build_capability_story_map()

    # Legacy to formal role mapping (heuristic)
    legacy_map = {}
    unmapped = set()

    updates = {
        "role_fixed": 0,
        "cap_added": 0,
        "as_a_fixed": 0,
    }

    role_to_stories = defaultdict(list)  # For deriving actor_of

    for f in STORIES_DIR.glob("*.yml"):
        if f.name == "_index.yml":
            continue

        content = f.read_text(encoding="utf-8")
        original = content

        sid = get_field(f, "id")
        role_id = get_field(f, "role_id")
        cap_id = get_field(f, "capability_id")
        story_urn = get_urn(f)

        target_role = role_id

        # Try to map legacy role
        if role_id and role_id not in roles:
            # Try suffix match
            parts = role_id.split("-")
            if len(parts) >= 2:
                suffix = parts[-1].upper()
                if suffix in role_suffix:
                    target_role = role_suffix[suffix]
                    legacy_map[role_id] = target_role

        # Update role_id if mapped
        if target_role != role_id and target_role in roles:
            content = re.sub(
                rf"^role_id:\s*.*$",
                f"role_id: {target_role}",
                content,
                flags=re.MULTILINE,
            )
            updates["role_fixed"] += 1

        # Update as_a if role exists
        if target_role in roles:
            title = roles[target_role]["title"]
            if title:
                content = re.sub(
                    rf"^as_a:\s*.*$", f"as_a: {title}", content, flags=re.MULTILINE
                )
                updates["as_a_fixed"] += 1

            # Collect for actor_of derivation
            if story_urn:
                role_to_stories[target_role].append(story_urn)
        else:
            unmapped.add(role_id)

        # Add capability_id if missing but known
        if not cap_id and sid:
            lookup_sid = sid.upper().replace("-", "_")
            if lookup_sid in story_to_cap:
                new_cap = story_to_cap[lookup_sid]
                # Insert before priority or at end
                if "capability_id:" not in content:
                    content = re.sub(
                        r"^(priority:\s*)",
                        f"capability_id: {new_cap}\n\\1",
                        content,
                        flags=re.MULTILINE,
                    )
                    updates["cap_added"] += 1

        # Write if changed
        if content != original:
            f.write_text(content, encoding="utf-8")

    # Derive actor_of for roles
    print("Derivando profunctor actor_of en roles...")
    for rid, stories in role_to_stories.items():
        if rid not in roles:
            continue
        role_file = roles[rid]["file"]
        content = role_file.read_text(encoding="utf-8")

        # Build actor_of list
        stories_unique = sorted(set(stories))[:20]  # Cap at 20
        list_str = "  actor_of:\n"
        for s in stories_unique:
            list_str += f"    - {s}\n"

        # Replace existing actor_of or insert
        if "actor_of:" in content:
            content = re.sub(
                r"^\s*actor_of:\s*(\[\]|\n(\s*-.*\n)*)",
                list_str,
                content,
                flags=re.MULTILINE,
            )
        else:
            content = content.replace("morphisms:", f"morphisms:\n{list_str}")

        role_file.write_text(content, encoding="utf-8")

    print(f"\n=== RESUMEN DE SANEAMIENTO ===")
    print(f"Stories con role_id corregido: {updates['role_fixed']}")
    print(f"Stories con as_a corregido: {updates['as_a_fixed']}")
    print(f"Stories con capability_id añadido: {updates['cap_added']}")
    print(f"Roles únicos derivados (actor_of): {len(role_to_stories)}")
    print(f"\nRoles legacy sin mapear ({len(unmapped)}):")
    for r in sorted(unmapped)[:10]:
        print(f"  - {r}")


if __name__ == "__main__":
    main()
