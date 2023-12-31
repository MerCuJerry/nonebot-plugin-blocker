from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from secrets import compare_digest
from ..config import (
    STATIC_FILE_PATH,
    MAIN_PAGE_PATH,
    ConfigModel,
    ConfigSingleModel,
    get_reply_config,
    save_reply_config,
    config,
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
        [Depends(security_dependency)] if config.WEBUI_USERNAME and config.WEBUI_PASSWORD else []
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
        config = get_reply_config()
        this_config = {uin: form.dict()}
        config.update(this_config)
        from ..__main__ import blockerlist

        blockerlist.change_blocker_type(uin, form.dict().get("blocker_list", False))
        save_reply_config(ConfigModel.parse_obj(config))
        return {"result": "success"}
    except:
        return {"result": "failed"}


@app.get("/query_reply_list")
async def __get_reply_list__():
    try:
        config = get_reply_config()
        return {"result": "success", "data": list(config.keys())}
    except:
        return {"result": "failed"}


@app.get("/query_reply")
async def __get_reply_config__(uin: str):
    try:
        config = get_reply_config()
        return {"result": "success", "data": config.get(uin, "none")}
    except:
        return {"result": "failed"}


@app.get("/delete")
async def __delete_reply_config__(uin: str):
    try:
        config = get_reply_config()
        config.pop(uin)
        from ..__main__ import blockerlist

        blockerlist.change_blocker_type(uin)
        save_reply_config(ConfigModel.parse_obj(config))
        return {"result": "success"}
    except:
        return {"result": "failed"}
