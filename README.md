<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-blocker

_✨ NoneBot Plugin Blocker ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/MerCuJerry/nonebot-plugin-blocker.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-blocker">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-blocker.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
<a href="https://pypi.python.org/pypi/nonebot-plugin-blocker" rel="nofollow">
    <img alt="pypi download" src="https://img.shields.io/pypi/dm/nonebot-plugin-blocker" style="max-width: 100%;">
</a>
</div>

## 📖 介绍

这是一个 nonebot2 插件项目，用于分群配置机器人的开启关闭

插件提供了一个简单的WebUI来让你配置Bot的开关指令以及对指令做出的回复。

## 💿 安装
<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-blocker
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_blocker"]

</details>

## ⚙️ 配置

### 请注意，使用<0.3.1版本的更新之后请重新在WebUI里进行配置
### >0.3.1,<0.3.3的请更新到0.3.3来自动更新配置项或者更新之后手动重新在WebUI里配置

### 常规配置项，位于.env文件里

```ini
#WebUI的登录凭证，不设置即不进行验证
BLOCKER_WEBUI_USERNAME=""
BLOCKER_WEBUI_PASSWORD=""
```

### 其他配置项

插件的回复配置文件位于 `data/blocker/config.json` 里，不建议手动更改

`data/blocker/blocklist.json` 里是已经加入名单的群号，可以在关闭nonebot之后手动编辑

## 💬 指令

指令只有管理员，群主以及Bot的SUPERUSER能够使用

### .bot on在该群开启bot

### .bot off在该群关闭bot

### 在上述指令后at特定bot将关闭使用了本插件的特定Bot，不会影响使用本插件的其他Bot

### 如果你在WebUI设置了指令|回复那么指令|回复将会是你设置的文本
