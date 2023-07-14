<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-blocker

_✨ NoneBot Plugin Blocker ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/owner/nonebot-plugin-blocker.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-blocker">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-blocker.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>

## 📖 介绍

这是一个 nonebot2 插件项目，用于分群配置机器人的开启关闭

## 💿 安装
<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-blocker
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot-plugin-blocker"]

</details>

## ⚙️ 配置

插件的配置文件位于 `data/blocker/blocker_reply.json` 里
```jsonc
    {
        "reply_on":{
            "type":"text"
            "data":{
                "text":"在本群开启"
            }
        },
        "reply_off":{
            "type":"text"
            "data":{
                "text":"在本群关闭"
            }
        }
    }
```
`data/blocker/blocklist.json` 里是已经设置关闭Bot的群号，可以在关闭nonebot之后手动编辑

## 💬 指令

指令只有管理员，群主以及Bot的SUPERUSER能够使用

### .bot on在该群开启bot

### .bot off在该群关闭bot

### 在上述指令后at特定bot将关闭使用了本插件的特定Bot，不会影响使用本插件的其他Bot