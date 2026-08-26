import os
import json
import urllib.request
import xml.etree.ElementTree as ET

MC_VERSION = "1.21.1"
NEOFORGE_VERSION = "21.1.72"

INSTANCE_DIR = "instance"
LIB_DIR = os.path.join(INSTANCE_DIR, "libraries")

def ensure(path):
    if not os.path.exists(path):
        os.makedirs(path)

def download(url, path):
    print(f"[DL] {url}")
    urllib.request.urlretrieve(url, path)
    print(f"[OK] -> {path}")

# -----------------------------
# 1. Préparation des dossiers
# -----------------------------
ensure(INSTANCE_DIR)
ensure(LIB_DIR)

# -----------------------------
# 2. Télécharger Minecraft
# -----------------------------
print("[INFO] Récupération du manifest Minecraft…")

VERSION_MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
manifest_path = os.path.join(INSTANCE_DIR, "version_manifest.json")
download(VERSION_MANIFEST, manifest_path)

with open(manifest_path, "r") as f:
    manifest = json.load(f)

version_url = next(v["url"] for v in manifest["versions"] if v["id"] == MC_VERSION)

version_manifest_path = os.path.join(INSTANCE_DIR, "version.json")
download(version_url, version_manifest_path)

with open(version_manifest_path, "r") as f:
    version_data = json.load(f)

client_url = version_data["downloads"]["client"]["url"]
minecraft_path = os.path.join(INSTANCE_DIR, "minecraft.jar")
download(client_url, minecraft_path)

# -----------------------------
# 3. Télécharger NeoForge universal (runtime)
# -----------------------------
print("[INFO] Téléchargement du runtime NeoForge…")

NEOFORGE_BASE = f"https://maven.neoforged.net/releases/net/neoforged/neoforge/{NEOFORGE_VERSION}/"

runtime_url = NEOFORGE_BASE + f"neoforge-{NEOFORGE_VERSION}-universal.jar"
runtime_path = os.path.join(INSTANCE_DIR, "neoforge.jar")
download(runtime_url, runtime_path)

# -----------------------------
# 4. Télécharger le POM NeoForge
# -----------------------------
pom_url = NEOFORGE_BASE + f"neoforge-{NEOFORGE_VERSION}.pom"
pom_path = os.path.join(INSTANCE_DIR, "neoforge.pom")
download(pom_url, pom_path)

# -----------------------------
# 5. Lire le POM et télécharger les libraries
# -----------------------------
print("[INFO] Téléchargement des libraries NeoForge…")

tree = ET.parse(pom_path)
root = tree.getroot()

ns = {"m": "http://maven.apache.org/POM/4.0.0"}

libs = []

for dep in root.findall("m:dependencies/m:dependency", ns):
    group = dep.find("m:groupId", ns).text.replace(".", "/")
    artifact = dep.find("m:artifactId", ns).text
    version = dep.find("m:version", ns).text

    lib_url = f"https://maven.neoforged.net/releases/{group}/{artifact}/{version}/{artifact}-{version}.jar"
    lib_path = os.path.join(LIB_DIR, f"{artifact}-{version}.jar")

    try:
        download(lib_url, lib_path)
        libs.append({"name": f"{artifact}-{version}.jar", "path": f"libraries/{artifact}-{version}.jar"})
    except:
        print(f"[WARN] Impossible de télécharger {artifact}-{version}.jar")

# -----------------------------
# 6. Générer libraries.json
# -----------------------------
with open(os.path.join(INSTANCE_DIR, "libraries.json"), "w") as f:
    json.dump(libs, f, indent=4)

# -----------------------------
# 7. Générer instance.json
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
