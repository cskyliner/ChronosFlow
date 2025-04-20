# 1

1.新建Emitter类，管理sidebar按钮的信号，并负责向MainWindow发送信号
2.新建Schedule类，负责日程添加

# 2

更改了sidebar搜索按钮、侧栏控制按钮的样式，并添加了向MainWindow发信号的self.emitter

# 3

将日历单击右键添加日程改为左键单击后更新到专门的页面

# 4

1.将主窗口改为了stack，现有日历、日程添加两个页面
2.实现了通过点击日历或侧栏来切换页面的功能
