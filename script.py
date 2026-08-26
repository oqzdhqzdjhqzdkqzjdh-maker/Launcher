import os
import json
import hashlib

# Dossiers
DIRS = {
    "mods": {
        "needed": "mods/needed",
        "bonus": "mods/bonus"
    },
    "resourcepacks": {
        "needed": "resourcepacks/needed",
        "bonus": "resourcepacks/bonus"
    },
    "shaderpacks": {
        "needed": "shaderpacks/needed",
        "bonus": "shaderpacks/bonus"
    }
}

OUTPUT_FILE = "manifest.json"

def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def scan_category(category_name, paths):
    items = []

    # Obligatoires
    needed_dir = paths["needed"]
    if os.path.isdir(needed_dir):
        for file in os.listdir(needed_dir):
            if file.endswith(".jar") or file.endswith(".zip"):
                full_path = os.path.join(needed_dir, file)
                items.append({
                    "name": file,
                    "sha256": sha256_file(full_path),
                    "needed": True
                })

    # Bonus / facultatifs
    bonus_dir = paths["bonus"]
    if os.path.isdir(bonus_dir):
        for file in os.listdir(bonus_dir):
            if file.endswith(".jar") or file.endswith(".zip"):
                full_path = os.path.join(bonus_dir, file)
                items.append({
                    "name": file,
                    "sha256": sha256_file(full_path),
                    "needed": False
                })

    return items

def main():
    manifest = {
        "mods": [],
        "resourcepacks": [],
        "shaderpacks": []
    }

    for category, paths in DIRS.items():
        manifest[category] = scan_category(category, paths)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)

    print("✔ Manifest généré :", OUTPUT_FILE)
    print("✔ Mods :", len(manifest["mods"]))
    print("✔ Resourcepacks :", len(manifest["resourcepacks"]))
    print("✔ Shaderpacks :", len(manifest["shaderpacks"]))

if __name__ == "__main__":
    main()
