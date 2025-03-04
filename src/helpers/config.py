import configparser
import sys
import os
from dotenv import load_dotenv


def resource_path(file_name: str = ''):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, file_name)
    elif os.path.exists(file_name):
        return file_name
    else:
        return os.getcwd() + '/' + file_name


class NoneDict(dict):
    def __getitem__(self, key):
        return dict.get(self, key)


class Config:
    DEFAULT_CONFIG_FILE = "app.properties"
    ENV_FILE = ".env"
    dict: NoneDict

    def __init__(self, file_name: str = ''):
        config = configparser.RawConfigParser()
        config.optionxform = lambda option: option

        config_file_name = file_name or self.DEFAULT_CONFIG_FILE
        config_file_path = resource_path(config_file_name)
        config.read(config_file_path)

        def get_config_section():
            if not hasattr(get_config_section, 'section_dict'):
                get_config_section.section_dict = dict()

                for section in config.sections():
                    get_config_section.section_dict[section] = NoneDict(dict(config.items(section)))

            return get_config_section.section_dict

        self.dict = NoneDict(get_config_section())

        env_file_name = self.ENV_FILE
        env_file_path = resource_path(env_file_name)
        load_dotenv(dotenv_path=env_file_path)

