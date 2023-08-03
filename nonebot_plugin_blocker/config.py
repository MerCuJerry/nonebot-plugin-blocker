from pydantic import BaseModel, Field
from pathlib import Path
from typing import Dict, Optional
from nonebot import get_driver, logger
import asyncio
import json

DATA_PATH = Path.cwd() / "data" / "blocker"
if not DATA_PATH.exists():
    DATA_PATH.mkdir(parents=True)

BLOCKLIST_JSON_PATH = DATA_PATH / "blocklist.json"
if not BLOCKLIST_JSON_PATH.exists():
    BLOCKLIST_JSON_PATH.write_text("{}", encoding="u8")

STATIC_FILE_PATH = Path(__file__).parent / "web" / "webpage"

MAIN_PAGE_PATH = STATIC_FILE_PATH / "main.html"

REPLY_JSON_PATH = DATA_PATH / "config.json"
if not REPLY_JSON_PATH.exists():
    REPLY_JSON_PATH.write_text("{}", encoding="u8")

reply_config_raw = {
    "reply_on": {"type": "text", "data": "在本群开启"},
    "reply_off": {"type": "text", "data": "在本群关闭"},
}


class JsonEncoder(json.JSONEncoder):
    sort_keys = True
    indent = 4
    ensure_ascii = False

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class PluginConfigModel(BaseModel):
    WEBUI_USERNAME: Optional[str] = Field(None, alias="blocker_webui_username")
    WEBUI_PASSWORD: Optional[str] = Field(None, alias="blocker_webui_password")


class ReplyModel(BaseModel):
    type: str
    data: Optional[str]


class ConfigSingleModel(BaseModel):
    blocker_type: bool = False  # False 黑名单 True 白名单
    command_on: Optional[str]
    command_off: Optional[str]
    reply_on: ReplyModel
    reply_off: ReplyModel


class ConfigModel(BaseModel):
    __root__: Dict[str, ConfigSingleModel]


def get_reply_config() -> dict:
    config = json.load(REPLY_JSON_PATH.open("r", encoding="u8"))
    if not isinstance(config, dict):
        config = {}
    return config


def save_reply_config(config_list: ConfigModel):
    REPLY_JSON_PATH.write_text(
        config_list.json(sort_keys=True, indent=4), encoding="u8"
    )


class BlockerList:
    blocklist: dict[str, set[int]] = {}
    blocker_type: dict[str, bool] = {}

    def __init__(self):
        raw_list = json.load(BLOCKLIST_JSON_PATH.open("r", encoding="u8"))
        config = get_reply_config()
        if not isinstance(raw_list, dict):
            raw_list = {}
        self.blocklist = {uin: set(val) for uin, val in raw_list.items()}
        self.blocker_type = {
            uin: val.get("blocker_type", False) for uin, val in config.items()
        }

    def add_blocker(self, gid: int, uin: str):
        try:
            self.blocklist.get(uin).add(gid)
            logger.info("[Blocker]Add Blocker Successful.")
        except AttributeError:
            self.blocklist.setdefault(uin, set([gid]))
            logger.info("[Blocker]Add Blocker Successful.")
        except:
            logger.info("[Blocker]Add Blocker Failed.")

    def del_blocker(self, gid: int, uin: str):
        try:
            self.blocklist.get(uin).remove(gid)
            logger.info("[Blocker]Delete Blocker Successful.")
        except (AttributeError, KeyError):
            logger.info("[Blocker]Delete Blocker Failed.")

    def change_blocker_type(self, uin: str, val: bool = False):
        try:
            self.blocker_type[uin] = val
        except KeyError:
            self.blocker_type.setdefault(uin, val)

    def __call__(self, gid: int, uin: str, module_name: str) -> bool:
        if "nonebot_plugin_blocker" in module_name:
            return False
        return (gid in self.blocklist.get(uin)) ^ self.blocker_type.get(uin, False)

    async def save_blocker(self):
        try:
            BLOCKLIST_JSON_PATH.write_text(JsonEncoder().encode(self.blocklist))
            logger.info("[Blocker]Save Blocker Successful.")
        except:
            logger.info("[Blocker]Save Blocker Failed.")

    def __del__(self):
        asyncio.get_running_loop().create_task(self.save_blocker())


config = PluginConfigModel.parse_obj(get_driver().config.dict())
