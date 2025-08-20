import traceback
import glo

from colorama import Fore, Style
from config import is_debugging


def print_error(error):
    print(Fore.RED + f"Fail while {glo.job}" + Style.RESET_ALL)
    if is_debugging:
        print(Fore.RED + f"{error}" + Style.RESET_ALL)
        traceback.print_exc()