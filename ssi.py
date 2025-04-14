#!/usr/bin/env python3
import requests, zipfile, io, os, shutil, sys

INDEX_URL = "https://raw.githubusercontent.com/YOUR-USERNAME/my-packages-repo/main/index.json"

def fetch_package_index():
    print("📦 Fetching package list...")
    res = requests.get(INDEX_URL)
    res.raise_for_status()
    return res.json()

def download_package(pkg_name, pkg_url):
    print(f"⬇️ Downloading {pkg_name}...")
    res = requests.get(pkg_url)
    res.raise_for_status()
    return io.BytesIO(res.content)

def install_package(pkg_name, pkg_data):
    temp_path = f"/tmp/{pkg_name}"
    os.makedirs(temp_path, exist_ok=True)

    with zipfile.ZipFile(pkg_data) as z:
        z.extractall(temp_path)

    print(f"⚙️ Installing to /usr/bin/ ...")
    for root, dirs, files in os.walk(temp_path):
        for file in files:
            src_file = os.path.join(root, file)
            dest_file = f"/usr/bin/{file}"
            shutil.copy2(src_file, dest_file)
            os.chmod(dest_file, 0o755)
            print(f"✅ Installed: {dest_file}")

    shutil.rmtree(temp_path)
    print(f"✅ {pkg_name} installation complete.")

def main():
    if len(sys.argv) != 2:
        print("❌ Usage: sudo installer <package-name>")
        return

    pkg_name = sys.argv[1]

    index = fetch_package_index()
    if pkg_name not in index:
        print(f"❌ Package '{pkg_name}' not found.")
        return

    pkg_url = index[pkg_name]["url"]
    pkg_data = download_package(pkg_name, pkg_url)
    install_package(pkg_name, pkg_data)

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("⚠️ Please run this script with sudo: `sudo installer <package-name>`")
        exit(1)
    main()
