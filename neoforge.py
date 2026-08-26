import os
import json
import urllib.request
import zipfile
import shutil

MC_VERSION = "1.21.1"
NEOFORGE_VERSION = "21.1.72"

INSTANCE_DIR = "instance"
LIB_DIR = os.path.join(INSTANCE_DIR, "libraries")

def download(url, path):
    print(f"[DL] {url}")
    urllib.request.urlretrieve(url, path)
    print(f"[OK] -> {path}")

def ensure(path):
    if not os.path.exists(path):
        os.makedirs(path)

# -----------------------------
# 1. Préparation des dossiers
# -----------------------------
ensure(INSTANCE_DIR)
ensure(LIB_DIR)

# -----------------------------
# 2. Récupération du manifest Mojang
# -----------------------------
print("[INFO] Récupération du manifest Minecraft…")

VERSION_MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
manifest_path = os.path.join(INSTANCE_DIR, "version_manifest.json")
download(VERSION_MANIFEST, manifest_path)

with open(manifest_path, "r") as f:
    manifest = json.load(f)

version_url = None
for v in manifest["versions"]:
    if v["id"] == MC_VERSION:
        version_url = v["url"]
        break

if not version_url:
    raise Exception("Version Minecraft introuvable dans le manifest officiel.")

# -----------------------------
# 3. Récupération du manifest de la version
# -----------------------------
version_manifest_path = os.path.join(INSTANCE_DIR, "version.json")
download(version_url, version_manifest_path)

with open(version_manifest_path, "r") as f:
    version_data = json.load(f)

client_url = version_data["downloads"]["client"]["url"]

# -----------------------------
# 4. Téléchargement du client Minecraft
# -----------------------------
mc_path = os.path.join(INSTANCE_DIR, "minecraft.jar")
download(client_url, mc_path)

# -----------------------------
# 5. Téléchargement du NeoForge installer
# -----------------------------
installer_url = f"https://maven.neoforged.net/releases/net/neoforged/neoforge/{NEOFORGE_VERSION}/neoforge-{NEOFORGE_VERSION}-installer.jar"
installer_path = os.path.join(INSTANCE_DIR, "neoforge-installer.jar")
download(installer_url, installer_path)

# -----------------------------
# 6. Extraction des libs NeoForge
# -----------------------------
print("[INFO] Extraction des libs NeoForge…")

installer_extract = os.path.join(INSTANCE_DIR, "installer")
ensure(installer_extract)

with zipfile.ZipFile(installer_path, "r") as z:
    z.extractall(installer_extract)

installer_libs = os.path.join(installer_extract, "libraries")

for root, dirs, files in os.walk(installer_libs):
    for file in files:
        shutil.copy(os.path.join(root, file), os.path.join(LIB_DIR, file))

# -----------------------------
# 7. Extraction du neoforge.jar
# -----------------------------
print("[INFO] Extraction du neoforge.jar…")

with zipfile.ZipFile(installer_path, "r") as z:
    for name in z.namelist():
        if name.endswith("neoforge.jar"):
            z.extract(name, INSTANCE_DIR)
            os.rename(os.path.join(INSTANCE_DIR, name), os.path.join(INSTANCE_DIR, "neoforge.jar"))
            break

# -----------------------------
# 8. Génération libraries.json
# -----------------------------
libs = [{"name": f, "path": f"libraries/{f}"} for f in os.listdir(LIB_DIR)]

with open(os.path.join(INSTANCE_DIR, "libraries.json"), "w") as f:
    json.dump(libs, f, indent=4)

# -----------------------------
# 9. Génération instance.json
# -----------------------------
instance_json = {
    "minecraftVersion": MC_VERSION,
    "loader": "NeoForge",
    "mainClass": "net.minecraft.client.main.Main",

    "client": "minecraft.jar",
    "loaderJar": "neoforge.jar",

    "paths": {
        "libraries": "libraries/",
        "mods": "../mods/",
        "resourcepacks": "../resourcepacks/",
        "shaderpacks": "../shaderpacks/"
    },

    "remote": {
        "base": "https://raw.githubusercontent.com/oqzdhqzdjhqzdkqzjdh-maker/Launcher/main/"
    }
}

with open(os.path.join(INSTANCE_DIR, "instance.json"), "w") as f:
    json.dump(instance_json, f, indent=4)

print("\n✔ Instance NeoForge 1.21.1 générée avec succès.")
print("✔ minecraft.jar OK")
print("✔ neoforge.jar OK")
print("✔ libraries OK")
print("✔ libraries.json OK")
print("✔ instance.json OK")
