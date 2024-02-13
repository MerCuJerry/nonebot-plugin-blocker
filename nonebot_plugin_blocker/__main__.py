from nonebot import get_driver, logger, on_message
from nonebot.drivers import ReverseDriver
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    MessageSegment,
    GROUP_ADMIN,
    GROUP_OWNER,
)
from nonebot.permission import SUPERUSER
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.message import run_preprocessor
from nonebot.exception import IgnoredException
import re
from .config import BlockerList, reply_config_raw, reply_config
from fastapi import FastAPI
from . import web

driver = get_driver()

blockerlist: BlockerList


@driver.on_startup
async def load_blocker_on_start():
    global blockerlist
    blockerlist = BlockerList(reply_config.config)
    if isinstance(driver, ReverseDriver) and isinstance(driver.server_app, FastAPI):
        driver.server_app.mount("/blocker-webui", web.app, name="blocker-webui")
        logger.info(
            "[Blocker]WebUI is now listening on "
            f"http://{driver.config.host}:{driver.config.port}/blocker-webui/"
        )
    else:
        logger.info("[Blocker]WebUI only support FastAPI reverse driver.")


@driver.on_shutdown
async def save_blocker_on_shut():
    global blockerlist
    del blockerlist


async def msg_checker_rule(event: GroupMessageEvent, state: T_State) -> bool:
    if (
        ("at" in event.get_message()) and (not event.is_tome())
    ) or event.user_id == event.self_id:
        return False  # 如果是骰子自己发的或者当发现at了任何人但不是骰子的时候不执行
    try:
        reply_config_this = reply_config.config[str(event.self_id)]
        for arg in ["on", "off"]:
            if reply_config_this["command_" + arg] == "":
                raise KeyError
            if re.match(
                reply_config_this["command_" + arg] + "$", event.get_plaintext()
            ):
                state["blocker_state"] = "reply_" + arg
    except KeyError:
        if match := re.match(
            "[.。]bot (on|off)(\s+)?(\[at:qq=\d+\])?", event.get_plaintext()
        ):
            state["blocker_state"] = "reply_" + match.group(1)
    if "blocker_state" in state:
        try:
            state["this_reply"] = reply_config_this[state["blocker_state"]]
        except (UnboundLocalError, KeyError):
            state["this_reply"] = reply_config_raw[state["blocker_state"]]
        state["blocker_type"] = blockerlist.blocker_type.get(str(event.self_id), False)
        return True
    else:
        return False


blocker = on_message(
    rule=msg_checker_rule,
    permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER,
    priority=1,
    block=True,
)


@run_preprocessor
async def blocker_hook(matcher: Matcher, event: GroupMessageEvent):
    if await blockerlist(event.group_id, str(event.self_id), matcher.plugin_name):
        logger.info("[Blocker]Your Message is Blocked By Blocker.")
        raise IgnoredException("[Blocker]Matcher Blocked By Blocker")


@blocker.handle()
async def blocker_msg_handle(
    matcher: Matcher, event: GroupMessageEvent, state: T_State
):
    assert state["this_reply"] and state["blocker_state"]
    msg_type = state["this_reply"].get("type")
    msg_data = state["this_reply"].get("data")
    if (state["blocker_state"] == "reply_on") ^ state["blocker_type"]:
        blockerlist.del_blocker(event.group_id, str(event.self_id))
    else:
        blockerlist.add_blocker(event.group_id, str(event.self_id))
    await blockerlist.save_blocker()
    if msg_type == "text":
        await matcher.finish(msg_data)
    else:
        await matcher.finish(MessageSegment(type=msg_type, data={"file": msg_data}))
