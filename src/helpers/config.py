import json
import shutil
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

PROFILE_DIR = Path.home()
USER_CONFIG_DIR = os.path.join(PROFILE_DIR, '.llms')

if not os.path.exists(USER_CONFIG_DIR):
    os.makedirs(USER_CONFIG_DIR)

DEFAULT_CONF_FILE = 'app.json'
ENV_FILE = '.env'


def __resource_path(file_name: str = ''):
    if os.path.exists(os.path.join(USER_CONFIG_DIR, file_name)):
        return os.path.join(USER_CONFIG_DIR, file_name)
    elif (hasattr(sys, '_MEIPASS')
            and os.path.exists(os.path.join(sys._MEIPASS, file_name))):
        return os.path.join(sys._MEIPASS, file_name)
    elif os.path.exists(file_name):
        return file_name
    else:
        return os.getcwd() + '/' + file_name


def load_env() -> None:
    load_dotenv(dotenv_path=__resource_path(ENV_FILE))


def load_conf(conf_name: str = '') -> dict:
    file = __resource_path(f'{conf_name}.json')

    if not os.path.exists(file):
        print(f'*** configuration {'for' + conf_name if conf_name else ''}'
              f'not found. loading default {DEFAULT_CONF_FILE} ***\n')
        file = __resource_path(DEFAULT_CONF_FILE)

    with open(file, 'r') as f:
        conf = json.load(f)

    return conf


def add_update_conf(file: str) -> None:
    if not os.path.exists(file):
        file = os.path.join(os.getcwd(), file)

    if not os.path.exists(file):
        print('File not found', file)
        sys.exit(1)

    file_name = os.path.basename(file)
    shutil.copy(file, os.path.join(USER_CONFIG_DIR, file_name))


def view_user_conf() -> [str]:
    if not os.path.exists(USER_CONFIG_DIR):
        print('No user configurations exist')
        sys.exit(1)

    files = os.listdir(USER_CONFIG_DIR)

    file_names = [os.path.splitext(file)[0] for file in files]

    return file_names

