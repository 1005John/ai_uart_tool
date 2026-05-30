# AI Native UART Tool

基于 AI 的 UART AT 指令测试工具，运行在树莓派 5 / Ubuntu 上。

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

## 启动

```bash
cd /Volumes/DevDrive/projects/ai_uart_tool
source venv/bin/activate
python webui.py
# 浏览器访问 http://localhost:7860
```

## 外置硬盘提醒

此项目在 DevDrive 外置硬盘上。离开前务必 `git push`。
