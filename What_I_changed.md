# 1

在Schedule类中，通过save_text向后端发送路径、主题、内容（目前无法发送日期），通过load_text加载内容;sidebar中的文本框用类似的方式发送信息

# 2

1.新建Emitter类，管理sidebar按钮的信号，并负责向MainWindow发送信号
2.在CreateEventWindow新建Schedule类，负责日程添加

# 3

1.更改了sidebar搜索按钮的样式；更改了sidebar的背景，以暂时解决不同主题的问题
2.添加了向MainWindow发信号的self.emitter;要想再向sidebar中添加新按钮，只需在存储按钮名字的元组中添加新页面的名字，即可创建好一个向MainWindow发射的新信号,接下来只需要在MainWindow中创建对应页面即可

# 4

将日历单击右键添加日程改为左键单击后更新到专门的页面

# 5

1.将主窗口改为了stack，现有四个页面（与sidebar按钮对应）
2.实现了通过点击日历或侧栏来切换页面的功能
