# Super Study 中文使用指南

Super Study 是一个面向软件工程学习与面试准备的 Codex Skill。它不会一次性倾倒整套知识，而是通过渐进式提问定位薄弱点，再从原理、实现、调试、边界、权衡、安全与迁移应用等角度逐层验证，直到形成可观察的掌握证据。

支持的主要方向包括前端、后端、数据库、数据工程、AI、Agent、计算机网络与网络安全。默认关注实际项目中常见的困难和高频概念，不追逐冷门 trivia；如果职位描述或项目确实要求某个细分领域，才会提高其优先级。

## 安装

最简单的方式是把本仓库链接交给 Codex：

```text
请从下面的仓库安装 super-study Skill：
https://github.com/Loffee5422/super-study/tree/main/skills/super-study
```

也可以手动把 `skills/super-study` 文件夹复制到个人 Skill 目录：

```text
Windows: %USERPROFILE%\.codex\skills\super-study
macOS/Linux: ~/.codex/skills/super-study
```

安装完成后重启 Codex，让 Skill 列表刷新。

## 基本使用

明确调用：

```text
使用 $super-study 帮我彻底掌握 React 渲染机制，用于前端面试。
```

针对职位描述：

```text
使用 $super-study 分析这份 JD，优先学习面试最可能考察、项目中最容易出问题的部分：[粘贴 JD]
```

针对 GitHub 或本地项目：

```text
使用 $super-study 深挖这个项目，确保我能解释架构、关键实现、技术选择、故障场景和个人贡献：[仓库链接或文件夹]
```

行为面试：

```text
使用 $super-study 帮我从真实经历中构建行为面试答案，不要虚构信息，并继续追问薄弱点。
```

你可以提供以下任意学习来源：

- GitHub 仓库；
- 本地项目文件夹或单个文件；
- 网页、文档或论文链接；
- 职位描述；
- 简历项目；
- 直接指定一个 Topic。

没有提供来源时，Skill 默认优先使用可用的 MCP 或连接器搜索，再使用官方文档、标准、规范、原始论文与仓库源码。

## 学习过程

一次学习通常遵循下面的循环：

1. 明确学习目标与面试场景；
2. 用一个回忆题或真实场景诊断当前理解；
3. 针对暴露出的精确缺口逐步提示；
4. 必要时给出简短解释、代码追踪、实验或图示；
5. 换一个新场景重新测试，避免只记住刚才的答案；
6. 继续追问机制、边界、失败、权衡、安全和迁移应用；
7. 通过无提示模拟面试形成最终证据。

“我懂了”不会被当成掌握。Skill 会分别检查：自主解释、因果机制、实现或调试、边界与误区、替代方案与权衡、安全影响、陌生场景迁移、连续面试追问与 teach-back。

你随时可以暂停。启用 Obsidian 后，下一次会从准确的未解决分支继续，而不是从头重新学习。

## 可选的 Obsidian 学习档案

Obsidian 不是必需的。它只负责持久化状态；提问、判断、检索和教学始终由 Codex 执行。

```powershell
python skills/super-study/scripts/super_study.py configure `
  --vault "D:\path\to\your\vault" --consent --create
python skills/super-study/scripts/super_study.py init
python skills/super-study/scripts/super_study.py validate
```

Vault 结构：

```text
00 Home/       人类可读的入口、导航和说明
10 Topics/     学习地图、范围和掌握契约
20 Concepts/   可跨 Topic 复用的规范化概念
30 Sessions/   每次学习的证据与断点
40 Sources/    来源、版本和 Git commit 信息
50 Reviews/    复习记录与检索证据
60 Targets/    JD 与面试目标
90 Templates/  可复用笔记模板
.super-study/  可重建机器索引
```

每次不会导入全部文件。Skill 先读取很小的导航与索引，再按需加载当前 Topic、最近 Session，以及少量相关 Concept 或 Source。Markdown 是事实来源，机器索引只是可重建缓存。

## Concept 如何避免重复

创建 Concept 前会先运行候选解析，并综合规范名称、别名、技术域、上位概念与摘要判断：

- 同一个概念：复用已有 Concept；
- 同名但语义不同：添加明确的作用域；
- 真正的新概念：创建新的稳定 ID；
- 旧名称：保留为 alias，避免历史链接失效。

因此不会依赖文件名猜测，也不需要每次把所有 Concept 塞进上下文。

## 隐私与安全

- 默认只读分析用户提供的代码仓库；
- 未得到明确授权时，不会向项目写入或推送修改；
- Vault 路径与写入许可保存在本机配置中，不进入本仓库；
- 不要把密码、Token、私有 JD 或敏感公司资料提交到公开仓库；
- 网络安全练习只应针对你拥有或明确获授权的隔离环境。

遇到问题请提交 [Issue](https://github.com/Loffee5422/super-study/issues)。
