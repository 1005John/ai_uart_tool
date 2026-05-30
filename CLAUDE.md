# AI Native UART Tool

基于 AI 的 UART AT 指令测试工具，支持 Windows / macOS / Linux (树莓派/Ubuntu/Debian)。

## 架构

```
webui.py (Gradio 6.15)  ← 主入口
  ├── agents/           ← Agent 层：对话、测试、缺陷、知识图谱
  ├── engines/          ← 串口引擎、测试执行器、结果匹配
  ├── llm/              ← DeepSeek V4 Flash 客户端
  ├── models/           ← SQLite 数据模型、测试方案管理
  ├── defect/           ← 本地缺陷存储 + 灵畿平台同步
  ├── knowledge/        ← 知识图谱
  └── test_at_link/     ← AT 指令集（27个通信模块）
```

## ⚠️ 代码修改必做

每次代码修改完成后：
1. 检查 `REQUIREMENTS.md` — 功能需求状态是否需要更新
2. 检查 `DESIGN.md` — 架构/模块/决策是否需要同步
3. 检查 `CHANGELOG.md` — 记录本次变更
4. 三者有变化立即更新并提交

## 启动

```bash
cd /Volumes/DevDrive/projects/ai_uart_tool
source venv/bin/activate
python webui.py
# 浏览器访问 http://localhost:7860
```

## 外置硬盘提醒

此项目在 DevDrive 外置硬盘上。离开前务必 `git push`。

## 密钥管理

API Key 不存储在项目内。真实密钥在 `~/.ai_uart_keys.json`（Mac mini 内置硬盘）。
首次 clone 后，手动将密钥文件复制到 `~/.ai_uart_keys.json` 即可运行。
