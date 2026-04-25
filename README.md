### 建分支 (要做功能自己建)
git switch main
git pull origin main
git switch -c feature/login-page #建分支並切過去
	# 結構是<類型>/<分支名>
	# feature/ 新功能
	# fix/ 修 bug
	# hotfix/ 緊急修復
	# refactor/ 重構
git push -u origin feature/login-page

### 更新分支

## 每天做事前
git switch main
git pull origin main # 把最新的main拉下來
git switch feature/login-page
git merge main

## 做完後
git add .
git commit -m "完成登入頁面"
git push
打開github專案頁面
通常會跳出Compare & pull request
填標題：如新增登入頁面
填描述：如完成 login UI
	串接 API
按Create Pull Request

