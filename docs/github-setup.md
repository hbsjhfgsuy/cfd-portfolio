# 本机 Git / GitHub 配置备忘

> 记录这台机器上为了推这个仓库所做的配置，换机器时照做一遍即可。

## 1. Git 本体

- 版本：git 2.55.0（MinGit 免安装版）
- 安装位置：`%LOCALAPPDATA%\Programs\MinGit`
- 已加入用户 PATH，**新开的终端**里直接敲 `git` 即可（当前已开着的窗口要重开）
- 注意：MinGit 不含 Git Bash，也没有图形化凭据管理器；命令行操作正常

## 2. 网络

本机直连 `github.com:443` 会被丢包（DNS 正常，TCP 超时），但系统代理可用。

已配置（全局）：

```bash
git config --global http.proxy  http://127.0.0.1:65532
git config --global https.proxy http://127.0.0.1:65532
```

代理端口若变化（Clash / v2ray 等重启后可能变），重新执行上面两条即可。

SSH 走 443 端口（22 端口通常被封），配置在 `~/.ssh/config`：

```text
Host github.com
    HostName ssh.github.com
    Port 443
    User git
    IdentityFile ~/.ssh/id_ed25519_cfd
    IdentitiesOnly yes
```

## 3. 首次推送步骤

1. 把公钥 `~/.ssh/id_ed25519_cfd.pub` 的内容贴到 <https://github.com/settings/keys>（Title 随便写，Key type 选 Authentication Key）。
2. 在 GitHub 上**新建空仓库** `cfd-portfolio`——不要勾选 README / .gitignore / license，否则会和本地首个提交冲突。
3. 关联并推送：

```bash
cd C:/Users/Administrator/Desktop/CFD/cfd-portfolio
git remote add origin git@github.com:<你的用户名>/cfd-portfolio.git
git push -u origin main
```

## 4. 验证

```bash
ssh -T git@github.com      # 应返回 "Hi <用户名>! You've successfully authenticated"
git remote -v              # 确认 origin 指向正确
git status                 # 应显示 working tree clean
```

## 5. 换机器后重新出图

```bash
python -m pip install -r requirements.txt
python scripts/fetch_flameD.py --extract
python scripts/export_flamed_csv.py
python scripts/plot_flamed.py
```

原始数据（`data/raw/`）不入库，因此 clone 下来只有几百 KB，跑一遍脚本就有完整数据。
