# sublime.conf

Sublime Text 4169 私人配置，融合了 subl 与 vsc 的操作习惯，聚焦于打造一个敏捷操作的文本查看器兼轻量级编辑器。

# 配置内容

1. 删改 Default 包，消除对于个人冗余的功能并削弱其预置命令、按键映射对其它插件的影响
2. 添加 CorePatch 包，提供或增强一部分便捷功能

# 逆向定制内容

使用 x64dbg 对 sublime_text 进行了轻微修改，patch 文件见 Patch/ 目录。

1. 拦截了证书检查，subl 将默认激活且 Remove License 将不再有效。
2. 删除了 About 界面的 `Registered to` 行。

请自行使用 x64dbg 附加到 sublime_text 进程后加载 patch 文件打补丁生成 crack 版本。
