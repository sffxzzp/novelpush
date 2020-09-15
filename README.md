NovelPush
======

基于 Python 3 的小说框架

特性
------

以下为特性列表，打勾为支持，未打勾待后续更新支持

- [x] 支持多网站来源，目前可用 json 或 python 自行扩展小说网站来源
- [x] 支持以正则形式过滤小说正文中的广告
- [x] 支持断点续传
- [x] 支持发生错误/关闭后，重开自动恢复
- [x] 支持自动打包为 epub 文件
- [x] 支持转换为 mobi 格式（依赖 kindlegen）
- [x] 支持自动发送邮件到指定邮箱
- [ ] 小说来源支持 css 选择器（需要 BeautifulSoup 模块支持）
- [ ] Web 界面

需求
------

1. requests

编写书源
------

请参考 plugins 目录下的文件

配置文件
------

请根据 settings-sample.json 文件，编辑并保存为 settings.json 文件。

或直接运行，遵循程序指引进行配置
