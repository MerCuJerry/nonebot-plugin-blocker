from pathlib import Path
from typing import Literal

from nonebot import get_plugin_config, logger, require
from pydantic import BaseModel, Field, RootModel

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store

OLD_DATA_PATH = Path.cwd() / "data" / "blocker"

plugin_config_dir: Path = store.get_plugin_config_dir()
CONFIG_PATH = plugin_config_dir

class BlockerPluginConfigModel(BaseModel):
    WEBUI_USERNAME: str | None = Field(None, alias="blocker_webui_username")
    WEBUI_PASSWORD: str | None = Field(None, alias="blocker_webui_password")
    OLD_DATA_PATH: Path = Field(OLD_DATA_PATH, alias="blocker_data_path")


config = get_plugin_config(BlockerPluginConfigModel)


if config.OLD_DATA_PATH.exists():
    for file in config.OLD_DATA_PATH.iterdir():
        if file.is_file():
            file.rename(CONFIG_PATH / file.name)

BLOCKLIST_JSON_PATH = store.get_plugin_config_file("blocklist.json")
if not BLOCKLIST_JSON_PATH.exists():
    BLOCKLIST_JSON_PATH.write_text("{}", encoding="u8")

STATIC_FILE_PATH = Path(__file__).parent / "web" / "webpage"

MAIN_PAGE_PATH = STATIC_FILE_PATH / "main.html"

REPLY_JSON_PATH = store.get_plugin_config_file("config.json")
if not REPLY_JSON_PATH.exists():
    REPLY_JSON_PATH.write_text("{}", encoding="u8")


reply_config_raw = {
    "reply_on": {"type": "text", "data": "在本群开启"},
    "reply_off": {"type": "text", "data": "在本群关闭"},
}


class ReplyModel(BaseModel):
    type: Literal["text", "image", "record"]
    data: str | None


class ConfigSingleModel(BaseModel):
    blocker_type: bool = False  # False 黑名单 True 白名单
    command_on: str | None
    command_off: str | None
    reply_on: ReplyModel
    reply_off: ReplyModel


class ConfigModel(RootModel):
    root: dict[str, ConfigSingleModel]


class ReplyConfig:
    config: dict

    def __init__(self):
        self.config = ConfigModel.model_validate_json(
            REPLY_JSON_PATH.read_text(encoding="u8")
        ).model_dump()

    async def save_config(self):
        REPLY_JSON_PATH.write_text(
            ConfigModel.model_validate(self.config).model_dump_json(indent=4),
            encoding="u8",
        )


reply_config = ReplyConfig()


class BlockerListModel(RootModel):
    root: dict[str, set[int]]


class BlockerList:
    blocklist: dict
    blocker_type: dict

    def __init__(self, reply_config: dict):
        self.blocklist = BlockerListModel.model_validate_json(
            BLOCKLIST_JSON_PATH.read_text(encoding="u8")
        ).model_dump()
        self.blocker_type = {
            uin: var.get("blocker_type", False) for uin, var in reply_config.items()
        }

    async def __call__(self, gid: int, uin: str, module_name: str) -> bool:
        if "nonebot_plugin_blocker" in module_name:
            return False
        return (gid in self.blocklist.get(uin)) ^ self.blocker_type.get(uin, False)

    async def add_blocker(self, gid: int, uin: str):
        try:
            self.blocklist.get(uin).add(gid)
            logger.info("[Blocker]Add Blocker Successful.")
        except AttributeError:
            self.blocklist.setdefault(uin, {gid})
            logger.info("[Blocker]Add Blocker Successful.")

    async def del_blocker(self, gid: int, uin: str):
        try:
            self.blocklist.get(uin).remove(gid)
            logger.info("[Blocker]Delete Blocker Successful.")
        except (KeyError, AttributeError):
            logger.info("[Blocker]Delete Blocker Successful.")

    async def change_blocker_type(self, uin: str, val: bool = False):
        try:
            self.blocker_type[uin] = val
        except KeyError:
            self.blocker_type.setdefault(uin, val)
            
    async def save_blocker(self):
        BLOCKLIST_JSON_PATH.write_text(
            BlockerListModel.model_validate(self.blocklist).model_dump_json(indent=4),
            encoding="u8",
        )
        logger.info("[Blocker]Save Blocker Successful.")

blockerlist = BlockerList(reply_config.config)