import os
import json
import hashlib
import zipfile

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

def extract_metadata(path):
    version = "unknown"
    description = "No description"

    try:
        with zipfile.ZipFile(path, "r") as z:

            # NeoForge / Forge mods.toml
            if "META-INF/mods.toml" in z.namelist():
                raw = z.read("META-INF/mods.toml").decode("utf-8")
                for line in raw.splitlines():
                    if line.strip().startswith("version"):
                        version = line.split("=")[1].strip().replace('"', "")
                    if line.strip().startswith("description"):
                        description = line.split("=")[1].strip().replace('"', "")

            # Fabric mod metadata
            elif "fabric.mod.json" in z.namelist():
                data = json.loads(z.read("fabric.mod.json"))
                version = data.get("version", version)
                description = data.get("description", description)

            # Old Forge mcmod.info
            elif "mcmod.info" in z.namelist():
                data = json.loads(z.read("mcmod.info"))
                if isinstance(data, list) and len(data) > 0:
                    version = data[0].get("version", version)
                    description = data[0].get("description", description)

            # Resourcepacks / Shaderpacks pack.mcmeta
            elif "pack.mcmeta" in z.namelist():
                data = json.loads(z.read("pack.mcmeta"))
                pack = data.get("pack", {})
                description = pack.get("description", description)

    except Exception:
        pass

    return version, description

def scan_category(category_name, paths):
    items = []

    for needed_flag, folder in [("needed", paths["needed"]), ("bonus", paths["bonus"])]:
        if os.path.isdir(folder):
            for file in os.listdir(folder):
                if file.endswith(".jar") or file.endswith(".zip"):
                    full_path = os.path.join(folder, file)

                    version, description = extract_metadata(full_path)

                    items.append({
                        "name": file,
                        "sha256": sha256_file(full_path),
                        "size": os.path.getsize(full_path),
                        "version": version,
                        "description": description,
                        "needed": (needed_flag == "needed")
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
