from nonebot import get_driver
driver = get_driver()
if driver._adapters.get("OneBot V12"):
    from nonebot.adapters.onebot.v12 import GroupMessageEvent, MessageSegment, GROUP_ADMIN, GROUP_OWNER
else:
    from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment, GROUP_ADMIN, GROUP_OWNER

from nonebot.permission import SUPERUSER
from nonebot import logger, on_message
from nonebot.matcher import Matcher
import re
from nonebot.typing import T_State
from nonebot.message import run_preprocessor
from .config import BlockerList

blockerlist: BlockerList
blocker_trigger: dict
    
@driver.on_startup
async def load_blocker_on_start():
    global blockerlist, blocker_trigger
    blockerlist = BlockerList()
    try:
        blocker_trigger = get_driver().config.blocker_trigger
    except AttributeError:
        blocker_trigger = {}


@driver.on_shutdown
async def save_blocker_on_shut():
    global blockerlist
    del blockerlist
    
def msg_checker(msg: str,uid: str):
    try:
        if re.match(blocker_trigger[uid]['on']+'$', msg) is not None:
            return True, True
        elif re.match(blocker_trigger[uid]['off']+'$', msg) is not None:
            return True, False
    except (KeyError,TypeError):
        if re.match('[.。]bot (on|off)\s?(|\[at:qq=\d+\])', msg) is not None:
            if msg.find('on') != -1:
                return True, True
            elif msg.find('off') != -1:
                return True, False
    return False, False

async def msg_checker_rule(event: GroupMessageEvent, state: T_State) -> bool:
    if event.get_plaintext().find('qq') != -1 and not event.is_tome():
        return False
    if event.user_id == event.self_id:
        return False
    state['blocker_passthrough'], state['blocker_state'] = msg_checker(event.get_plaintext(), str(event.self_id))
    return state['blocker_passthrough']
    
blocker = on_message(rule=msg_checker_rule, permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER, priority=2, block=True)

@run_preprocessor
async def blocker_hook(matcher: Matcher, event: GroupMessageEvent):
    blocker_pass, tmp = msg_checker(event.get_plaintext(), str(event.self_id))
    if blockerlist.check_blocker(event.group_id, event.self_id) and not blocker_pass:
        logger.info('[Blocker]Your Message is Blocked By Blocker.')
        await matcher.finish()
        
@blocker.handle()
async def blocker_msg_handle(matcher: Matcher, event: GroupMessageEvent, state: T_State):
    if state['blocker_state']:
        msg_type, msg_data = blockerlist.get_on_reply()
        blockerlist.del_blocker(event.group_id, event.self_id)
        logger.info('[Blocker]Delete Blocker Successful.')
        if msg_type is None:
            await matcher.finish('在本群开启')
    else:
        msg_type, msg_data = blockerlist.get_off_reply()
        blockerlist.add_blocker(event.group_id, event.self_id)
        logger.info('[Blocker]Add Blocker Successful.')
        if msg_type is None:
            await matcher.finish('在本群关闭')
    await matcher.finish(MessageSegment(type=msg_type, data=msg_data))
