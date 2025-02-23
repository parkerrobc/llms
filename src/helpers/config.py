import configparser
import sys
import os


class Config:
    CONFIG_FILE = "app.properties"

    def __init__(self):
        config = configparser.RawConfigParser()
        config.optionxform = lambda option: option

        path: str = ''

        if hasattr(sys, '_MEIPASS'):
            path = os.path.join(sys._MEIPASS, self.CONFIG_FILE)
        elif os.path.exists(self.CONFIG_FILE):
            path = self.CONFIG_FILE
        else:
            path = os.getcwd() + '/' + self.CONFIG_FILE

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
