# 1

1.新建Emitter类，管理sidebar按钮的信号，并负责向MainWindow发送信号
2.新建Schedule类，负责日程添加

# 2

1.更改了sidebar搜索按钮的样式；更改了sidebar的背景，以暂时解决不同主题的问题
2.添加了向MainWindow发信号的self.emitter;要想再向sidebar中添加新按钮，只需在存储按钮名字的元组中添加新页面的名字，即可创建好一个向MainWindow发射的新信号,接下来只需要在MainWindow中创建对应页面即可

# 3

将日历单击右键添加日程改为左键单击后更新到专门的页面

# 4

1.将主窗口改为了stack，现有四个页面（与sidebar按钮对应）
2.实现了通过点击日历或侧栏来切换页面的功能
