from pydantic import BaseModel, Field, RootModel
from pathlib import Path
from typing import Dict, Optional, Set, Literal
from nonebot import logger, get_plugin_config
import asyncio


class PluginConfigModel(BaseModel):
    WEBUI_USERNAME: Optional[str] = Field(None, alias="blocker_webui_username")
    WEBUI_PASSWORD: Optional[str] = Field(None, alias="blocker_webui_password")
    data_path: Optional[str] = Field(None, alias="blocker_data_path")


config = get_plugin_config(PluginConfigModel)


DATA_PATH = (
    Path.cwd() / "data" / "blocker"
    if config.data_path is None
    else Path(config.data_path)
)
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


class ReplyModel(BaseModel):
    type: Literal["text", "image", "record"]
    data: Optional[str]


class ConfigSingleModel(BaseModel):
    blocker_type: bool = False  # False 黑名单 True 白名单
    command_on: Optional[str]
    command_off: Optional[str]
    reply_on: ReplyModel
    reply_off: ReplyModel


class ConfigModel(RootModel):
    root: Dict[str, ConfigSingleModel]


class ReplyConfig:
    config: dict

    def __init__(self):
        self.config = ConfigModel.model_validate_json(
            REPLY_JSON_PATH.read_text(encoding="u8")
        ).model_dump()

    def save_config(self):
        REPLY_JSON_PATH.write_text(
            ConfigModel.model_validate(self.config).model_dump_json(indent=4),
            encoding="u8",
        )


reply_config = ReplyConfig()


class BlockerListModel(RootModel):
    root: Dict[str, Set[int]]


class BlockerList:
    blocklist: dict
    blocker_type: dict[str, bool]

    def __init__(self, reply_config: dict):
        self.blocklist = BlockerListModel.model_validate_json(
            BLOCKLIST_JSON_PATH.read_text(encoding="u8")
        ).model_dump()
        self.blocker_type = {
            uin: var.get("blocker_type", False) for uin, var in reply_config.items()
        }

    def add_blocker(self, gid: int, uin: str):
        try:
            self.blocklist.get(uin).add(gid)
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

    async def __call__(self, gid: int, uin: str, module_name: str) -> bool:
        if "nonebot_plugin_blocker" in module_name:
            return False
        return (gid in self.blocklist.get(uin)) ^ self.blocker_type.get(uin, False)

    async def save_blocker(self):
        try:
            BLOCKLIST_JSON_PATH.write_text(
                BlockerListModel.model_validate(self.blocklist).model_dump_json(
                    indent=4
                ),
                encoding="u8",
            )
            logger.info("[Blocker]Save Blocker Successful.")
        except:
            logger.info("[Blocker]Save Blocker Failed.")

    def __del__(self):
        asyncio.get_running_loop().create_task(self.save_blocker())
