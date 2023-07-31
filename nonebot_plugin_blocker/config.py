from pydantic import BaseModel, Field
from pathlib import Path
from typing import Dict, Optional
from nonebot import get_driver, logger
import json

DATA_PATH = Path.cwd() / "data" / "blocker"
if not DATA_PATH.exists():
    DATA_PATH.mkdir(parents=True)

BLOCKLIST_JSON_PATH = DATA_PATH / "blocklist.json"
if not BLOCKLIST_JSON_PATH.exists():
    BLOCKLIST_JSON_PATH.write_text("{}",encoding="u8")

STATIC_FILE_PATH = Path(__file__).parent / "web" / "webpage"

MAIN_PAGE_PATH = STATIC_FILE_PATH / "main.html"

REPLY_JSON_PATH = DATA_PATH / "config.json"
if not REPLY_JSON_PATH.exists():
    REPLY_JSON_PATH.write_text("{}",encoding="u8")
    
reply_config_raw = {"reply_on": {"type": "text", "data": "在本群开启"}, "reply_off": {"type": "text", "data": "在本群关闭"}}

class PluginConfigModel(BaseModel):
    WEBUI_USERNAME: Optional[str] = Field(None, alias="blocker_webui_username")
    WEBUI_PASSWORD: Optional[str] = Field(None, alias="blocker_webui_password")
    
class ReplyModel(BaseModel):
    type: str
    data: Optional[str]

class ConfigSingleModel(BaseModel):
    blocker_type: bool = False # False 黑名单 True 白名单
    command_on: Optional[str]
    command_off: Optional[str]
    reply_on: ReplyModel
    reply_off: ReplyModel
    
class ConfigModel(BaseModel):
    __root__: Dict[str,ConfigSingleModel]
    
def get_reply_config() -> dict:
    config = json.load(REPLY_JSON_PATH.open("r", encoding="u8"))
    if not isinstance(config, dict):
        config = {}
    return config

def save_reply_config(config_list: ConfigModel):
    REPLY_JSON_PATH.write_text(config_list.json(),encoding="u8")
        
class BlockerList:
    blocklist: dict[str, list[int]] = {}
    blocker_type: dict[str, bool] = {}
    
    def __init__(self):
        self.blocklist = json.load(BLOCKLIST_JSON_PATH.open("r",encoding="u8"))
        config = get_reply_config()
        if not isinstance(self.blocklist, dict):
            self.blocklist = {}
        for uin in self.blocklist.keys():
            this_blocker_type = config.get(uin, {}).get("blocker_type", False)
            self.blocker_type.setdefault(uin, this_blocker_type)
        
    def add_blocker(self,gid: int, uin: str):
        try:
            self.blocklist.get(uin).index(gid)
        except ValueError:
            self.blocklist.get(uin).append(gid)
        except AttributeError:
            self.blocklist.setdefault(uin,[gid])
        except:
            logger.info("[Blocker]Add Blocker Failed.")
            return
        logger.info("[Blocker]Add Blocker Successful.")
        
        
    def del_blocker(self,gid: int, uin: str):
        try:
            self.blocklist.get(uin).remove(gid)
            logger.info("[Blocker]Delete Blocker Successful.")
        except ValueError:
            logger.info("[Blocker]Delete Blocker Failed.")
    
    def change_blocker_type(self,uin: str, val: bool = False):
        try:
            self.blocker_type[uin] = val
        except KeyError:
            self.blocker_type.setdefault(uin, val)
        
    def check_blocker(self,gid: int, uin: str, module_name: str) -> bool:
        try: 
            module_name.index("nonebot_plugin_blocker")
            return False
        except ValueError:
            try:
                self.blocklist.get(uin).index(gid)
                return not self.blocker_type.get(uin, False)
            except ValueError:
                return self.blocker_type.get(uin, False)

    def __del__(self):
        json.dump(self.blocklist,BLOCKLIST_JSON_PATH.open("w",encoding="u8"),ensure_ascii=False)
        
driver_config = get_driver().config
config = PluginConfigModel.parse_obj(driver_config.dict())