import os
import json
import platform

from typing import TypedDict, List

class _SysConfig():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.pin = True
        self.vm_mode = True
        self.slow_mode = False
        self.slow_mode_time = 0.12


class TypeContent(TypedDict):
    note: str
    content: str


class _DataConfig():
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.save_path = self.get_save_path()

    def get_save_path(self):
        if platform.system() == 'Windows':
            return os.getenv('LOCALAPPDATA') + "\\Lazy_typewriter\\type_content.json"
        elif platform.system() == 'Darwin':
            return os.getenv('HOME') + "/Library/Application Support/Lazy_typewriter/type_content.json"
        else:
            return "type_content.json"

    # load type content from file
    def load_type_content(self) -> List[TypeContent]:
        try:
            with open(self.save_path, "r", encoding='utf-8') as f:
                type_content = json.load(f)
                return [TypeContent(note=tc['note'], content=tc['content']) for tc in type_content['data']['list']]
        except FileNotFoundError:
            return []

    # save type content to file
    def save_type_content(self, type_content: List[TypeContent]):
        if not os.path.exists(os.path.dirname(self.save_path)):
            os.makedirs(os.path.dirname(self.save_path))

        list_content = [{'note': tc['note'], 'content': tc['content']} for tc in type_content]
        with open(self.save_path, "w", encoding='utf-8') as f:
            json.dump({"data": {"list": list_content}}, f, ensure_ascii=False, indent=4)


sys_config = _SysConfig()
data_config = _DataConfig()
