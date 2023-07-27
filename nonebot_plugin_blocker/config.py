import json
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Dict, Optional
from nonebot import get_driver

DATA_PATH = Path.cwd() / "data" / "blocker"
if not DATA_PATH.exists():
    DATA_PATH.mkdir(parents=True)

BLOCKLIST_JSON_PATH = DATA_PATH / "blocklist.json"
if not BLOCKLIST_JSON_PATH.exists():
    BLOCKLIST_JSON_PATH.write_text('{}',encoding='u8')

STATIC_FILE_PATH = Path(__file__).parent / "web" / "webpage"

MAIN_PAGE_PATH = STATIC_FILE_PATH / "main.html"

REPLY_JSON_PATH = DATA_PATH / "reply_config.json"
if not REPLY_JSON_PATH.exists():
    REPLY_JSON_PATH.write_text('{}',encoding='u8')

class PluginConfig(BaseModel):
    WEBUI_USERNAME: Optional[str] = Field(None, alias="blocker_webui_username")
    WEBUI_PASSWORD: Optional[str] = Field(None, alias="blocker_webui_password")

class ReplyConfigSingleModel(BaseModel):
    command_on: str|None = None
    command_off: str|None = None
    reply_on_type: str
    reply_on_content: str|None = None
    reply_off_type: str
    reply_off_content: str|None = None
    
class ReplyConfigModel(BaseModel):
    __root__: Dict[str,ReplyConfigSingleModel]
    
def get_reply_config() -> dict:
    config_list: dict = json.load(REPLY_JSON_PATH.open("r",encoding="u8"))
    if type(config_list) != dict:
        config_list = {}
    return config_list

def save_reply_config(config_list: dict):
    json.dump(config_list,REPLY_JSON_PATH.open("w",encoding="u8"),ensure_ascii=False)

class BlockerList:
    blocklist : dict[str,list[int]]

    def __init__(self):
        self.blocklist = json.load(BLOCKLIST_JSON_PATH.open('r', encoding='UTF-8'))
        if type(self.blocklist) != dict:
            self.blocklist = {}
    
    def add_blocker(self,gid: int, qid: int):
        try:
            self.blocklist[str(qid)].index(gid)
        except ValueError:
            self.blocklist[str(qid)].append(gid)
        except KeyError:
            self.blocklist.setdefault(str(qid),[gid])
        
    def del_blocker(self,gid: int, qid: int):
        try:
            self.blocklist[str(qid)].remove(gid)
        except:
            pass
        
    def check_blocker(self,gid: int, qid: int) -> bool:
        try:
            self.blocklist[str(qid)].index(gid)
            return True
        except:
            return False

    def __del__(self):
        json.dump(self.blocklist, BLOCKLIST_JSON_PATH.open('w', encoding='UTF-8'), ensure_ascii=False)
            
driver_config = get_driver().config
config = PluginConfig.parse_obj(driver_config.dict())