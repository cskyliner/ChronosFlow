# 将暂存区（Staging Area）的更改提交到本地仓库，并附带一条简短的提交信息（如这里的start settings）

git commit -m "start settings"

# 创建userB

git branch userB

# Switched to branch 'userB'

git checkout userB

# 本地新增文件

git add .文件名

# 下载userB的内容

git pull origin userB

# 向github上传userB

git push origin userB

# 查看进度

git status

#  

需求 命令
查看所有远程仓库 git remote -v
查看某个远程仓库地址 git remote get-url origin
查看远程仓库详细信息 git remote show origin
查看本地分支与远程分支的关联 git branch -vv
修改远程地址 git remote set-url origin <新地址>
删除远程仓库 git remote remove origin