import os
import subprocess

IS_WINDOWS = os.name == 'nt'

BANNER_LINES = [
    " __  __      _              _     ",
    "|  \\/  |    | |            | |    ",
    "| \\  / |_  _| |_ ___   ___ | |___ ",
    "| |\\/| \\ \\/ / __/ _ \\ / _ \\| / __|",
    "| |  | |>  <| || (_) | (_) | \\__ \\",
    "|_|  |_/_/\\_\\\\__\\___/ \\___/|_|___/",
]

SUBTITLE = "Everything in one place"
VERSION  = "v0.1.0 by Mxt_e"


def clear():
    subprocess.run(["cmd", "/c", "cls"] if IS_WINDOWS else ["clear"], check=False)
