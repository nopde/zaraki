from colorama import Fore, Back, Style

class Console:
    INFO = " INFO "
    ERROR = " ERROR "
    APP = " APP "

    def __init__(self):
        self.logs = []

    @staticmethod
    def text(msg: str = "", prefix: str = "", text_color: str = Fore.RESET, back_color: str = Fore.RESET, prefix_text_color: str = Fore.RESET, prefix_back_color: str = Fore.RESET):
        return f"{prefix_text_color}{prefix_back_color}{prefix}{Style.RESET_ALL} {text_color}{back_color}{msg}{Style.RESET_ALL}"

    def save_logs(self):
        logs = "\r".join(self.logs)
        with open("latest.log", "w+", encoding="UTF-8") as file:
            file.write(logs)

    def save_log(self, log: str):
        self.logs.append(log)
        self.save_logs()

    def log(self, msg: str = "", prefix: str = "", text_color: str = Fore.RESET, back_color: str = Back.RESET, prefix_text_color: str = Fore.RESET, prefix_back_color: str = Back.RESET):
        print(Console.text(msg=msg, prefix=prefix, text_color=text_color, back_color=back_color, prefix_text_color=prefix_text_color, prefix_back_color=prefix_back_color))
        self.save_log(f"[{prefix}] {msg}")

    def info(self, msg: str):
        self.log(msg=msg, prefix=self.INFO, prefix_text_color=Fore.BLACK, prefix_back_color=Back.YELLOW)

    def error(self, msg: str, reason: str):
        print(Console.text(msg=f"{msg}: {Fore.LIGHTRED_EX}{reason}{Style.RESET_ALL}", prefix=self.ERROR, prefix_text_color=Fore.BLACK, prefix_back_color=Back.LIGHTRED_EX))
        self.save_log(f"[{self.ERROR}] {msg}: {reason}")

    def app(self, msg: str):
        self.log(msg=msg, prefix=self.APP, prefix_text_color=Fore.BLACK, prefix_back_color=Back.LIGHTCYAN_EX)

    def downloading(self, mod_name: str, mod_version: str):
        self.log(msg=f"{mod_name} v{mod_version}", prefix=" Downloading ", prefix_text_color=Fore.BLACK, prefix_back_color=Back.LIGHTBLUE_EX)

    def downloaded(self, mod_name: str, mod_version: str):
        self.log(msg=f"{mod_name} v{mod_version}", prefix=" Downloaded ", prefix_text_color=Fore.BLACK, prefix_back_color=Back.LIGHTYELLOW_EX)

    def installed(self, mod_name: str, mod_version: str):
        self.log(msg=f"{mod_name} v{mod_version}", prefix=" Installed ", prefix_text_color=Fore.BLACK, prefix_back_color=Back.GREEN)

console = Console()