import typing
from pathlib import Path
import json


class Settings:
    __config_file_path: Path
    default_files_path: Path = None
    dpi: int = None

    def __init__(self):
        self.__config_file_path = Path('settings.json')
        if not self.__config_file_path.exists():
            self.__create_default_settings_file()
        else:
            self.load()

    def load(self, settings_file_path: Path = None):
        if settings_file_path is not None:
            self.__config_file_path = settings_file_path
        with open(self.__config_file_path, 'r', encoding='utf-8') as file:
            settings_data: dict = json.load(file)
            type_hints: dict = typing.get_type_hints(self)
            for key, value in settings_data.items():
                if not hasattr(self, key):
                    continue
                setattr(self, key, type_hints[key](value))

    def save(self, settings_file_path: Path = None):
        if settings_file_path is not None:
            self.__config_file_path = settings_file_path
        with open(self.__config_file_path, 'w', encoding='utf-8') as file:
            attrs: dict = self.__dict__
            json.dump(dict(filter(lambda i: False if i[0][0:1] == '_' else True, attrs.items())), file,
                      indent=4, default=lambda o: str(o))

    def __create_default_settings_file(self):
        self.__config_file_path = Path('settings.json')
        self.default_files_path = Path(Path.home())
        self.dpi = 300
        self.save()
