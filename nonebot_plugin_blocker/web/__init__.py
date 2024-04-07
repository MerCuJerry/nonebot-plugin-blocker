from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from secrets import compare_digest
from nonebot import get_bots
from ..config import (
    STATIC_FILE_PATH,
    MAIN_PAGE_PATH,
    ConfigSingleModel,
    reply_config,
    config,
    blockerlist,
)


async def security_dependency(
    credentials: HTTPBasicCredentials = Depends(HTTPBasic()),
):
    assert config.WEBUI_USERNAME and config.WEBUI_PASSWORD
    if not (
        compare_digest(credentials.username, config.WEBUI_USERNAME)
        and compare_digest(credentials.password, config.WEBUI_PASSWORD)
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials


app = FastAPI(
    title="Blocker插件WebUI",
    description="Blocker plugin`s webui",
    dependencies=(
        [Depends(security_dependency)]
        if config.WEBUI_USERNAME and config.WEBUI_PASSWORD
        else []
    ),
    version=("nonebot-plugin-blocker"),
)

app.mount(
    "/static", StaticFiles(directory=STATIC_FILE_PATH, html=False), name="frontend"
)


@app.get("/", response_class=HTMLResponse)
async def show_webpage():
    return HTMLResponse(
        content=MAIN_PAGE_PATH.read_text(encoding="u8"), status_code=200
    )


@app.post("/submit/{uin}")
async def __set_config__(uin: str, form: ConfigSingleModel):
    try:
        reply_config.config.update({uin: form.model_dump()})
        await reply_config.save_config()
        await blockerlist.change_blocker_type(
            uin, form.model_dump().get("blocker_list", False)
        )
        return {"result": "success"}
    except Exception:
        return {"result": "failed"}


@app.get("/query_reply_list")
async def __get_reply_list__():
    try:
        bot_list : set = set(get_bots().keys())
        bot_list.update(reply_config.config.keys())
        return {"result": "success", "data": list(bot_list)}
    except Exception:
        return {"result": "failed"}


@app.get("/query_reply")
async def __get_reply_config__(uin: str):
    try:
        return {"result": "success", "data": reply_config.config.get(uin)}
    except Exception:
        return {"result": "failed"}


@app.get("/delete")
async def __delete_reply_config__(uin: str):
    try:
        reply_config.config.pop(uin)
        await reply_config.save_config()
        await blockerlist.change_blocker_type(uin)
        return {"result": "success"}
    except Exception:
        return {"result": "failed"}
