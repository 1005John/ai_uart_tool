# AI Native UART Tool — 系统设计

| 版本：v1.5 | 日期：2026-06-04 | 对应需求：REQUIREMENTS.md v1.5

## 1. 架构概览

```
┌──────────────────────────────────────────────────────┐
│                   Web UI (Gradio)                     │
│  🔌 串口控制栏（sticky 顶部）                          │
│  ┌──────────────┬──────────────┬──────────────┐       │
│  │ 📦 用例集库   │ 📋 方案管理   │ 🐛 缺陷管理   │       │
│  │ 左:用例集列表 │ 左:方案+勾选  │ 左:列表+灵畿  │       │
│  │ 右:Dataframe │ 中:用例表格   │ 右:缺陷详情   │       │
│  │              │ 右:执行日志   │              │       │
│  └──────────────┴──────────────┴──────────────┘       │
├──────────────────────────────────────────────────────┤
│                    Agent 层                           │
│  ChatSession → TestAgent / DefectAgent               │
├──────────────────────────────────────────────────────┤
│                    Engine 层                          │
│  SerialEngine / TestExecutor / ResultMatcher         │
├──────────────────────────────────────────────────────┤
│                    数据层                             │
│  SQLite (ai_uart.db) + JSON (test_sets/, test_plans/)│
├──────────────────────────────────────────────────────┤
│                    外部集成                           │
│  DeepSeek API  →  灵畿 lc CLI                        │
│  USB 串口设备 (ML307H/ML307C-DC)                      │
└──────────────────────────────────────────────────────┘
```

**数据模型**：用例集（独立编辑维护）← 方案（勾选组合，只读视图）

**核心流程**：创建用例集 → 添加用例 → 方案勾选用例集 → 执行（多轮循环）→ FAIL 自动生成缺陷 → 提交灵畿

## 2. UI 设计

### 2.1 标签页结构

| 子标签 | 区域 | 组件 |
|--------|------|------|
| 🔌 串口控制 | 固定顶部 | 端口下拉（含 AT 口自动探测标签 [AT:版本]/[DATA]/[无响应]）+ 波特率 + 连接状态 |
| 📦 用例集库 | 左 | Radio 列表 + 新建/复制/删除按钮 + 文本框 |
| | 右 | Dataframe 可编辑表格（点击行选中）→ 列: 标记/名称/AT指令/**期望值**/超时/延迟 + 保存/删除/上移/下移按钮 |
| 📋 方案管理 | 左 | Radio + 轮次/间隔 + 用例集 Checkbox（勾选即保存） |
| | 中 | Dataframe 用例表格（勾选→执行）→ 列: ☑/集名/名称/AT指令/**期望值**/超时/延迟 + 状态 |
| | 右 | Textbox 执行日志（>>>发送 / <<<接收）+ 执行后显示文件路径 |
| 🐛 缺陷管理 | 左 | Dataframe 缺陷列表 + 批量删除 + **刷新缺陷**按钮 + 灵畿提交 |
| | 右 | Markdown 缺陷详情 |

### 2.2 ChatSession — 对话会话

- **职责**：协调所有 Agent，管理对话上下文和运行时状态
- **文件**：`agents/chat_session.py`
- **核心方法**：

| 方法 | 输入 | 输出 | 说明 |
|------|------|------|------|
| handle(user_input) | 用户文本 | list[str] | 意图路由 → 委托给对应 Agent |
| build_system_prompt() | 无 | str | 动态生成含模块列表和串口状态的提示词 |

**依赖**：LLMClient、IntentRouter、SerialEngine、TestAgent、DefectAgent、KnowledgeAgent、ExcelTestLoader

### 2.2 IntentRouter — 意图路由器

- **职责**：使用 LLM 进行意图分类，正则提取参数
- **文件**：`agents/intent_router.py`
- **意图类型**：serial | test | defect | knowledge | greeting | help | unknown

### 2.3 SerialEngine — 串口引擎

- **职责**：pySerial 封装，线程安全的串口读写
- **文件**：`engines/serial_engine.py`
- **多编码支持**：`_safe_decode()` 工具函数按 UTF-8 → GBK → Latin-1 顺序尝试解码，解决中移物联模组和非 ASCII 数据的乱码问题
- **核心方法**：

| 方法 | 输入 | 输出 | 说明 |
|------|------|------|------|
| list_ports() | 无 | list[dict] | 扫描可用串口 |
| open(port, baud) | 端口号, 波特率 | bool | 打开串口 |
| send_and_wait(cmd, patterns, timeout) | AT指令, 正则列表, s | dict | 发送并等待匹配 |
| wait_for(patterns, timeout) | 正则列表, 秒 | dict | 纯等待直到匹配或超时 |

### 2.4 TestExecutor — 测试执行引擎

- **职责**：TestCase → ExecutableCase → 发送 → 匹配 → 判定 → 记录数据库
- **文件**：`engines/test_executor.py`
- **指令生成优先级**：Excel 已有 send_data → 调用 test_at_link 模块 → 参数拼接

### 2.5 ExcelTestLoader — 用例加载器

- **职责**：读取 23+ 模块的 Excel 文件，解析为 TestCase 对象
- **文件**：`engines/excel_loader.py`
- **模块映射**：MODULE_MAP 字典（模块名 → Excel 文件名 + 命令模块）

### 2.6 DefectAgent — 缺陷管理

- **职责**：AI 生成缺陷报告，本地存储（SQLite+JSON），灵畿同步
- **文件**：`agents/defect_agent.py` + `defect/`

### 2.7 KnowledgeAgent — 知识图谱

- **职责**：从测试结果提取三元组，查询历史失败、模组能力、错误码
- **文件**：`agents/knowledge_agent.py` + `knowledge/`

### 2.8 LLMClient — AI 客户端

- **职责**：DeepSeek/阿里云 API 封装，密钥从 `~/.ai_uart_keys.json` 安全加载
- **文件**：`llm/llm_client.py`

## 3. 数据模型

### 3.1 核心实体

```
TestPlan (方案)
  └── TestSet (用例集) *
        └── TestCase (用例) *
              └── ExecutableCase (AT 指令)
                    └── TestCaseRun (执行结果) → 判定 PASS/FAIL

TestCaseRun (FAIL) → LocalDefect (本地缺陷) → 灵畿缺陷
PASS/FAIL 结果 → KnowledgeTriple (知识三元组)
```

### 3.2 数据库表

| 表名 | 关键字段 | 说明 |
|------|----------|------|
| test_sessions | name, module, port, status, passed, failed | 测试会话 |
| test_case_runs | session_id, case_name, at_command, actual_result, status | 用例执行记录 |
| local_defects | title, description, status, lingji_id | 本地缺陷 |
| knowledge_triples | subject, predicate, object, confidence | 知识图谱 |

### 3.3 JSON 文件

| 路径 | 内容 |
|------|------|
| data/test_plans/*.json | 方案（名称、用例集列表、循环次数） |
| data/test_sets/*.json | 用例集（用例数组） |
| defects/defect_NNNN.json | 单个缺陷的 JSON 导出 |
| data/last_exec_result.json | 最近一次执行结果缓存 |

## 4. 接口设计

### 4.1 内部接口

- ChatSession 通过 IntentRouter 分派意图，委托给对应 Agent
- TestExecutor 依赖 SerialEngine（发送/接收）+ ExcelLoader（加载用例）+ ResultMatcher（结果判定）
- DefectAgent 依赖 LocalDefectStore（本地存储）+ LingjiSync（灵畿 CLI）
- KnowledgeAgent 依赖 KnowledgeStore（三元组提取）+ KnowledgeQuerier（查询）

### 4.2 外部接口

| 接口 | 协议 | 说明 |
|------|------|------|
| DeepSeek API | HTTPS | `/chat/completions`，401 认证 |
| 阿里云通义千问 API | HTTPS | `/chat/completions`，Bearer 认证 |
| 灵畿 lc CLI | subprocess | `lc bug create/list/view/delete` 等 |
| USB 串口 | UART | 通过 pySerial 读写 |

## 5. 关键决策

| 决策 | 原因 | 替代方案（已否决） |
|------|------|-------------------|
| Web UI 选 Gradio | Python 原生，零前端代码，适合工具类应用 | Flask+Vue（太重） |
| SQLite 而非 PostgreSQL | 单机运行，零配置部署 | PostgreSQL（需要额外服务） |
| 密钥外置到 ~/.ai_uart_keys.json | 项目开源安全 | 环境变量（不方便多 key 管理） |
| 灵畿通过 CLI 而非 API | 灵畿不提供 REST API | — |
| 串口端口名不做路径改写 | pyserial 原生接受各平台格式（COM3 / /dev/ttyUSB0） | 按平台分支处理（太复杂） |
| lc 查找用 shutil.which() | 替代 subprocess(["which"])，跨平台 | — |
