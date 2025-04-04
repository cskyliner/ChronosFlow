# project Untitled


## Python Essential:

	Python3.10
	PySide6
	PEP 8 风格规范
	...
## 界面美化设计：

	QtDesigner...

## 版本控制与协作
	git,github...
## 类似往年程设项目：

[MindfulMeadow](https://github.com/MindfulMeadow-Dev-Team/MindfulMeadow),
[MindFlow](https://github.com/Oscarhouhyk/MindFlow),
[Qt_taskorganizer](https://github.com/MethierAdde/Qt_taskorganizer)...

## 核心功能：

	日程管理，时间记录

## 主要功能（待选）：
1. 选择日期界面：
day week month year 切换 日历导入？万年历计算。分级展示日程形式
day:
week:
month:
year(maybe):
热度图？

2. 音频提示，视觉提示：
QSystemTrayIcon（Qt 托盘通知）任务栏：
UI设计，通知管理，菜单弹出设计
plyer.notification（通用桌面通知）：
任务临近提醒，窗口弹出，后端对接

3. Upcoming：
临近日程推荐排序？

4. 文件管理器式的日程安排：
类似文件夹，大事件套小事件

5. 日记功能：
支持markdown渲染，需要进一步研究，是否实时预览

6. 课表：
excel导入，尽可能减少手动操作

7. 给出小建议，安排空闲时间：
往届多以用户自定义任务紧急程度，与其他参数加权计算紧急程度。是否可以接入大语言模型API？或是根据Kaggle训练集预先训练好评估函数？

8. 快速检索：
根据日期、标题或者内容。检索速度？模糊检索？加tag？

9. 数据统计与可视化处理： 
10.  数据库存储读取:
MySQL,json格式（是否需要服务器存储？还是纯本地读写？）

11. *模板化：
针对北京大学，提供一种or多种**特色**模板形式以供任务安排or每日记录？

12. *活动信息获取：
利用python爬虫优势从北大官网获取活动信息并写入日历？（**难度未知**）

13. 用户个性化（profile）：
...
## Class设计

### DayBlock：
以日为单位设置日历？
### Event: 
事件日程基类
也许可以根据事件类型划分子类：
*Task（短期任务）*，*Activity（公共活动）*,*Clocks（长期打卡）*
### MainWindow: 
主窗口类
侧边栏功能对应不同主窗口，两种实现方法？：
1. 多个主页面，复制一种侧边栏sidebar
2. 一个主页面，切换不同页面形式，以一个MainWindow为母类，下存储多个主窗口样式
### CreateEventWindow：
创建日程窗口？
### CreateDailyWindow：
创建日记窗口？
### FindWindow：
检索结果
...

## 页面设计
动画?拖拽?过渡?简洁？…unknown

## 性能表现优化
多线程、异步操作保证页面流畅…
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTExMzUxNDEwMDEsLTEwMzMyODg2MDBdfQ
==
-->