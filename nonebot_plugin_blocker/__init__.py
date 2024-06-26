from nonebot.plugin import PluginMetadata

from .__main__ import * # noqa

__version__ = "0.4.8"
__plugin_meta__ = PluginMetadata(
    name="Blocker",
    description="分群配置关闭Bot插件",
    usage="使用指令阻止机器人在该群回复",
    type="application",
    homepage="https://github.com/MerCuJerry/nonebot-plugin-blocker",
    supported_adapters={"~onebot.v11"},
    extra={
        "version": __version__,
        "author": "MerCuJerry <mercujerry@gmail.com>",
    },
)