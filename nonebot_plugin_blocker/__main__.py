from nonebot import get_driver
driver = get_driver()
if driver._adapters.get("OneBot V12"):
    from nonebot.adapters.onebot.v12 import Bot, GroupMessageEvent, MessageSegment, GROUP_ADMIN, GROUP_OWNER
else:
    from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, GROUP_ADMIN, GROUP_OWNER

from nonebot import on_regex, logger
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from .config import load_blocker_list, save_blocker_list, add_blocker, del_blocker, check_blocker
    
blocker = on_regex(r"^.bot (on|off)$",permission= GROUP_ADMIN | GROUP_OWNER ,priority=2)

@driver.on_startup
async def load_blocker_on_start():
    load_blocker_list()

@driver.on_shutdown
async def save_blocker_on_shut():
    save_blocker_list()

@run_preprocessor
async def blocker_hook(matcher: Matcher,event: GroupMessageEvent):
    if check_blocker(event.group_id) and event.get_plaintext().find('.bot') == -1:
        logger.info("[Blocker]Your Message is Blocked By Blocker.")
        await matcher.finish()
        
@blocker.handle()
async def blocker_msg_handle(matcher: Matcher,event: GroupMessageEvent):
    if event.get_plaintext().find('on') != -1:
        del_blocker(event.group_id)
        logger.info("[Blocker]Delete Blocker Successful.")
        await matcher.finish('在本群开启')
    elif event.get_plaintext().find('off') != -1:
        add_blocker(event.group_id)
        logger.info("[Blocker]Add Blocker Successful.")
        await matcher.finish('在本群关闭')
