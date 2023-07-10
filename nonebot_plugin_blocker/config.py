import json
from pathlib import Path

DATA_PATH = Path.cwd() / "data" / "blocker"
if not DATA_PATH.exists():
    DATA_PATH.mkdir(parents=True)

BLOCKLIST_JSON_PATH = DATA_PATH / "blocklist.json"
if not BLOCKLIST_JSON_PATH.exists():
    BLOCKLIST_JSON_PATH.write_text('{}',encoding='u8')

REPLY_JSON_PATH = DATA_PATH / "blocker_reply.json"
if not REPLY_JSON_PATH.exists():
    tmp_dict = {}
    tmp_dict['reply_on']={'type':'text','data':{'text':'在本群开启'}}
    tmp_dict['reply_off']={'type':'text','data':{'text':'在本群关闭'}}
    with REPLY_JSON_PATH.open('w', encoding='UTF-8') as file:
            json.dump(tmp_dict, file, ensure_ascii=False)

class BlockerList:
    blocker_reply : dict
    blocklist : dict[str,list[int]]

    def __init__(self):
        with BLOCKLIST_JSON_PATH.open('r', encoding='UTF-8') as file:
            self.blocklist = json.load(file)
            if type(self.blocklist) != dict:
                self.blocklist = {}
        with REPLY_JSON_PATH.open('r', encoding='UTF-8') as file:
            self.blocker_reply = json.load(file)
            if type(self.blocker_reply) != dict:
                self.blocker_reply = {}
            
    def get_on_reply(self):
        try:
            return self.blocker_reply['reply_on']['type'], self.blocker_reply['reply_on']['data']
        except:
            return None, None
    
    def get_off_reply(self):
        try:
            return self.blocker_reply['reply_off']['type'], self.blocker_reply['reply_off']['data'] 
        except:
            return None, None 
    
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
        except ValueError:
            pass
        
    def check_blocker(self,gid: int, qid: int) -> bool:
        try:
            self.blocklist[str(qid)].index(gid)
        except:
            return False
        else:
            return True

    def __del__(self):
        with BLOCKLIST_JSON_PATH.open('w', encoding='UTF-8') as file:
            json.dump(self.blocklist, file, ensure_ascii=False)