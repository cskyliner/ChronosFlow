# project Untitled
- [Preparation](#preparation)
  - [Python Essential](#python-essential)
  - [版本控制与协作](#版本控制与协作)
  - [类似开源项目](#类似开源项目)
  - [核心功能](#核心功能)
  - [主要功能](#主要功能)
- [class设计](#class设计)
  - [Event](#event)
  - [Data](#data)
  - [Notice](#notice)
  - [MainWindow](#mainwindow)
  - [Calendar](#calendar)
  - [CreateEventWindow](#createeventwindow)
  - [CreateDailyWindow](#createdailywindow)
  - [FindWindow](#findwindow)
  - [Settings](#settings)
  - [SideBar](#siderbar)
- [页面设计](#页面设计)
- [性能优化](#性能优化)


# Preparation

## Python Essential:
conda\
Python3.10\
[sqlite3](https://docs.python.org/3/library/sqlite3.html)\
[PySide6](https://doc.qt.io/qtforpython-6/index.html)(>=6.72)\
[PEP 8 代码风格规范](https://peps.python.org/pep-0008/)\
...

## 版本控制与协作
	git,github...
    **分支策略**  
  `main`(稳定版) + `docs`(开发文档) + `userX/*`(开发分支)
## 类似开源项目：
往年程设：\
[MindfulMeadow](https://github.com/MindfulMeadow-Dev-Team/MindfulMeadow),
[MindFlow](https://github.com/Oscarhouhyk/MindFlow),
[Qt_taskorganizer](https://github.com/MethierAdde/Qt_taskorganizer)\
开源项目：\
[Beaverhabits](https://github.com/daya0576/beaverhabits)
[Reminders](https://github.com/remindersdevs/Reminders?tab=readme-ov-file)
## 核心功能：
	日程管理，时间记录，任务规划

## 主要功能：
1. **分级日历纵览**：\
分级展示日程\
day:\
<img src="CalendarSampleDay1.jpg" width="200" height="350"/>\
week:\
<img src="CalendarSampleWeek1.jpg" width="200" height="350"/>\
month:\
<img src="CalendarSampleMonth1.jpg" width="200" height="350"/>\
or\
<img src="CalendarSampleYear2.png" width="300" height="200"/>\
year(maybe):\
<img src="CalendarSampleYear1.jpg" width="200" height="350"/>\

2. **音频提示，视觉提示**：\
通过任务栏小托盘实现快速操作，连接系统通知实现原生体验的日程提醒。
3. **Upcoming**：\
临近日程根据优先级显示
4. **给出小建议，安排空闲时间**：\
以用户自定义任务紧急程度，与其他参数加权计算紧急程度。较远目标：（智能型任务助手）
5. **分级式的日程安排**：\
对Event采取不同分类：\
DDL直接使用截止日期和提前通知；\
Task则使用树状管理，每个节点都作为Task类型，使用markdown格式，而叶则采用checklist，检查是否存在子任务来自动决定是否为最小事件\
Clock则为长期打卡任务，实现重复提醒操作
6. 日记功能：\
支持markdown格式，文本本地储存，允许用户自定义地址
7. 课表：\
支持excel导入，尽可能减少手动操作
8. 快速检索：\
根据日期、标题或tag准确搜索，加入对内容的模糊搜索。
9. 数据统计与可视化处理：
周总结，热度图直观显示每日安排
10. 模板化：\
针对北京大学，提供一种or多种**特色**预制模板形式，以供快速布置任务安排or进行每日记录
...
# Class设计

## Event: 
事件日程基类，连接前后端\
也许可以根据事件类型划分子类：
*Task（短期日程）*，*Activity（公共活动）*,*Clocks（长期打卡）*,*DDL（截止日期）*...\
函数接口：\
创建事件
EventFactory.create(事件类型，事件标题)\
增删改事件:
event.add_event(),event.delete_event(),event.modify_event()\
搜索事件：
search_all(keywords:str)(全局搜索)
## Notice:
QSystemTrayIcon（Qt 托盘通知）任务栏：
处理UI设计，通知管理，菜单弹出设计\
plyer.notification（通用桌面通知）：
任务临近提醒，窗口弹出，后端对接
## MainWindow: 
主窗口类\
存储多个主窗口样式
包含一个侧边栏
## Calendar:
日历显示类\
月分级为主要窗口
使用Qt自带QCalendarWidget组件实现了以月单位的日历，支持基本的右键添加操作菜单\
TODO： 日，周，年的处理。（拖拽实现多选）。 日历中快速添加日程，解析自然语言时间。和创建日程窗口连接。
“联动操作”，点击月分级中的日方块，跳转到日窗口之类的人性化快捷操作。
## CreateEventWindow：
创建日程窗口：
和Event类实现前后端对接
## CreateDailyWindow：
创建日记窗口：
记录日记，实现markdown渲染
## FindWindow：
检索结果
## Settings:
设置窗口
具体类别：
本地存储地址设置
通知设置
## SiderBar:
侧边栏类\
实现多种功能切换,提供搜索栏入口，（整合进Task的文件夹分类）\
动画:连接toggle_btn，使用InOutQuad曲线滑动处理\
FIXME:似乎对于Dark模式的支持不好
## Upcoming:
即将到来的日程：
按照时间轴排序，同时支持拖拽快速修改日程
...

# 页面设计
tools:\
[qss](https://doc.qt.io/qtforpython-6/tutorials/basictutorial/widgetstyling.html#tutorial-widgetstyling)(类似前端css)自定义qtUI格式\
操作动画：QPropertyAnimation\
Layout自动布局
图标与背景图案设计:
toggle_btn的图标，搜索按键的图标，日历的背景图案

# 性能优化
多线程、异步操作保证页面流畅…
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTExMzUxNDEwMDEsLTEwMzMyODg2MDBdfQ
==
-->