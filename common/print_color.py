from colorama import Fore, Style


def print_green(content: str):
    print(Fore.GREEN + content)
    print(Style.RESET_ALL, end="")


def print_yellow(content: str):
    print(Fore.YELLOW + content)
    print(Style.RESET_ALL, end="")


def print_red(content: str):
    print(Fore.RED + content)
    print(Style.RESET_ALL, end="")
