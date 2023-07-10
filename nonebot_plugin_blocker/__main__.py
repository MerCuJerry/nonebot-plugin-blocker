from nonebot import get_driver
driver = get_driver()
if driver._adapters.get("OneBot V12"):
    from nonebot.adapters.onebot.v12 import GroupMessageEvent, MessageSegment, GROUP_ADMIN, GROUP_OWNER
else:
    from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment, GROUP_ADMIN, GROUP_OWNER

from nonebot.permission import SUPERUSER
from nonebot import on_regex, logger
from nonebot.matcher import Matcher
import re
from nonebot.message import run_preprocessor
from .config import BlockerList

blockerlist: BlockerList

blocker = on_regex(r"^[.。]bot (on|off)$",permission= GROUP_ADMIN | GROUP_OWNER | SUPERUSER, priority=2)

@driver.on_startup
async def load_blocker_on_start():
    global blockerlist
    blockerlist = BlockerList()

@driver.on_shutdown
async def save_blocker_on_shut():
    global blockerlist
    del blockerlist

@run_preprocessor
async def blocker_hook(matcher: Matcher,event: GroupMessageEvent):
    if blockerlist.check_blocker(event.group_id) and re.match('[.。]bot (on|off)',event.get_plaintext()) is None:
        logger.info("[Blocker]Your Message is Blocked By Blocker.")
        await matcher.finish()
        
@blocker.handle()
async def blocker_msg_handle(matcher: Matcher,event: GroupMessageEvent):
    if event.get_plaintext().find('on') != -1:
        msg_type , msg_data = blockerlist.get_on_reply()
        blockerlist.del_blocker(event.group_id)
        logger.info("[Blocker]Delete Blocker Successful.")
        await matcher.finish(MessageSegment(type=msg_type,data=msg_data))
    elif event.get_plaintext().find('off') != -1:
        msg_type , msg_data = blockerlist.get_off_reply()
        blockerlist.add_blocker(event.group_id)
        logger.info("[Blocker]Add Blocker Successful.")
        await matcher.finish(MessageSegment(type=msg_type,data=msg_data))
