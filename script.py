import os
import json
import hashlib
import zipfile

DIRS = {
    "mods": {
        "needed": "mods/needed",
        "bonus": "mods/bonus"
    }
}

OUTPUT_FILE = "manifest.json"

def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def extract_mixins_metadata(z):
    """Scan the jar for any *.mixins.json file."""
    for name in z.namelist():
        if name.lower().endswith(".mixins.json"):
            try:
                data = json.loads(z.read(name))
                modid = name.lower().replace(".mixins.json", "").split("/")[-1]
                return {
                    "package": data.get("package", ""),
                    "modid": modid,
                    "description": data.get("refmap", "").replace(".refmap.json", "")
                }
            except:
                continue
    return {"package": "", "modid": "", "description": ""}

def extract_metadata(path):
    version = "unknown"
    description = ""
    package = ""
    modid = ""
    displayName = ""
    authors = []

    try:
        with zipfile.ZipFile(path, "r") as z:
            names = z.namelist()

            # NeoForge 1.21.1 metadata
            if "META-INF/neoforge.mods.toml" in names:
                raw = z.read("META-INF/neoforge.mods.toml").decode("utf-8")
                for line in raw.splitlines():
                    line = line.strip()
                    if line.startswith("modId"):
                        modid = line.split("=")[1].strip().replace('"', "")
                    if line.startswith("displayName"):
                        displayName = line.split("=")[1].strip().replace('"', "")
                    if line.startswith("authors"):
                        authors = [line.split("=")[1].strip().replace('"', "")]
                    if line.startswith("version"):
                        version = line.split("=")[1].strip().replace('"', "")
                    if line.startswith("description"):
                        description = line.split("=")[1].strip().replace('"', "")

            # Forge / NeoForge older
            elif "META-INF/mods.toml" in names:
                raw = z.read("META-INF/mods.toml").decode("utf-8")
                for line in raw.splitlines():
                    line = line.strip()
                    if line.startswith("modId"):
                        modid = line.split("=")[1].strip().replace('"', "")
                    if line.startswith("displayName"):
                        displayName = line.split("=")[1].strip().replace('"', "")
                    if line.startswith("authors"):
                        authors = [line.split("=")[1].strip().replace('"', "")]
                    if line.startswith("version"):
                        version = line.split("=")[1].strip().replace('"', "")
                    if line.startswith("description"):
                        description = line.split("=")[1].strip().replace('"', "")

            # Fabric
            elif "fabric.mod.json" in names:
                data = json.loads(z.read("fabric.mod.json"))
                modid = data.get("id", modid)
                displayName = data.get("name", displayName)
                authors = data.get("authors", authors)
                version = data.get("version", version)
                description = data.get("description", description)

            # Old Forge
            elif "mcmod.info" in names:
                data = json.loads(z.read("mcmod.info"))
                if isinstance(data, list) and len(data) > 0:
                    modid = data[0].get("modid", modid)
                    displayName = data[0].get("name", displayName)
                    authors = data[0].get("authorList", authors)
                    version = data[0].get("version", version)
                    description = data[0].get("description", description)

            # Mixins JSON fallback
            mixin_meta = extract_mixins_metadata(z)
            if mixin_meta["package"]:
                package = mixin_meta["package"]
            if mixin_meta["modid"] and not modid:
                modid = mixin_meta["modid"]
            if mixin_meta["description"] and not description:
                description = mixin_meta["description"]

    except Exception:
        pass

    return version, description, package, modid, displayName, authors

def scan_mods():
    items = []

    for needed_flag, folder in [("needed", DIRS["mods"]["needed"]), ("bonus", DIRS["mods"]["bonus"])]:
        if os.path.isdir(folder):
            for file in os.listdir(folder):
                if file.endswith(".jar"):
                    full_path = os.path.join(folder, file)

                    version, description, package, modid, displayName, authors = extract_metadata(full_path)

                    items.append({
                        "name": file,
                        "sha256": sha256_file(full_path),
                        "size": os.path.getsize(full_path),
                        "version": version,
                        "package": package,
                        "description": description if description else "unknown",
                        "modid": modid,
                        "displayName": displayName,
                        "authors": authors,
                        "needed": (needed_flag == "needed")
                    })

    return items

def main():
    manifest = {
        "mods": scan_mods()
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)

    print("✔ Manifest généré :", OUTPUT_FILE)
    print("✔ Mods :", len(manifest["mods"]))

if __name__ == "__main__":
    main()
