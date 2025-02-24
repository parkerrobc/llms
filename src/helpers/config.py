import configparser
import sys
import os


class Config:
    DEFAULT_CONFIG_FILE = "app.properties"

    def __init__(self, path: str = ''):
        config = configparser.RawConfigParser()
        config.optionxform = lambda option: option

        file_name = path or self.DEFAULT_CONFIG_FILE

        if hasattr(sys, '_MEIPASS'):
            path = os.path.join(sys._MEIPASS, file_name)
        elif os.path.exists(file_name):
            path = file_name
        else:
            path = os.getcwd() + '/' + file_name

        config.read(path)

        def get_config_section():
            if not hasattr(get_config_section, 'section_dict'):
                get_config_section.section_dict = dict()

                for section in config.sections():
                    get_config_section.section_dict[section] = NoneDict(dict(config.items(section)))

            return get_config_section.section_dict

        self.dict = NoneDict(get_config_section())


class NoneDict(dict):
    def __getitem__(self, key):
        return dict.get(self, key)
