# AI Native UART Tool

物联网蜂窝模组（ML307H/ML307C-DC）的 AI 驱动 AT 指令自动化测试工具。

## 功能简介

- **串口控制** — 扫描、打开、断开串口，发送 AT 指令并自动匹配响应
- **测试方案管理** — 三级结构（方案→用例集→用例），23+ 通信模块
- **AI 驱动测试** — DeepSeek 意图识别、自动生成缺陷报告、失败分析
- **缺陷管理** — FAIL 自动生成本地缺陷，一键提交到灵畿平台
- **知识图谱** — 自动积累历史测试数据，支持相似失败查询

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| Web UI | Gradio 6.15 | 四标签页：对话/测试/缺陷/知识 |
| AI | DeepSeek V4 Flash | 意图分类、缺陷生成、知识问答 |
| 串口 | pySerial 3.5 | AT 指令收发、正则匹配 |
| 数据 | SQLite + JSON | 测试会话、用例执行记录、缺陷、知识图谱 |
| 外部平台 | 灵畿 lc CLI | 缺陷提交与同步 |

## 快速开始

```bash
git clone git@github.com:1005John/ai_uart_tool.git
cd ai_uart_tool
python3 -m venv venv
source venv/bin/activate
pip install gradio pyserial pandas openpyxl httpx
python webui.py
# → http://localhost:7860
```

## 目录结构

```
ai_uart_tool/
├── webui.py              ← Gradio Web UI 主入口
├── main.py               ← CLI 入口（scan/modules/plan/quick/chat）
├── agents/               ← ChatSession, IntentRouter, Test/Defect/KnowledgeAgent
├── engines/              ← SerialEngine, TestExecutor, ExcelLoader, ResultMatcher
├── models/               ← schemas, database, test_plan_manager
├── llm/                  ← DeepSeek API 客户端 + 提示词模板
├── defect/               ← 本地缺陷存储 + 灵畿同步
├── knowledge/            ← 知识图谱存储 + 查询引擎
├── test_at_link/common/  ← 27 个 AT 指令模块
├── test_data/            ← 23+ Excel 测试配置文件
├── config/               ← 配置模板（真实密钥在 ~/.ai_uart_keys.json）
├── data/                 ← 运行时数据（DB + JSON）
└── defects/              ← 缺陷 JSON 导出
```

## 部署

树莓派 5 / Ubuntu / Debian，需 Python 3.10+ 和 USB 串口设备。
CLI 模式可用 `python main.py chat` 在终端直接交互。
