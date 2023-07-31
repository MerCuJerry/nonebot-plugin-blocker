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
from nonebot.exception import IgnoredException

import re
from .config import BlockerList, get_reply_config, reply_config_raw
from . import web

blockerlist: BlockerList
    
driver.server_app.mount("/blocker-webui", web.app, name="blocker-webui")

@driver.on_startup
async def load_blocker_on_start():
    global blockerlist
    blockerlist = BlockerList()
    logger.info("[Blocker]WebUI is now listening on "
                f"http://{driver.config.host}:{driver.config.port}/blocker-webui/")

@driver.on_shutdown
async def save_blocker_on_shut():
    global blockerlist
    del blockerlist
    
async def msg_checker_rule(event: GroupMessageEvent, state: T_State) -> bool:
    if (re.search("[at:qq=\d+]", event.get_plaintext()) and not event.is_tome()) or event.user_id == event.self_id:
        return False # 如果是骰子自己发的或者当发现at了任何人但不是骰子的时候不执行
    try:
        reply_config: dict = get_reply_config().get(str(event.self_id))
        if re.match(reply_config.get("command_on")+"$", event.get_plaintext()):
            state["blocker_state"] = "reply_on"
        elif re.match(reply_config.get("command_off")+"$", event.get_plaintext()):
            state["blocker_state"] = "reply_off"
        state["this_reply"] = reply_config.get(state["blocker_state"])
    except (AttributeError,KeyError,TypeError):
        if match := re.match("[.。]bot (on|off)\s?(|\[at:qq=\d+\])", event.get_plaintext()):
            state["blocker_state"] = "reply_"+match.group(1)
            state["this_reply"] = reply_config_raw.get(state["blocker_state"])
    return True if "blocker_state" in state else False
    
blocker = on_message(rule=msg_checker_rule, permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER, priority=1, block=True)

@run_preprocessor
async def blocker_hook(matcher: Matcher, event: GroupMessageEvent):
    if blockerlist.check_blocker(event.group_id, str(event.self_id), matcher.plugin_name):
        logger.info("[Blocker]Your Message is Blocked By Blocker.")
        raise IgnoredException("[Blocker]Matcher Blocked By Blocker")
        
@blocker.handle()
async def blocker_msg_handle(matcher: Matcher, event: GroupMessageEvent, state: T_State):
    assert state["this_reply"] and state["blocker_state"]
    msg_type = state["this_reply"].get("type")
    msg_data = state["this_reply"].get("data")
    if state["blocker_state"] == "reply_on":
        blockerlist.del_blocker(event.group_id, str(event.self_id))
        logger.info("[Blocker]Delete Blocker Successful.")
    else:
        blockerlist.add_blocker(event.group_id, str(event.self_id))
        logger.info("[Blocker]Add Blocker Successful.")
    if msg_type == "text":
        await matcher.finish(msg_data)
    else:
        await matcher.finish(MessageSegment(type=msg_type, data={"file":msg_data}))
