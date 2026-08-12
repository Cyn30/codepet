# CodePet 中文指南

**坚持编程，养大一个朋友。**

CodePet 是一个支持 macOS、Windows 和 Linux 的开源桌面宠物。宠物运行在透明桌面窗口中，可以趴在 macOS 菜单栏下方休息、沿屏幕行走、回到笼子、进食和通过白色 emoji 气泡表达情绪。它会根据用户真实的 GitHub 活动成长，但不会监听键盘，也不会读取源代码。

[返回英文主 README](README.md)

> 当前版本属于 public alpha：主要玩法、透明桌宠、双宠物家庭、商店、GitHub 奖励、旧存档迁移和安装包构建流程均已实现。发布稳定版之前，仍然需要在每个目标操作系统的真实设备上测试安装包。

## 它是怎样成为桌面应用的？

Bongo Cat 一类桌宠并不是在桌面壁纸上作画。它们运行一个本机应用，由应用创建以下组件：

1. 无边框透明窗口，用来绘制宠物。
2. 窗口置顶设置，让宠物显示在其他窗口上方。
3. 系统托盘或菜单栏图标，用来显示、隐藏、打开设置和退出。
4. 动画计时器，用来切换动作帧和改变位置。
5. 本地存档，用来保存宠物状态。
6. 安装包，把运行环境、Qt、代码和美术资源一起交付给用户。

CodePet 使用 PySide6/Qt 实现窗口和界面，使用 PyInstaller 生成本机应用。用户下载预构建 Release 后不需要自行安装 Python。

CodePet 使用原创二维像素动作表，而不是复制 Bongo Cat 或《星露谷物语》的素材。二维像素画的轮廓更清晰、资源更轻、动作更容易保持一致，也更适合社区继续添加皮肤和帧动画。

## 已有功能

- 没有矩形背景的透明可拖动桌宠
- 6 个品种均有独立正式图集，支持待机、走路、跑步、进食、撒娇和睡觉六组八帧动画
- 猫狗各自独立的自然行为调度，行为有最长时限、近期状态记忆，不使用随机瞬移
- 动作循环边界切换、渐进加减速、提前刹车转身和进食后休息期
- 使用白色 emoji 气泡表达心情和需求
- 猫和狗两类宠物，共 6 个原创品种皮肤
- 每个家庭最多同时养 2 只宠物
- 等级越高，升级所需经验越多
- 从“初识”到“灵魂伙伴”的 5 个亲密度段位
- 饥饿、快乐、精力、寿命、连续打卡和离线时间衰减
- 家庭金币、食物库存和商店
- 按猫狗现实饮食偏好设计的亲密度变化
- GitHub commit、pull request 和创建 repository 奖励
- 奖励确定性计算和事件去重
- 本地存档，不含遥测和键盘监听
- 应用内 GitHub Device Flow 登录，并把凭据保存在系统钥匙串
- 为开发者保留 GitHub CLI 和环境变量 token 备用方式

## 普通用户安装步骤

### macOS

1. 打开 GitHub 仓库的 **Releases** 页面。
2. 下载 `CodePet-macOS.dmg`。
3. 双击打开下载的 dmg。
4. 把 `CodePet.app` 拖入 **Applications（应用程序）** 文件夹。
5. 从应用程序文件夹打开 CodePet。

如果未签名的 alpha 版本被 macOS 阻止，请在应用程序文件夹中右键 CodePet，选择“打开”，然后再次确认。正式公开发布时，维护者应该使用 Apple Developer ID 对应用签名并进行 notarization，而不是长期要求用户绕过 Gatekeeper。

### Windows

1. 打开仓库的 **Releases** 页面。
2. 下载 `CodePet-Windows.zip`。
3. 完整解压 zip。
4. 打开解压后的 `CodePet` 文件夹。
5. 运行 `CodePet.exe`。

不要只把 exe 单独移动出去，因为旁边的 Qt 文件也是应用的一部分。

### Linux

1. 从 **Releases** 下载 `CodePet-Linux.tar.gz`。
2. 解压文件。
3. 运行 `CodePet/CodePet`。

Wayland 下的置顶窗口行为取决于桌面合成器；目前 X11 的透明置顶体验更加一致。

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

## 第一次启动

1. 输入宠物名字。
2. 选择猫或狗。
3. 选择具体品种。
4. 设置 14 至 3,650 天的寿命。
5. 点击 **Adopt**。
6. 在 CodePet Home 中选择宠物、陪玩、管理食物和进入商店。
7. 右键桌面宠物，可以选择休息、散步、短跑、恢复自然活动、回笼、同步 GitHub 或隐藏宠物。
8. 用鼠标左键点击宠物相当于抚摸，每次增加 1–2 点亲密度。

可以在 Home 中领养第二只宠物。GitHub 奖励会发给当前选中的宠物；金币和食物属于家庭共享。这样同一个 GitHub 事件不会被两只宠物重复放大奖励。

## 自然动作与移动逻辑

CodePet 不会在每个计时器 tick 都重新随机选动作。每只猫狗会完整经历一个有
最短和最长时间的行为阶段，例如观察四周、慢慢散步、短距离奔跑、减速停下或
窝着休息。调度器会记住近期状态并降低重复概率，而且任何自然状态都不可能
无限持续。猫更偏好长时间休息和短时爆发，狗更偏好持续散步。

位移按照真实经过时间计算，不依赖电脑帧率。散步速度约为每秒 10–16 像素，
奔跑约为每秒 27–38 像素，因此走几步不会突然横穿屏幕。速度会渐进变化；靠近
屏幕边缘时会提前刹车，停顿后再转身。进食完成后必定先休息，并在消化期内
禁止直接奔跑。画面只会在当前八帧动作完整播放后切换到下一组，避免半途截断
姿势而产生卡顿或诡异跳变。

## 连接自己的私人 GitHub

CodePet 只会在用户主动点击 **Sync GitHub** 时调用只读 GraphQL API。
桌宠是本机进程并不妨碍它访问网络：透明窗口负责显示，同一个本机应用可以
通过 HTTPS 直接调用 GitHub API，所以无需把 token 上传给网页或第三方服务器。

### 方法 A：在应用内连接 GitHub（正式 Release 推荐）

1. 打开 **CodePet Home**。
2. 点击 **Connect GitHub**。
3. CodePet 会复制一次性验证码，并在浏览器中打开 GitHub。
4. 输入验证码，确认只读 GitHub App 权限。
5. 返回 CodePet，点击 **Sync GitHub**。

CodePet 使用 GitHub Device Flow。得到的用户 token 会保存在 macOS Keychain、
Windows Credential Locker 或 Linux 桌面钥匙串中，不会写入 `save.json`、网站或
仓库。Client ID 只是公开的应用标识，可以随安装包发布；Client Secret 绝对不能
放进桌面应用。

### 方法 B：GitHub CLI

1. 安装 [GitHub CLI](https://cli.github.com/)。
2. 在终端运行：

   ```bash
   gh auth login
   ```

3. 选择 `GitHub.com`。
4. 选择 HTTPS。
5. 在浏览器中完成登录授权。
6. 打开 CodePet Home，点击 **Sync GitHub**。

CodePet 只在同步时向 GitHub CLI 请求当前凭据，不会把凭据写入存档。

### 方法 C：开发阶段使用 fine-grained personal access token

1. 打开 GitHub 的 **Settings > Developer settings > Personal access tokens > Fine-grained tokens**。
2. Resource owner 选择自己的账户。
3. 只选择希望 CodePet 统计的仓库。
4. 只授予只读仓库权限，不要授予写入或管理权限。
5. 设置合理的过期时间。
6. 在终端设置 token 并从同一终端启动 CodePet：

   ```bash
   export GITHUB_TOKEN="github_pat_your_token_here"
   codepet-desktop
   ```

PowerShell：

```powershell
$env:GITHUB_TOKEN="github_pat_your_token_here"
codepet-desktop
```

不要把真实 token 粘贴进 README、代码、Issue、截图或 commit。如果 token 泄露，请立即在 GitHub 设置中撤销。

## GitHub 奖励规则

奖励由 GitHub 事件 ID 的哈希确定。同一个事件永远产生同一个结果，已处理的事件 ID 会保存在本地，因此重复同步不会重复获得奖励。

| GitHub 活动 | 经验值 | 金币 | 亲密度 | 食物 |
| --- | ---: | ---: | ---: | --- |
| Commit | 8–15 | 5–10 | 1–5 | 20% 概率 |
| Pull request | 12–20 | 5–10 | 2–5 | 无 |
| 创建 repository | 5–8 | 1–3 | 1–2 | 无 |

当前 API 查询会读取最近更新的前 50 个可访问仓库的默认分支 commit，以及近期 PR 和 repository contribution。拥有大量仓库的账户，后续版本需要继续增加分页。

## 商店、食物与猫狗偏好

| 食物 | 价格 | 猫的亲密度 | 狗的亲密度 |
| --- | ---: | ---: | ---: |
| 猫粮 | 15 | +3 至 +5 | -2 至 0 |
| 狗粮 | 15 | -2 至 0 | +3 至 +5 |
| 磨牙骨 | 25 | -3 至 0 | +5 至 +7 |
| 熟鸡肉 | 35 | +4 至 +7 | +4 至 +7 |
| 三文鱼 | 45 | +7 至 +10 | +3 至 +6 |
| 金枪鱼 | 60 | +9 至 +13 | +1 至 +4 |
| 庆祝大餐 | 100 | +10 至 +14 | +10 至 +14 |

价格更高的通用食物对猫狗都安全；便宜且物种倾向明显的食物，如果喂错可能降低亲密度。每种食物同时有独立的饥饿恢复值。

## 心情气泡与亲密度

小尺寸桌面气泡使用 emoji，让用户不打开管理窗口也能理解宠物状态：

- `😊` 或 `🥰`：快乐并且被照顾得很好
- `😴`：精力不足
- `😟`：开始饥饿或不开心
- `😿` / `🥺`：进入需要尽快照顾的阈值
- `💤`、`🏠`、`🌿`、`✨`：休息、回笼、自由活动和散步反馈

亲密度段位依次为 New Friends、Familiar、Friends、Best Friends、Soulmates。离线衰减按每 6 小时计算，并设置最大上限，因此长时间没启动不会在一次打开时无限扣除数值。宠物非常饥饿时可能损失有限的亲密度，但程序永远不会删除存档。

## 构建本机安装包

PyInstaller 不能跨系统构建，因此需要在目标操作系统执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[desktop,packaging]"
python scripts/build_desktop.py
```

输出文件：

- macOS：`dist/CodePet-macOS.dmg`
- Windows：`dist/CodePet-Windows.zip`
- Linux：`dist/CodePet-Linux.tar.gz`

`.github/workflows/release.yml` 会在三个操作系统分别自动构建。推送类似 `v0.4.0` 的 tag 后，GitHub Actions 会构建并把安装文件加入 GitHub Release。

### 哪些内容应该上传到 GitHub

| 内容 | 源码仓库 | GitHub Release |
| --- | --- | --- |
| 解压后的项目源码 | 是 | GitHub 会自动生成源码压缩包 |
| macOS DMG | 否 | 是，只保留一个带版本号的文件 |
| Windows ZIP / Linux TAR.GZ | 否 | 是 |
| 动画预览 GIF | 仅在文档需要展示时可选 | 否 |
| 本地输出目录、缓存和依赖 | 否 | 否 |

不要把安装包或源码 zip 当作普通仓库文件提交。源码仓库应上传解压后的项目文件，
安装程序则作为对应版本的 Release 附件。

### 维护者一次性配置：让所有用户一键登录

这是项目发布者要做一次的工作，普通用户不应该自行创建 Client ID。

1. 在你的 GitHub 账号或组织下注册一个 GitHub App。
2. 开启 **Device Flow**。
3. 只申请统计活动所需的 Metadata、Contents 和 Pull requests 读取权限，不申请
   写入或管理权限。
4. 发布前把公开 Client ID 写入 `src/codepet/build_config.py` 的
   `PUBLIC_GITHUB_CLIENT_ID`；本地开发也可以设置 `CODEPET_GITHUB_CLIENT_ID`。
5. 不要把 Client Secret 写入仓库或安装包。

如果发布者还没有配置 Client ID，应用会明确提示；开发者仍可使用 `gh auth login`
或 `GITHUB_TOKEN`。

## 正式像素动画制作规范

动画状态机与宠物品种美术分离。每个品种使用一张原创的 1024×768 透明图集，
按照 128×128 划分为 8 列、6 行，依次是待机、走路、跑步、进食、撒娇和睡觉，
每组严格 8 帧。动作速度统一定义在 `animation.py`，加载器会拒绝尺寸错误的图集，
不会悄悄显示错位帧。

完整格式见 [assets/animations/README.md](assets/animations/README.md)。要真正去除
生成式痕迹，应该在 Aseprite 中逐帧重绘并使用洋葱皮检查，统一脚掌锚点、轮廓、
明暗和运行速度。可以研究其他游戏中的动物运动规律，但不能描摹或复制其精灵、
配色、轮廓和角色设计。

首批 6 个品种现在都有通过校验的 1024×768 透明图集，共 288 个运行帧。原有静态
动作表仅作为未来新增品种缺少图集时的防御性回退。修改美术后应运行
`scripts/validate_animation_atlas.py`，并目视检查生成的 GIF 播放预览。

## 开发与测试

```bash
python -m pip install -e ".[desktop,dev]"
python -m unittest discover -s tests -v
ruff check src tests scripts
```

项目结构：

```text
domain.py      家庭、宠物、情绪、亲密度、寿命和时间衰减
catalog.py     食物价格和物种偏好
rewards.py     GitHub 事件到奖励的确定性映射
auth.py        GitHub Device Flow 与系统凭据存储
github.py      只读 GraphQL 活动客户端
storage.py     原子存档与旧版本迁移
animation.py   可复用动画片段和状态机
sprites.py     带校验的品种图集加载器及旧素材回退
overlay.py     透明桌宠窗口
dashboard.py   家庭、领养、库存和商店界面
desktop.py     应用控制器和系统托盘
packaging/     本机应用打包配置
scripts/       跨平台 Release 构建入口
tests/         规则、奖励、GitHub 解析和存档测试
```

UI 只调用领域操作，不在界面文件中计算价格、偏好或奖励。以后添加新宠物、新食物和新客户端时，应该复用现有规则，而不是写第二套平行逻辑。

生成干净的 GitHub 源码上传包：

```bash
python scripts/package_source.py outputs/CodePet-source.zip
```

该压缩包会排除虚拟环境、网站依赖、构建产物、测试缓存、嵌套 Git 数据和安装包。
上传时先解压，再把其中内容放到仓库根目录；不要把源码 zip 本身提交进仓库。

## 隐私

默认存档为 `~/.codepet/save.json`。存档包含宠物状态、库存、金币、活动日期和已处理 GitHub 事件 ID，不包含 token、密码、源代码、commit message 或仓库内容。

CodePet 不进行全局键盘或鼠标监听。只有用户主动点击宠物窗口或 CodePet 管理窗口时，应用才会收到鼠标事件。

## 贡献和许可

提交 PR 前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。所有游戏规则修改都必须配套测试，新美术必须是原创且允许重新分发。

代码采用 [MIT License](LICENSE)。原创生成式二维像素素材说明见 [ASSET-LICENSE.md](ASSET-LICENSE.md)。
