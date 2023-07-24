from nonebot import get_driver, logger, on_message
driver = get_driver()
if driver._adapters.get("OneBot V12"):
    from nonebot.adapters.onebot.v12 import GroupMessageEvent, MessageSegment, GROUP_ADMIN, GROUP_OWNER
else:
    from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment, GROUP_ADMIN, GROUP_OWNER

from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.message import run_preprocessor

import re
from .config import BlockerList, get_reply_config
from . import web

blockerlist: BlockerList
    
driver.server_app.mount("/blocker-webui", web.app, name="blocker-webui")
logger.info("[Blocker]WebUI is now listening on "
            f"<u><e>http://{driver.config.host}:{driver.config.port}/blocker-webui/</e></u>"
)

@driver.on_startup
async def load_blocker_on_start():
    global blockerlist
    blockerlist = BlockerList()

@driver.on_shutdown
async def save_blocker_on_shut():
    global blockerlist
    del blockerlist
    
def msg_checker(msg: str,uid: str) -> bool|None:
    try:
        reply_config = get_reply_config().get(uid)
        if re.match(reply_config.get("command_on")+'$', msg) is not None:
            return True
        elif re.match(reply_config.get("command_off")+'$', msg) is not None:
            return False
    except (AttributeError,KeyError,TypeError):
        if re.match('[.。]bot on\s?(|\[at:qq=\d+\])', msg) is not None:
            return True
        elif re.match('[.。]bot off\s?(|\[at:qq=\d+\])', msg) is not None:
            return False
    return None

async def msg_checker_rule(event: GroupMessageEvent, state: T_State) -> bool:
    if (event.get_plaintext().find('qq') != -1 and not event.is_tome()) or event.user_id == event.self_id:
        return False
    state['blocker_state'] = msg_checker(event.get_plaintext(), str(event.self_id))
    return True if state['blocker_state'] is not None else False
    
blocker = on_message(rule=msg_checker_rule, permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER, priority=2, block=True)

@run_preprocessor
async def blocker_hook(matcher: Matcher, event: GroupMessageEvent):
    if blockerlist.check_blocker(event.group_id, event.self_id) and msg_checker(event.get_plaintext(), str(event.self_id)) is None:
        logger.info('[Blocker]Your Message is Blocked By Blocker.')
        await matcher.finish()
        
@blocker.handle()
async def blocker_msg_handle(matcher: Matcher, event: GroupMessageEvent, state: T_State):
    reply_config = get_reply_config().get(str(event.self_id))
    if state['blocker_state']:
        blockerlist.del_blocker(event.group_id, event.self_id)
        logger.info('[Blocker]Delete Blocker Successful.')
        try:
            msg_type = reply_config.get("reply_on_type")
            msg_data = reply_config.get("reply_on_content")
            if msg_data == "":
                raise AttributeError
        except AttributeError:
            await matcher.finish('在本群开启')
    else:
        blockerlist.add_blocker(event.group_id, event.self_id)
        logger.info('[Blocker]Add Blocker Successful.')
        try:
            msg_type = reply_config.get("reply_off_type")
            msg_data = reply_config.get("reply_off_content")
            if msg_data == "":
                raise AttributeError
        except AttributeError:
            await matcher.finish('在本群开启')
    if msg_type == "text":
        await matcher.finish(msg_data)
    else:
        await matcher.finish(MessageSegment(type=msg_type, data={"file":msg_data}))
