import sys
import PySimpleGUI as sg

from pathlib import Path
from json import dump, load
from json.decoder import JSONDecodeError
from .settings import template
from collections import UserDict
from .helper import resources, get_musics, root, music_dir


class Music:
    _music_path = None
    _music_selected = ""
    _music_enabled = False

    def __init__(self, data):
        self.data = data
        self.musics = get_musics()
        self.init()

    def init(self):
        self.music_selected = self.data['music_selected']
        self.music_enabled = self.data['enabled']

    @property
    def music_enabled(self):
        return self._music_enabled

    @music_enabled.setter
    def music_enabled(self, value):
        if value:
            value = bool(self.musics and self.music_selected)
        self._music_enabled = value

    @property
    def music_path(self):
        return self._music_path

    @property
    def music_selected(self):
        return self._music_selected

    @music_selected.setter
    def music_selected(self, value: str):
        if value not in self.musics:
            value = ""
        self._music_selected = value
        self._music_path = music_dir / value

    def refresh_musics(self):
        self.musics = get_musics()

    def update(self, music_name):
        self.music_selected = music_name

    def rollback(self):
        self.init()

    def save(self):
        self.data.update({
            'enabled': self.music_enabled,
            'music_selected': self.music_selected
        })
        return self.data


class Configure(UserDict):
    def __init__(self):
        super().__init__(None)
        self.path = root / 'settings.json'
        self.raw_data = Configure._try_load(self.path)
        self['music'] = Music(self.raw_data['music'])

    @staticmethod
    def _save(path, data):
        with open(path, 'w', encoding='utf-8') as f:
            dump(data, f, indent=4)

    @staticmethod
    def _try_load(path: Path):
        data = template
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    data = load(f)
                except JSONDecodeError:
                    sg.popup_error('配置文件损坏，请删除配置文件并重新启动程序', f'配置文件地址：{path}', title='连续复制-错误', font=('', 14))
                    sys.exit(1)
        else:
            Configure._save(path, template)
        return data

    def save(self):
        self.raw_data['music'] = self['music'].save()
        Configure._save(self.path, self.raw_data)

    def rollback(self):
        self['music'].rollback()


configure = Configure()
