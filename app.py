from colorama import Fore, Back
from easygui import diropenbox
from requests import get
import os
import yaml
import shutil
import asyncio

from modules.mod import Mod, ModInstaller
from modules.console import console
from modules.shared_vars import shared_vars

class Zaraki:
    def __init__(self):
        self.mod_installer = ModInstaller()
        self.mod_list: list[Mod] = []
        self.mods_to_download: list[Mod] = []
    def get_game_path(self):
        while True:
            game_path = diropenbox("Select Lethal Company folder")
            if game_path:
                shared_vars.set_game_path(game_path)
                break
    def get_mod_list(self, offline: bool = False):
        if offline:
            with open("mods.yml", "r") as file:
                data = yaml.safe_load(file)
        else:
            data = yaml.safe_load(get("https://raw.githubusercontent.com/CaraMob323/Tobimods/main/mods.yml").text)
        
        for mod in data:
            self.mod_list.append(Mod(mod["displayName"], mod["authorName"]))

    async def check_mods(self):
        console.app("Checking mods")
        semaphore = asyncio.Semaphore(5)
        tasks = []
        for mod in self.mod_list:
            async with semaphore:
                tasks.append(asyncio.create_task(mod.fetch_info()))
        await asyncio.gather(*tasks)
        for mod in self.mod_list:
            if not mod.is_updated:
                self.mods_to_download.append(mod)
        if self.mods_to_download.__len__() > 0:
            console.info(f"Finished checking mods ({self.mods_to_download.__len__()} mods to update)")
        else:
            console.info(f"Mods already up-to-date.")
    async def handle_mods(self):
        if self.mods_to_download.__len__() > 0:
            console.app("Downloading mods")
            semaphore = asyncio.Semaphore(5)
            tasks = []
            for mod in self.mods_to_download:
                console.downloading(mod.name, mod.latest_version)
                async with semaphore:
                    tasks.append(asyncio.create_task(self.mod_installer.download_mod(mod)))
                await asyncio.gather(*tasks)

                tasks = []
                async with semaphore:
                    tasks.append(asyncio.create_task(self.mod_installer.install_mod(mod)))
                await asyncio.gather(*tasks)
            console.info(f"Installed {self.mods_to_download.__len__()} mods")
    def run(self):
        console.log(prefix=" ♕  LC-ModManager ", prefix_text_color=Fore.BLACK, prefix_back_color=Back.LIGHTMAGENTA_EX)

        self.get_game_path()

        os.makedirs(shared_vars.PLUGINS_FOLDER, exist_ok=True)
        os.makedirs(shared_vars.TEMP_FOLDER, exist_ok=True)

        self.get_mod_list()
        asyncio.run(self.check_mods())
        asyncio.run(self.handle_mods())

        shutil.rmtree(os.path.join(shared_vars.TEMP_FOLDER), ignore_errors=True)

        console.app("Finished")

def main():
    zaraki = Zaraki()

    zaraki.run()

if __name__ == "__main__":
    main()