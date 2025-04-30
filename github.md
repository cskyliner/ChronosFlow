# 添加远程仓库

## 生成SSH密钥

ssh-keygen -t rsa -b 4096 -C "邮箱"

## 查看密钥 & 复制密钥

cat ~/.ssh/id_rsa.pub   
cat ~/.ssh/id_rsa.pub | clip

## 将密钥添加到GitHub中

Settings → SSH and GPG keys → New SSH key

## 测试 SSH 连接（应该看到欢迎消息，确认认证成功）

ssh -T git@github.com

## 添加 SSH 远程仓库

git remote add origin 仓库地址

## 验证远程仓库

git remote -v

应该看到类似这样的 SSH URL：
origin git@github.com:username/repo.git (fetch)
origin git@github.com:username/repo.git (push)

## 首次推送代码

git push -u origin 分支

## 其它

查看所有远程仓库 git remote -v
查看某个远程仓库地址 git remote get-url origin
查看远程仓库详细信息 git remote show origin
查看本地分支与远程分支的关联 git branch -vv
修改远程地址 git remote set-url origin <新地址>
删除远程仓库 git remote remove origin

# 日常推送代码

## 转到某文件

cd 地址

## 创建仓库

git branch 仓库名

## 转到仓库

git checkout 仓库名

## 本地暂存文件

git add .文件名

## 将暂存区的更改提交到本地仓库，并附带一条简短的提交信息（如这里的start settings）

git commit -m "start settings"

## 向github上传分支

git push origin 分支名

# 拉取分支的内容

git pull origin 分支名

## 查看进度

git status

## 拉取时允许无关历史

git pull origin 分支名 --allow-unrelated-histories

## 或者合并时允许

git merge origin/分支名 --allow-unrelated-histories