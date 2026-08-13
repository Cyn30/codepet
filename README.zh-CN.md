# CodePet 中文指南

<p align="center">
  <strong>坚持培养编程习惯，养育陪伴桌面宠物。</strong>
</p>

<p align="center">
  一只生活在你的桌面上的像素宠物。它会回应你的照顾，并随着真实 GitHub 活动成长。
</p>

<p align="center">
  <a href="https://github.com/Cyn30/codepet/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/Cyn30/codepet/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="公开测试版" src="https://img.shields.io/badge/status-public%20alpha-f59e0b">
  <img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="macOS、Windows、Linux" src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-6b7280">
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-22c55e"></a>
  <a href="https://github.com/Cyn30/codepet/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/Cyn30/codepet?style=social"></a>
</p>

<p align="center">
  <img src="website/public/og.png" alt="CodePet 像素桌面宠物" width="820">
</p>

<p align="center">
  <a href="https://github.com/Cyn30/codepet/releases"><strong>下载 CodePet</strong></a>
  ·
  <a href="README.md">English README</a>
  ·
  <a href="https://github.com/Cyn30/codepet/issues/new">报告问题</a>
  ·
  <a href="CONTRIBUTING.md">参与贡献</a>
</p>

> **公开测试版：**桌面宠物、自然行为、双宠物家庭、商店、GitHub 奖励、旧存档
> 迁移和跨平台构建流程已经实现。每次发布前仍应在真实设备上测试安装包。如果
> Releases 页面暂时没有安装包，请使用下方的源码运行方式。

## 为什么做 CodePet？

CodePet 把持续编程变成一段能直接看见的小小陪伴。宠物会休息、散步、短跑、
进食、撒娇，并通过 emoji 气泡表达心情。Commit、pull request 和创建 repository
会转化成经验值、金币、亲密度以及偶尔掉落的食物。

它采用互动桌宠常用的本机应用模式：无边框透明窗口、置顶显示和
系统托盘控制，但美术、玩法和代码均为原创。CodePet **不会监听键盘，也不会读取
你的源代码**。

## 核心亮点

| | 功能 | 实际体验 |
| --- | --- | --- |
| 🐾 | 本机桌面宠物 | 透明、无边框、可拖动、置顶显示的宠物窗口 |
| 🎞️ | 自然像素动画 | 每个品种都有待机、走路、跑步、进食、撒娇和睡觉动画 |
| 🌿 | 贴近真实的行为 | 渐进加减速、停下休息、进食消化期，不会随机瞬移 |
| 💻 | GitHub 驱动成长 | Commit、PR 和新 repository 会带来游戏奖励 |
| 💛 | 照顾与亲密度 | 饥饿、快乐、精力、五段亲密度、心情、食物和陪玩 |
| 🐱 | 小猫和小狗 | 首批 6 个品种，每个家庭最多同时养 2 只 |
| 🏠 | 笼子与放风 | 可以自由活动、休息、短跑，也可以回到笼子 |
| 🔒 | 本地优先隐私 | 本地存档、系统钥匙串、无遥测、无键盘监听 |

## 安装

预构建版本已经包含 Python、Qt 和美术资源，普通用户不需要安装开发工具。

### macOS

1. 打开 [Releases 页面](https://github.com/Cyn30/codepet/releases)。
2. 从最新版本下载 `CodePet-macOS.dmg`。
3. 打开磁盘映像，把 `CodePet.app` 拖入 **Applications（应用程序）**。
4. 从应用程序文件夹启动 CodePet。

Alpha 安装包可能尚未完成 Apple notarization。如果 macOS 阻止启动，请在应用程序
文件夹中右键 CodePet，选择“打开”，并且只在确认文件来自本仓库时继续。正式稳定
版本应使用 Apple Developer ID 签名并完成 notarization。

### Windows

1. 从 [Releases 页面](https://github.com/Cyn30/codepet/releases) 下载 `CodePet-Windows.zip`。
2. 完整解压压缩包。
3. 打开解压后的 `CodePet` 文件夹。
4. 运行 `CodePet.exe`。

请保留整个文件夹，不要单独移动 exe；旁边的 Qt 库也是应用的一部分。

### Linux

1. 从 [Releases 页面](https://github.com/Cyn30/codepet/releases) 下载 `CodePet-Linux.tar.gz`。
2. 解压压缩包。
3. 运行 `CodePet/CodePet`。

目前 X11 的透明置顶窗口体验最一致；Wayland 的行为取决于桌面合成器。

## 启动后的前三分钟

1. 选择宠物名字、物种和品种。
2. 设置 14 至 3,650 天的寿命。
3. 点击 **Adopt**。
4. 左键点击桌面宠物相当于抚摸，每次增加 1–2 点亲密度。
5. 右键宠物可以选择休息、散步、短跑、恢复自然活动、回笼、同步 GitHub 或隐藏。
6. 打开 **CodePet Home** 喂食、进入商店、切换当前宠物或领养第二只宠物。

GitHub 奖励发给当前选中的宠物；金币、食物和已处理事件属于家庭共享，因此同一个
GitHub 事件不能被两只宠物重复领取。

## 自然行为，而不是随机换动作

CodePet 不会在每个计时器 tick 随机选择姿势。每只宠物会经历有时间边界的行为
阶段：观察四周、慢慢散步、短距离奔跑、逐渐减速，然后窝着休息。狗更偏好持续
散步，猫更偏好长时间休息和短时爆发。近期状态记忆会减少连续重复，而且任何
状态都不会无限持续。

位移按照真实经过时间计算，而不是每帧固定移动。散步约为每秒 10–16 像素，奔跑
约为每秒 27–38 像素，所以走几步不会突然横穿整个屏幕。宠物会在屏幕边缘前刹车，
停顿后转身；动作会在完整循环后切换；进食后必定先进入休息期。

## 安全连接 GitHub

推荐直接使用桌面应用内置登录：

1. 打开 **CodePet Home**。
2. 点击 **Connect GitHub**。
3. CodePet 会复制一次性验证码，并在浏览器中打开 GitHub。
4. 输入验证码，确认只读权限。
5. 返回 CodePet，点击 **Sync GitHub**。

CodePet 使用 GitHub Device Flow。授权凭据保存在 macOS Keychain、Windows
Credential Locker 或 Linux 桌面钥匙串中，不会写入 `save.json`、网站或仓库。

### CodePet 会读取什么？

| 数据 | 用途 |
| --- | --- |
| GitHub 用户 ID 和用户名 | 确认当前授权用户 |
| Commit ID 和作者关系 | 统计用户近期 commit |
| Pull request contribution ID | 为近期 PR 发放奖励 |
| Repository contribution ID | 为新建 repository 发放奖励 |

GitHub App 只有 Metadata、Contents 和 Pull requests 的只读权限。Contents 权限在
技术上允许读取 repository 数据，但 CodePet 的 GraphQL 查询不会请求文件内容、
diff、源代码、commit message、Issue 文本或 secret。只有用户和 GitHub App 安装
都被允许访问时，私有活动才可能被统计。

### 开发者备用方式

也可以安装 [GitHub CLI](https://cli.github.com/) 并运行：

```bash
gh auth login
```

或者使用细粒度、只读的开发 token 启动 CodePet：

```bash
export GITHUB_TOKEN="github_pat_your_token_here"
codepet-desktop
```

PowerShell：

```powershell
$env:GITHUB_TOKEN="github_pat_your_token_here"
codepet-desktop
```

只选择希望统计的 repository，并只授予 Metadata、Contents 和 Pull requests 读取
权限。不要把真实 token 放进源代码、Issue、截图、commit 或文档。

## GitHub 奖励循环

奖励采用确定性计算：同一个 GitHub 事件 ID 永远得到相同结果。已处理事件保存在
本地，因此重复同步不会重复领取。

| GitHub 活动 | 经验值 | 金币 | 亲密度 | 食物 |
| --- | ---: | ---: | ---: | --- |
| Commit | 8–15 | 5–10 | 1–5 | 20% 概率 |
| Pull request | 12–20 | 5–10 | 2–5 | 无 |
| 创建 repository | 5–8 | 1–3 | 1–2 | 无 |

每一级需要的经验值都会增加。亲密度段位依次是 **New Friends**、**Familiar**、
**Friends**、**Best Friends** 和 **Soulmates**。

<details>
<summary><strong>食物价格与猫狗偏好</strong></summary>

| 食物 | 价格 | 猫猫的亲密度 | 狗狗的亲密度 |
| --- | ---: | ---: | ---: |
| 猫粮 | 15 | +3 至 +5 | −2 至 0 |
| 狗粮 | 15 | −2 至 0 | +3 至 +5 |
| 磨牙骨 | 25 | −3 至 0 | +5 至 +7 |
| 熟鸡肉 | 35 | +4 至 +7 | +4 至 +7 |
| 三文鱼 | 45 | +7 至 +10 | +3 至 +6 |
| 金枪鱼 | 60 | +9 至 +13 | +1 至 +4 |
| 庆祝大餐 | 100 | +10 至 +14 | +10 至 +14 |

物种倾向明显的食物价格更低，但喂错可能降低亲密度；价格更高的通用食物对猫狗
都更加安全。

</details>

## 心情、照顾与寿命

- `😊` / `🥰`：快乐，并且被照顾得很好
- `😴`：精力不足
- `😟`：饥饿或不开心
- `😿` / `🥺`：进入需要尽快照顾的阈值
- `💤`、`🏠`、`🌿`、`✨`：休息、回笼、放风和活动反馈

离线衰减按照有上限的 6 小时时段计算，长时间未打开应用也不会产生无限惩罚。
没有得到照顾的宠物可能损失有限亲密度，但存档永远不会被删除。达到用户设定的
寿命后，宠物会成为 **Cherished Memory**，而不是从存档中消失。

## 从设计上保护隐私

- 不进行全局键盘监听
- 不收集源代码或 commit message
- 没有遥测或广告 SDK
- 没有由 CodePet 运营的中转服务器
- GitHub 权限只读
- 凭据只保存在操作系统钥匙串
- 宠物数据保存在 `~/.codepet/save.json`
- 只有与 CodePet 窗口互动时才会收到鼠标事件

本地存档包含宠物状态、库存、金币、时间和已处理事件 ID；不包含 GitHub token、
密码、repository 文件或源代码。

## 从源代码运行

需要 Python 3.10 或更高版本：

```bash
git clone https://github.com/Cyn30/codepet.git
cd codepet
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[desktop]"
codepet-desktop
```

Windows 激活虚拟环境：

```powershell
.venv\Scripts\activate
```

## 开发与测试

```bash
python -m pip install -e ".[desktop,dev]"
python -m unittest discover -s tests -v
ruff check src tests scripts packaging/entrypoint.py
```

验证所有正式动画图集：

```bash
for atlas in assets/animations/*.png; do
  python scripts/validate_animation_atlas.py "$atlas"
done
```

在当前操作系统构建安装包：

```bash
python -m pip install -e ".[desktop,packaging]"
python scripts/build_desktop.py
```

PyInstaller 不能跨系统构建。Release 工作流会分别在 macOS、Windows 和 Linux
构建，并把安装包加入带版本号的 GitHub Release。

<details>
<summary><strong>项目架构</strong></summary>

```text
src/codepet/domain.py      宠物、家庭、心情、亲密度、寿命和衰减
src/codepet/catalog.py     食物价格和物种偏好
src/codepet/rewards.py     GitHub 事件到奖励的确定性映射
src/codepet/auth.py        Device Flow 和系统凭据存储
src/codepet/github.py      只读 GitHub GraphQL 客户端
src/codepet/storage.py     原子本地存档和旧版本迁移
src/codepet/animation.py   动画片段和状态机
src/codepet/sprites.py     带校验的品种图集加载器
src/codepet/overlay.py     透明桌面宠物窗口
src/codepet/dashboard.py   领养、库存、照顾和商店界面
src/codepet/desktop.py     应用控制器和系统托盘
packaging/                 本机应用入口和打包配置
scripts/                   美术校验和 Release 构建工具
tests/                     规则、奖励、认证、GitHub 和动画测试
```

UI 只调用领域操作，不在界面中重复计算价格、奖励或食物偏好。新增客户端和功能应
复用已有规则，不应再创建平行实现。

</details>

## 路线图

- [ ] 完成 macOS Developer ID 签名和 notarization
- [ ] 增加更多品种和新的宠物物种
- [ ] 增加笼子、家具和房间自定义
- [ ] 增加成就和更丰富的 coding streak 反馈
- [ ] 为超大型 GitHub 账号改进分页
- [ ] 扩大 Windows、Linux 和 Wayland 兼容性测试

路线图是计划并非承诺，欢迎贡献代码和提交具体、可复现的问题。

## 参与贡献

提交 pull request 前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。游戏规则修改必须
包含测试。新美术必须原创并允许重新分发；不能描摹或复制其他游戏的精灵、配色、
轮廓或角色设计。

如果 CodePet 让编程变得更有趣一点，欢迎为仓库点亮 ⭐。这能帮助更多贡献者和
桌宠爱好者发现这个项目。

## 许可证

代码采用 [MIT License](LICENSE)。美术许可与来源说明见
[ASSET-LICENSE.md](ASSET-LICENSE.md)。
