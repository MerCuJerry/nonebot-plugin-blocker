import json
from pathlib import Path

DATA_PATH = Path.cwd() / "data" / "blocker"
if not DATA_PATH.exists():
    DATA_PATH.mkdir(parents=True)

BLOCKLIST_JSON_PATH = DATA_PATH / "blocklist.json"
if not BLOCKLIST_JSON_PATH.exists():
    BLOCKLIST_JSON_PATH.write_text('[]',encoding='u8')

REPLY_JSON_PATH = DATA_PATH / "blocker_reply.json"
if not REPLY_JSON_PATH.exists():
    tmp_dict = {}
    tmp_dict['reply_on']={'type':'text','data':{'text':'在本群开启'}}
    tmp_dict['reply_off']={'type':'text','data':{'text':'在本群关闭'}}
    with REPLY_JSON_PATH.open('w', encoding='UTF-8') as file:
            json.dump(tmp_dict, file, ensure_ascii=False)

class BlockerList:
    blocker_reply : dict
    blocklist : list[int]

    def __init__(self):
        with BLOCKLIST_JSON_PATH.open('r', encoding='UTF-8') as file:
            self.blocklist = json.load(file)
        with REPLY_JSON_PATH.open('r', encoding='UTF-8') as file:
            self.blocker_reply = json.load(file)
            
    def get_on_reply(self):
        return self.blocker_reply['reply_on']['type'],self.blocker_reply['reply_on']['data']
    
    def get_off_reply(self):
        return self.blocker_reply['reply_off']['type'],self.blocker_reply['reply_off']['data']    
    
    def add_blocker(self,gid: int):
        try:
            self.blocklist.index(gid)
        except ValueError:
            self.blocklist.append(gid)
        
    def del_blocker(self,gid: int):
        try:
            self.blocklist.remove(gid)
        except ValueError:
            pass
        
    def check_blocker(self,gid: int) -> bool:
        try:
            self.blocklist.index(gid)
        except:
            return False
        else:
            return True

    def __del__(self):
        with BLOCKLIST_JSON_PATH.open('w', encoding='UTF-8') as file:
            json.dump(self.blocklist, file, ensure_ascii=False)