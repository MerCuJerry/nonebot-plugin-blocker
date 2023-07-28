from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from secrets import compare_digest
from ..config import(
    STATIC_FILE_PATH,
    MAIN_PAGE_PATH,
    ConfigModel,
    get_reply_config,
    save_reply_config,
    config
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
    version=("nonebot-plugin-blocker")
)

app.mount("/static", StaticFiles(directory=STATIC_FILE_PATH, html=False), name="frontend")

@app.get("/",response_class=HTMLResponse)
async def show_webpage():
    return HTMLResponse(content=MAIN_PAGE_PATH.read_text(encoding="UTF-8"), status_code=200)

@app.post("/submit")
async def __set_config__(form: ConfigModel):
    save_dict = get_reply_config()
    save_dict.update(form.dict().get("__root__"))
    save_reply_config(ConfigModel.parse_obj(save_dict))
    try:
        return {"result":"success"}
    except:
        return {"result":"failed"}
        
@app.get("/query_reply_list")
async def __get_reply_list__():
    try:
        return {"result":"success","data":list(get_reply_config().keys())}
    except:
        return {"result":"failed"}
    
@app.get("/query_reply")
async def __get_reply_config__(uin: str):
    try:
        return {"result":"success","data":get_reply_config().get(uin,"none")}
    except:
        return {"result":"failed"}
    
@app.get("/delete")
async def __delete_reply_config__(uin: str):
    try:
        save_dict = get_reply_config()
        save_dict.pop(uin)
        save_reply_config(ConfigModel.parse_obj(save_dict))
        return {"result":"success"}
    except:
        return {"result":"failed"}