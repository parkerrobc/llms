import json
import shutil
import sys
import os
from collections import OrderedDict
from pathlib import Path
from dotenv import load_dotenv

PROFILE_DIR = Path.home()
USER_CONFIG_DIR = os.path.join(PROFILE_DIR, '.llms')

if not os.path.exists(USER_CONFIG_DIR):
    os.makedirs(USER_CONFIG_DIR)

DEFAULT_CONF_FILE = 'app.json'
ENV_FILE = '.env'


def resource_path(file_name: str = ''):
    if os.path.exists(os.path.join(USER_CONFIG_DIR, file_name)):
        return os.path.join(USER_CONFIG_DIR, file_name)
    elif (hasattr(sys, '_MEIPASS')
            and os.path.exists(os.path.join(sys._MEIPASS, file_name))):
        return os.path.join(sys._MEIPASS, file_name)
    elif os.path.exists(file_name):
        return file_name
    else:
        return os.getcwd() + '/' + file_name


class ConfigLoader(OrderedDict):
    def __init__(self):
        super().__init__()
        load_dotenv(dotenv_path=resource_path(ENV_FILE))

    def __load_conf(self, conf_name: str = '') -> None:
        file = resource_path(f'{conf_name}.json')

        if not os.path.exists(file):
            conf_text = f' for {conf_name}' if conf_name and conf_name != '-' else ''
            print(f'*** configuration{conf_text} not found. loading default {DEFAULT_CONF_FILE} ***\n')
            file = resource_path(DEFAULT_CONF_FILE)

        with open(file, 'r') as f:
            conf = json.load(f)

        self.__setitem__(conf_name, conf)

    def load(self, conf_name: str = '') -> dict:
        if conf_name not in self.__dict__.keys():
            self.__load_conf(conf_name)

        return self.__getitem__(conf_name)


def add_update_conf(file: str) -> None:
    if not os.path.exists(file):
        file = os.path.join(os.getcwd(), file)

    if not os.path.exists(file):
        print('File not found', file)
        sys.exit(1)

    file_name = os.path.basename(file)
    shutil.copy(file, os.path.join(USER_CONFIG_DIR, file_name))


def view_user_conf() -> list[str]:
    if not os.path.exists(USER_CONFIG_DIR):
        print('No user configurations exist')
        sys.exit(1)

    files = os.listdir(USER_CONFIG_DIR)

    file_names = [os.path.splitext(file)[0] for file in files]

    return file_names

