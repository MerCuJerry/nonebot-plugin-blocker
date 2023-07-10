from nonebot.plugin import PluginMetadata

from .__main__ import *  # noqa

__version__ = "0.1.5"
__plugin_meta__ = PluginMetadata(
    name="Blocker",
    description='分群配置关闭Bot插件',
    type="application",
    homepage="https://github.com/MerCuJerry/nonebot-plugin-blocker",
    supported_adapters={"~onebot.v11"},
)