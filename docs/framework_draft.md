# CHRONOSFLOW
- [Preparation](#preparation)
  - [Python Essential](#python-essential)
  - [版本控制与协作](#版本控制与协作)
    - [分支策略](#分支策略)
    - [工作流程](#工作流程)
    - [commit规范](#commit规范)
  - [类似开源项目](#类似开源项目)
  - [核心功能](#核心功能)
  - [主要功能](#主要功能)
- [文件及class功能设计](#文件及class功能设计)
  - [main](#main)
  - [Event](#event)
  - [Data](#data)
  - [Notice](#notice)
  - [MainWindow](#mainwindow)
  - [Calendar](#calendar)
  - [Emitter](#emitter)
  - [CreateEventWindow](#createeventwindowschedule)
  - [CreateDailyWindow](#createdailywindow)
  - [FindWindow](#findwindow)
  - [Settings](#settings)
  - [SideBar](#siderbar)
  - [common](#common)
  - [SignalConnect](#signalconnect)
  - [Tray](#tray)
  - [FloatingWindow](#floatingwindow)
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
[本项目GitHub网址](https://github.com/cskyliner/ChronosFlow)
### 分支策略
`main`(稳定版) + `docs`(更新开发文档) + `userX/*`(开发分支)
### 工作流程
1. 获取某分支新代码
```
git checkout branchX
git pull origin branchX
```
2. 同步main进度
```
git checkout userX
git fetch origin
git merge origin/main
```
**如果出现冲突，处理冲突后重新提交一次**
```
git add .
git commit 
```
**尽量不要merge其他user的分支，这样会导致git记录混乱**
3. 进行开发 → 提交更改 → 推送到远程
```
git add .
git commit -m "feat: 添加xxx功能"
git push origin userX
```
4. 通过 Pull Request 提交合并请求，合并到main分支：
+ 填写清晰的标题与描述
+ 选择合并方式：Squash and merge
+ 修改提交信息，给出本次提交实现功能和修改bug的简要描述

### commit规范
```
<标签>: <简洁描述>
```
可参考[conventional commits](https://www.conventionalcommits.org/en/v1.0.0/)
|标签|含义|
|---|----|
|fix| 修改bug|
|feat| 添加功能|
|docs| 修改文档|
|style| 格式调整|
|refactor|重构代码（无功能影响）|
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
# 文件及class功能设计
## main：
feat:主文件，项目入口\
实现了主窗口的创建\
实现了信号连接即SignalConnect\
实现了读取logging配置\
实现了检测系统类型\
## Event: 
feat:事件日程基类，连接前后端\
根据事件类型划分子类：
*Activity（公共活动）*,*Clocks（长期打卡）*,*DDL（截止日期）*...\
**子类参数**：
```python
class DDLEvent(BaseEvent):
	"""
	DDL类
	输入：标题，截止时间，具体内容，提前提醒时间，重要程度，是否完成或过期（0为未完成，1为完成）
	"""
	def __init__(self, title: str, datetime: str, notes: str, advance_time: str, importance: str, done: int = 0):
		super().__init__(title)
		self.datetime = datetime  # 格式："yyyy-MM-dd HH:mm"
		self.notes = notes
		self.advance_time = advance_time
		self.importance = importance
		self.done = done
class ActivityEvent(BaseEvent):
  """
  活动类
  输入：标题，开始时间，结束时间，具体内容，提前提醒时间，重要程度，是否完成或过期（0为未完成，1为完成）
  """
  def __init__(self, title: str, start_time: str, end_time: str, notes: str, advance_time: str, importance: str, done: int = 0):
    super().__init__(title)
    self.start_time = start_time  # 格式："yyyy-MM-dd HH:mm"
    self.end_time = end_time
    self.notes = notes
    self.advance_time = advance_time
    self.importance = importance
    self.done = done
```
TODO:对重复的处理，新类型的支持
## Notice:
feat:通知和任务栏浮窗\
已完成：\
保存通知信息，连接系统时间，按时发送信号给托盘和悬浮窗\
TODO：任务栏UI设计的Mac适配,后端对接\
## MainWindow: 
feat:主窗口类\
存储多个主窗口样式，包含一个侧边栏\
TODO：支持多种主题样式
## Calendar:
feat:日历显示类\
月分级为主要窗口，使用Qt自带QCalendarWidget组件实现了以月单位的日历\
TODO：“联动操作”，左键单击月分级中的日方块后到专门的添加日程页面，展示出每日的日程安排（此处或许可以复用Upcoming）。日、周、年的处理。日历中快速添加日程和创建。修改日程窗口连接。支持基本的右键添加操作菜单。\
Try:尝试通过自己构建万年历实现界面自定义优化
## CreateEventWindow（Schedule）：
feat:有Schedule类，创建/修改日程窗口\
DDL类基本实现：通过save_text向后端发送路径、日期、主题、内容\
TODO:通过load_text加载已有事件内容，和Event类实现前后端对接，实现了对接后端创建DDL事件，对其他事件类型的支持（此处**务必**和后端做好对接）。
## Emitter：
feat:用于统一发送信号，进行前后端对接\
**统一实例化**：
为了便于信号发射接收的统一，设置单独实例化
，每次调用emitter时候，只需要```Emitter.instance().函数名.connect/emit()```就可以了，**是否有必要多次实例化有待讨论**\
具体信号见Emiiter.py
## CreateDailyWindow：
feat:记录日记，实现markdown渲染\
TODO:创建日记窗口：\
## FindWindow：
feat:搜索窗口\
在主窗口中实现折叠窗口\
TODO:检索结果和upcoming实现代码复用
## Settings:
feat:设置窗口\
具体类别：\
本地存储地址设置,通知设置\
已完成：
设置保存,本地存储地址设置\
TODO:通知方式自定义(仅显示),音量调节(仅显示),背景颜色(仅显示)
## SiderBar:
feat:侧边栏类,实现多种功能切换\
要想再向sidebar中添加新按钮，只需在存储按钮名字的元组中添加新页面的名字，即可创建好一个向MainWindow发射的新信号,接下来只需要在MainWindow中创建对应页面即可
## Upcoming:
feat:即将到来的日程\
同一日期的日程合并在一个时间框下\
TODO:点击“眼睛”按钮快速修改日程(跳转到Schedule)，m可以通过拖拽来修改时间\
按照时间轴排序，与后端连接
## common:
feat:打包导入的库，避免每次import大量库，直接
```from common import *```即可
## SignalConnect:
feat:初始化Emiiter和Event中参数连接
## Tray
feat:托盘类\
实现系统托盘，程序初始化会在系统任务栏产生一个图标,通过右键图标能够回到主页面，显示悬浮窗，以及彻底退出应用,同时接受消息并形成系统通知
## FloatingWindow
feat:悬浮窗类\
最小化主窗口会产生悬浮窗，通过悬浮窗按钮能够回到主页面，隐藏悬浮窗，彻底退出应用
消息通知也会显示在悬浮窗上

...

# 页面设计
**Tools**:[qss](https://doc.qt.io/qtforpython-6/tutorials/basictutorial/widgetstyling.html#tutorial-widgetstyling)(类似前端css)自定义qtUI格式\
**操作动画**：QPropertyAnimation\
**图标与背景图案设计**:
日历的背景图案，设置否需要单独一个图标而不是放在侧边栏，
创建事件窗口的美化，日历不会随着窗口缩放而缩放

# 性能优化
多线程、异步操作保证页面流畅…