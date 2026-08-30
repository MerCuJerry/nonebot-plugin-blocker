import re
from pathlib import Path

from fastapi import FastAPI
from nonebot import get_driver, logger, on_message

try:
    from nonebot.adapters.onebot.v11 import (
        GROUP_ADMIN,
        GROUP_OWNER,
        GroupMessageEvent,
        MessageSegment,
    )
    _BLOCKER_USE_ONEBOT_V11 = True
except ImportError:
    _BLOCKER_USE_ONEBOT_V11 = False
try:
    from nonebot.adapters.milky.event import GroupMessageEvent
    from nonebot.adapters.milky.message import MessageSegment
    from nonebot.adapters.milky.permission import GROUP_ADMIN, GROUP_OWNER
    _BLOCKER_USE_MILKY = True
except ImportError:
    _BLOCKER_USE_MILKY = False

from nonebot.drivers import ReverseDriver
from nonebot.exception import IgnoredException
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State

from . import web
from .config import blockerlist, reply_config, reply_config_raw

driver = get_driver()


@driver.on_startup
async def load_blocker_on_start():
    if isinstance(driver, ReverseDriver) and isinstance(driver.server_app, FastAPI):
        driver.server_app.mount("/blocker-webui", web.app, name="blocker-webui")
        logger.info(
            "[Blocker]WebUI is now listening on "
            f"http://{driver.config.host}:{driver.config.port}/blocker-webui/"
        )
    else:
        logger.info("[Blocker]WebUI only support FastAPI reverse driver.")


async def msg_checker_rule(event: GroupMessageEvent, state: T_State) -> bool:
    if _BLOCKER_USE_ONEBOT_V11:
        user_id = event.user_id
        self_id = event.self_id
    elif _BLOCKER_USE_MILKY:
        user_id = event.data.sender_id
        self_id = event.self_id
    if (
        ("at" in event.get_message()) and (not event.is_tome())
    ) or user_id == self_id:
        return False  # 如果是骰子自己发的或者当发现at了任何人但不是骰子的时候不执行
    try:
        reply_config_this = reply_config.config[str(self_id)]
        for arg in ["on", "off"]:
            if reply_config_this["command_" + arg] == "":
                raise KeyError
            if re.match(
                reply_config_this["command_" + arg] + "$", event.get_plaintext()
            ):
                state["blocker_state"] = "reply_" + arg
    except KeyError:
        if match := re.match(
            r"[.。]bot (on|off)(\s+)?(\[at:qq=\d+\])?", event.get_plaintext()
        ):
            state["blocker_state"] = "reply_" + match.group(1)
    if "blocker_state" in state:
        try:
            state["this_reply"] = reply_config_this[state["blocker_state"]]
        except (UnboundLocalError, KeyError):
            state["this_reply"] = reply_config_raw[state["blocker_state"]]
        state["blocker_type"] = blockerlist.blocker_type.get(str(self_id), False)
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
    if _BLOCKER_USE_ONEBOT_V11:
        group_id = event.group_id
        self_id = event.self_id
    elif _BLOCKER_USE_MILKY:
        group_id = event.data.peer_id
        self_id = event.self_id
    if await blockerlist(group_id, self_id, matcher.plugin_name):
        logger.info("[Blocker]Your Message is Blocked By Blocker.")
        raise IgnoredException("[Blocker]Matcher Blocked By Blocker")


@blocker.handle()
async def blocker_msg_handle(
    matcher: Matcher, event: GroupMessageEvent, state: T_State
):
    assert state["this_reply"] and state["blocker_state"]
    if _BLOCKER_USE_ONEBOT_V11:
        group_id = event.group_id
        self_id = event.self_id
    elif _BLOCKER_USE_MILKY:
        group_id = event.data.peer_id
        self_id = event.self_id
    msg_type = state["this_reply"].get("type")
    msg_data = state["this_reply"].get("data")
    if (state["blocker_state"] == "reply_on") ^ state["blocker_type"]:
        await blockerlist.del_blocker(group_id, str(self_id))
    else:
        await blockerlist.add_blocker(group_id, str(self_id))
    await blockerlist.save_blocker()
    match msg_type: # PEP 634 :)
        case "text" :
            msg = MessageSegment.text(msg_data)
        case "image":
            msg = MessageSegment.image(Path(msg_data).read_bytes())
        case "record":
            msg = MessageSegment.record(Path(msg_data).read_bytes())
    await matcher.finish(msg)