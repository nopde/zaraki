import aiohttp
import zipfile
import os
import shutil
import json
import asyncio

from modules.shared_vars import shared_vars
from modules.console import console

class Mod:
    def __init__(self, name: str, author: str):
        self.name = name
        self.author = author
        self.folder_name = f"{author}-{name}"
        self.mod_folder = os.path.join(shared_vars.PLUGINS_FOLDER, self.folder_name)
        self.latest_version = None
        self.download_url = None
        self.is_updated = None
    def exists_locally(self):
        if os.path.exists(os.path.join(self.mod_folder, "manifest.json")):
            return True
        return False
    def get_local_version(self):
        with open(os.path.join(self.mod_folder, "manifest.json"), "r", encoding="utf-8-sig") as file:
            return json.load(file)["version_number"]
    async def fetch_info(self):
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://thunderstore.io/api/experimental/package/{self.author}/{self.name}/") as response:
                        if response.status == 200:
                            request = await response.json()
                            self.download_url = request["latest"]["download_url"]
                            self.latest_version = request["latest"]["version_number"]
                            if self.exists_locally():
                                if self.get_local_version() == self.latest_version:
                                    self.is_updated = True
                            break
            except (aiohttp.ClientResponseError, aiohttp.ClientOSError, aiohttp.ClientConnectorError):
                await asyncio.sleep(1)
            except Exception:
                break

class ModInstaller:
    @staticmethod
    async def download_mod(mod: Mod):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(mod.download_url) as response:
                    with open(os.path.join(shared_vars.TEMP_FOLDER, f"{mod.name}.zip"), "wb") as file:
                        file.write(await response.content.read())

                with zipfile.ZipFile(os.path.join(shared_vars.TEMP_FOLDER, f"{mod.name}.zip"), "r") as file:
                    file.extractall(os.path.join(shared_vars.TEMP_FOLDER, mod.folder_name))

                os.remove(os.path.join(shared_vars.TEMP_FOLDER, f"{mod.name}.zip"))

                console.downloaded(mod.name, mod.latest_version)
        except Exception as e:
            console.error(f"Error downloading {mod.name}", e)
    @staticmethod
    def count_files(folder: str):
        root_dirs = os.listdir(folder)
        file_count = 0
        for i in root_dirs:
            if os.path.isfile(os.path.join(folder, i)):
                file_count += 1
        return file_count
    def handle_bepinex(self, mod: Mod, root):
        if self.count_files(os.path.join(root, "BepInEx")) > 0:
            bepinex_dirs = os.listdir(os.path.join(root, "BepInEx"))
            blacklisted_files = ["CHANGELOG.md", "icon.png", "LICENSE", "manifest.json", "README.md"]
            for i in bepinex_dirs:
                if i in blacklisted_files:
                    os.remove(os.path.join(root, "BepInEx", i))
        if os.path.exists(os.path.join(root, "BepInEx", "plugins")):
            if self.count_files(os.path.join(root, "BepInEx", "plugins")) > 0 or not os.path.exists(os.path.join(root, "BepInEx", "plugins", mod.folder_name)):
                shutil.copytree(os.path.join(root, "BepInEx", "plugins"), mod.mod_folder, dirs_exist_ok=True)
                shutil.rmtree(os.path.join(root, "BepInEx", "plugins"))
        shutil.copytree(root, shared_vars.GAME_FOLDER, dirs_exist_ok=True)
    def handle_subfolder(self, mod: Mod, root, name):
        if os.path.exists(os.path.join(root, "plugins")):
            if self.count_files(os.path.join(root, "plugins")) > 0 or not os.path.exists(os.path.join(root, "plugins", mod.folder_name)):
                shutil.copytree(os.path.join(root, "plugins"), mod.mod_folder, dirs_exist_ok=True)
                shutil.rmtree(os.path.join(root, "plugins"))
        os.makedirs(os.path.join(shared_vars.BEPINEX_FOLDER, name), exist_ok=True)
        os.makedirs(os.path.join(root, name), exist_ok=True)
        shutil.copytree(os.path.join(root, name), os.path.join(shared_vars.BEPINEX_FOLDER, name), dirs_exist_ok=True)
    def handle_other(self, mod: Mod, root):
        root_dirs = [i.lower() for i in os.listdir(root)]

        if "bepinex" in root_dirs:
            self.handle_bepinex(mod, root)
        else:
            for i in root_dirs:
                if i in ["config", "core", "patchers", "plugins"]:
                    self.handle_subfolder(mod, root)
                elif os.path.isfile(os.path.join(root, i)):
                    shutil.move(os.path.join(root, i), os.path.join(mod.mod_folder, i))
    def extract_mod(self, mod: Mod):
        root = os.path.join(shared_vars.TEMP_FOLDER, mod.folder_name)
        root_dirs = os.listdir(root)
        root_dirs_lower = [i.lower() for i in root_dirs]

        os.makedirs(mod.mod_folder, exist_ok=True)
        
        for file_name in root_dirs:
            if os.path.isfile(os.path.join(root, file_name)) and file_name:
                shutil.move(os.path.join(root, file_name), os.path.join(mod.mod_folder, file_name))

        if "bepinex" in root_dirs_lower:
            self.handle_bepinex(mod, root)
        else:
            for i in root_dirs_lower:
                if i in ["config", "core", "patchers", "plugins"]:
                    self.handle_subfolder(mod, root, i)
                else:
                    if os.path.isdir(os.path.join(root, i)):
                        self.handle_other(mod, os.path.join(root, i))
    async def install_mod(self, mod: Mod):
        self.extract_mod(mod)
        console.installed(mod.name, mod.latest_version)