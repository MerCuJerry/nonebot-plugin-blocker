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
    BLOCKLIST_JSON_PATH.write_text('{}',encoding='u8')

STATIC_FILE_PATH = Path(__file__).parent / "web" / "webpage"

MAIN_PAGE_PATH = STATIC_FILE_PATH / "main.html"

REPLY_JSON_PATH_OLD = DATA_PATH / "reply_config.json"

REPLY_JSON_PATH = DATA_PATH / "config.json"
if not REPLY_JSON_PATH.exists():
    REPLY_JSON_PATH.write_text('{}',encoding='u8')
    
reply_config_raw = {"reply_on": {"type": "text", "data": "在本群开启"}, "reply_off": {"type": "text", "data": "在本群关闭"}}

class PluginConfigModel(BaseModel):
    WEBUI_USERNAME: Optional[str] = Field(None, alias="blocker_webui_username")
    WEBUI_PASSWORD: Optional[str] = Field(None, alias="blocker_webui_password")
    
class ReplyModel(BaseModel):
    type: str
    data: Optional[str]

class ConfigSingleModel(BaseModel):
    command_on: Optional[str]
    command_off: Optional[str]
    reply_on: ReplyModel
    reply_off: ReplyModel
    
class ConfigModel(BaseModel):
    __root__: Dict[str,ConfigSingleModel]
    
def get_reply_config() -> dict:
    config = json.load(REPLY_JSON_PATH.open('r', encoding='u8'))
    if not isinstance(config, dict):
        config = {}
    return config

def save_reply_config(config_list: ConfigModel):
    REPLY_JSON_PATH.write_text(config_list.json(),encoding='u8')
    
def upgrade_config():
    if REPLY_JSON_PATH_OLD.exists():
        config_update = {}
        config_tmp = json.load(REPLY_JSON_PATH_OLD.open('r', encoding='u8'))
        if not isinstance(config_tmp, dict):
            REPLY_JSON_PATH_OLD.with_suffix(".delete")
            logger.warning("[Blocker]Old config is upgraded. please remove old config file")
            return
        for key, val in config_tmp.items():
            config_update_on={}
            config_update_off={}
            config_update_reply={}
            config_update_on["type"]=val["reply_on_type"]
            config_update_on["data"] = val["reply_on_content"]
            config_update_off["type"] = val["reply_off_type"]
            config_update_off["data"] = val["reply_off_content"]
            config_update_reply["reply_on"] = config_update_on
            config_update_reply["reply_off"] = config_update_off
            config_update_reply["command_on"] = val["command_on"]
            config_update_reply["command_off"] = val["command_off"]
            config_update[key] = config_update_reply
        save_reply_config(ConfigModel.parse_obj(config_update))
        REPLY_JSON_PATH_OLD.unlink()
        logger.warning("[Blocker]Old config is upgraded please remove old config file")
        return
        
class BlockerList:
    blocklist: dict = {}
    
    def __init__(self):
        self.blocklist = json.load(BLOCKLIST_JSON_PATH.open('r',encoding='u8'))
        if not isinstance(self.blocklist, dict):
            self.blocklist = {}
        
    def add_blocker(self,gid: int, uin: str):
        try:
            self.blocklist.get(uin).index(gid)
        except ValueError:
            self.blocklist.get(uin).append(gid)
        except AttributeError:
            return self.blocklist.setdefault(uin,[gid])
        
    def del_blocker(self,gid: int, uin: str):
        try:
            self.blocklist.get(uin).remove(gid)
        except:
            pass
        
    def check_blocker(self,gid: int, uin: str) -> bool:
        try:
            self.blocklist.get(uin).index(gid)
            return True
        except:
            return False

    def __del__(self):
        json.dump(self.blocklist,BLOCKLIST_JSON_PATH.open('w',encoding='u8'),ensure_ascii=False)
        
driver_config = get_driver().config
config = PluginConfigModel.parse_obj(driver_config.dict())