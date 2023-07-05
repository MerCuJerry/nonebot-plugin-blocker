import json
from pathlib import Path

DATA_PATH = Path.cwd() / "data" / "blocker"
if not DATA_PATH.exists():
    DATA_PATH.mkdir(parents=True)

BLOCKLIST_JSON_PATH = DATA_PATH / "blocklist.json"
if not BLOCKLIST_JSON_PATH.exists():
    BLOCKLIST_JSON_PATH.write_text("[0,0]", encoding="u8")

blocklist : list[int]

def add_blocker(gid: int):
    try:
        blocklist.index(gid)
    except ValueError:
        blocklist.append(gid)
    
def del_blocker(gid: int):
    blocklist.remove(gid)
    
def check_blocker(gid: int) -> bool:
    try:
        blocklist.index(gid)
    except ValueError:
        return False
    except:
        return False
    else:
        return True

def save_blocker_list():
    with BLOCKLIST_JSON_PATH.open('w', encoding='UTF-8') as file:
        json.dump(blocklist, file, ensure_ascii=False)
    
def load_blocker_list():
    global blocklist
    with BLOCKLIST_JSON_PATH.open('r', encoding='UTF-8') as file:
        blocklist=json.load(file)