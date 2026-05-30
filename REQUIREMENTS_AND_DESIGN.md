# AI Native UART Tool — 需求与设计文档

> 版本：v1.0 | 日期：2026-05-30 | 基于源码逆向整理

---

## 目录

1. [项目概述](#1-项目概述)
2. [功能需求](#2-功能需求)
3. [非功能需求](#3-非功能需求)
4. [系统架构](#4-系统架构)
5. [模块详细设计](#5-模块详细设计)
6. [数据模型](#6-数据模型)
7. [接口设计](#7-接口设计)
8. [部署与运行](#8-部署与运行)
9. [待完善项](#9-待完善项)

---

## 1. 项目概述

### 1.1 一句话描述

**AI Native UART Tool** 是一个面向物联网蜂窝模组（ML307H/ML307C-DC 等）的 AI 驱动的 AT 指令自动化测试工具，支持 Web UI 交互、串口实时通信、缺陷管理与平台同步、知识图谱构建。

### 1.2 核心价值

| 痛点 | 解决方案 |
|------|----------|
| AT 指令测试依赖手工逐条发送和人工判读 | 从 Excel 用例库自动加载、批量执行、自动匹配结果 |
| 测试失败后需要手动撰写缺陷报告 | AI（DeepSeek）自动分析失败原因、生成缺陷描述 |
| 缺陷需要在灵畿平台手动录入 | 自动同步本地缺陷到灵畿，双向追踪 |
| 历史测试经验无法复用 | 知识图谱自动积累，支持相似失败查询 |
| 跨模块测试用例管理混乱 | 三级结构（方案→用例集→用例）清晰管理 |

### 1.3 技术栈

| 层级 | 技术 | 版本/说明 |
|------|------|----------|
| Web 框架 | Gradio | 6.15.0 |
| AI 引擎 | DeepSeek API | V4 Flash (deepseek-v4-flash) |
| 串口通信 | pySerial | 3.5+ |
| 数据库 | SQLite | 本地文件 (data/ai_uart.db) |
| Excel 解析 | openpyxl | 最新 |
| 外部 CLI | 灵畿 lc | @lingji/lc@0.3.2 (Node.js) |
| 目标平台 | 树莓派 5 / Ubuntu / macOS | Python 3.10+ |

---

## 2. 功能需求

### 2.1 串口控制（FR-SERIAL）

| ID | 需求 | 状态 |
|----|------|------|
| FR-SERIAL-01 | 扫描并列出所有可用串口 | ✅ 已实现 |
| FR-SERIAL-02 | 打开指定串口（支持自定义波特率） | ✅ 已实现 |
| FR-SERIAL-03 | 断开串口连接 | ✅ 已实现 |
| FR-SERIAL-04 | 发送 AT 指令并等待响应（模式匹配） | ✅ 已实现 |
| FR-SERIAL-05 | 支持 ASCII 和 HEX 两种发送模式 | ✅ 已实现 |
| FR-SERIAL-06 | 自动检测 USB 串口 | ✅ 已实现 (🔵 标记) |

### 2.2 测试方案管理（FR-PLAN）

| ID | 需求 | 状态 |
|----|------|------|
| FR-PLAN-01 | 创建/删除测试方案 | ✅ 已实现 |
| FR-PLAN-02 | 方案内包含多个用例集（三层下钻） | ✅ 已实现 |
| FR-PLAN-03 | 用例集内可新增/编辑/删除用例 | ✅ 已实现 |
| FR-PLAN-04 | 方案支持配置循环执行次数 | ✅ 已实现 |
| FR-PLAN-05 | 双击表格单元格编辑用例 | ✅ 已实现 |

### 2.3 测试执行（FR-EXEC）

| ID | 需求 | 状态 |
|----|------|------|
| FR-EXEC-01 | 从 23+ 模块的 Excel 文件加载测试用例 | ✅ 已实现 |
| FR-EXEC-02 | 支持按模组型号、用例级别(P0/P1/P2)筛选 | ✅ 已实现 |
| FR-EXEC-03 | AT 指令自动生成（调用 test_at_link 模块） | ✅ 已实现 |
| FR-EXEC-04 | 逐条执行并实时显示进度 | ✅ 已实现 |
| FR-EXEC-05 | 自动匹配预期结果（正则） | ✅ 已实现 |
| FR-EXEC-06 | 执行结果持久化到 SQLite | ✅ 已实现 |
| FR-EXEC-07 | 自动读取模组版本信息（ATI） | ✅ 已实现 |

### 2.4 缺陷管理（FR-DEFECT）

| ID | 需求 | 状态 |
|----|------|------|
| FR-DEFECT-01 | FAIL 用例自动生成本地缺陷 | ✅ 已实现 |
| FR-DEFECT-02 | AI 自动生成缺陷标题和描述 | ✅ 已实现 |
| FR-DEFECT-03 | 批量提交缺陷到灵畿平台 | ✅ 已实现 |
| FR-DEFECT-04 | 获取灵畿项目列表和责任人 | ✅ 已实现 |
| FR-DEFECT-05 | 本地缺陷与灵畿 ID 双向关联 | ✅ 已实现 |
| FR-DEFECT-06 | 已提交灵畿的缺陷禁止本地删除 | ✅ 已实现 |
| FR-DEFECT-07 | 多维筛选（型号/版本/标题/日期范围） | ✅ 已实现 |

### 2.5 AI 对话（FR-CHAT）

| ID | 需求 | 状态 |
|----|------|------|
| FR-CHAT-01 | 自然语言意图识别（串口/测试/缺陷/知识） | ✅ 已实现 |
| FR-CHAT-02 | 自然语言触发测试执行 | ✅ 已实现 |
| FR-CHAT-03 | 快捷按钮（MQTT计划/TCP计划/知识统计） | ✅ 已实现 |
| FR-CHAT-04 | CLI 对话模式（非 WebUI） | ✅ 已实现 |

### 2.6 知识图谱（FR-KG）

| ID | 需求 | 状态 |
|----|------|------|
| FR-KG-01 | 从测试结果自动提取三元组 | ✅ 已实现 |
| FR-KG-02 | 相似失败查询 | ✅ 已实现 |
| FR-KG-03 | 模组能力矩阵查询 | ✅ 已实现 |
| FR-KG-04 | 错误码解释（LLM 增强） | ✅ 已实现 |
| FR-KG-05 | 缺陷提交自动导入知识图谱 | ✅ 已实现 |

---

## 3. 非功能需求

| ID | 需求 | 目标 | 状态 |
|----|------|------|------|
| NFR-01 | 单条用例执行超时 | 默认 10s，可配置 | ✅ |
| NFR-02 | LLM API 调用超时 | 30s | ✅ |
| NFR-03 | 灵畿 CLI 调用超时 | 30s | ✅ |
| NFR-04 | 对话历史保留 | 最多 50 条 | ✅ |
| NFR-05 | 数据库并发安全 | WAL 模式 + 5s 锁超时 | ✅ |
| NFR-06 | 串口连接异常处理 | try-catch + 可读错误提示 | ✅ |
| NFR-07 | 缺陷提交限流 | 每条间隔 0.5s | ✅ |
| NFR-08 | Mock 模式 | 无串口时可模拟运行 | ❌ 未实现 |

---

## 4. 系统架构

### 4.1 分层架构

```
┌─────────────────────────────────────────────┐
│                  Web UI 层                    │
│         webui.py (Gradio 6.15)               │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌────────────┐  │
│  │ 💬对话│ │📋测试 │ │🐛缺陷 │ │📊知识图谱   │  │
│  └──────┘ └──────┘ └──────┘ └────────────┘  │
├─────────────────────────────────────────────┤
│                Agent 层                       │
│  ┌───────────┐  ┌──────────┐  ┌──────────┐  │
│  │ChatSession │  │TestAgent │  │DefectAgent│  │
│  │IntentRouter│  │          │  │           │  │
│  └───────────┘  └──────────┘  └──────────┘  │
│  ┌──────────────┐                            │
│  │KnowledgeAgent│                            │
│  └──────────────┘                            │
├─────────────────────────────────────────────┤
│              引擎层（Engines）                 │
│  ┌───────────┐ ┌────────────┐ ┌──────────┐  │
│  │SerialEngine│ │TestExecutor│ │ExcelLoader│  │
│  │(pyserial)  │ │            │ │(openpyxl) │  │
│  └───────────┘ └────────────┘ └──────────┘  │
│  ┌──────────────┐                            │
│  │ResultMatcher │                            │
│  └──────────────┘                            │
├─────────────────────────────────────────────┤
│              数据层                           │
│  ┌────────┐ ┌────────────┐ ┌─────────────┐  │
│  │SQLite  │ │ JSON 文件   │ │Excel 测试数据│  │
│  │ai_uart │ │test_plans/ │ │test_data/   │  │
│  │.db     │ │test_sets/  │ │23+ .xlsx    │  │
│  └────────┘ └────────────┘ └─────────────┘  │
├─────────────────────────────────────────────┤
│              外部集成                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │DeepSeek  │  │灵畿 CLI   │  │USB 串口    │   │
│  │API       │  │(lc)       │  │设备        │   │
│  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────┘
```

### 4.2 核心数据流

```
┌─────────┐   ┌──────────┐   ┌───────────┐   ┌────────┐
│ 选择模块  │──→│ 加载Excel │──→│ 生成用例列表│──→│ 勾选导入 │
└─────────┘   └──────────┘   └───────────┘   └────────┘
                                                  │
                                                  ▼
┌─────────┐   ┌──────────┐   ┌───────────┐   ┌────────┐
│ 查看结果  │←──│ 自动匹配  │←──│ 逐条执行   │←──│ 测试集  │
└────┬────┘   └──────────┘   └───────────┘   └────────┘
     │
     ▼ (FAIL)
┌─────────┐   ┌──────────┐   ┌───────────┐
│ 生成缺陷  │──→│ 提交灵畿  │──→│ 知识图谱   │
└─────────┘   └──────────┘   └───────────┘
```

### 4.3 意图路由流程

```
用户输入
    │
    ▼
┌──────────────┐
│ IntentRouter │──→ LLM 分类
└──────────────┘
    │
    ├── greeting  ──→ 问候回复
    ├── help      ──→ 帮助文本
    ├── serial    ──→ 扫描/打开/关闭串口
    ├── test      ──→ 生成计划/执行测试
    ├── knowledge ──→ 知识图谱查询
    ├── defect    ──→ 缺陷CRUD/提交灵畿
    └── unknown   ──→ LLM 自由对话
```

---

## 5. 模块详细设计

### 5.1 webui.py — Web UI 主入口

**职责：** Gradio 界面构建 + 全局状态管理

**全局状态：**

| 变量 | 类型 | 说明 |
|------|------|------|
| `_source_cases` | list[TestCase] | 仓库模块加载的用例 |
| `_custom_cases` | list[TestCase] | 自定义用例 |
| `_suite_cases` | list[TestCase] | 当前测试集的用例 |
| `_DEFECT_CACHE` | list[dict] | 缺陷列表缓存（行点击映射） |
| `_selected_plan` | str | 当前选中的方案名 |
| `_selected_set` | str | 当前选中的用例集名 |

**四个标签页：**
1. **💬 对话** — 聊天区 + 串口控制面板（右侧栏）
2. **📋 测试方案** — 三框下钻（方案列表→用例集→用例）
3. **🐛 缺陷管理** — 多维筛选 + 缺陷表格 + 灵畿提交
4. 知识图谱查询功能散落在对话和缺陷页面中，无独立标签页。

### 5.2 ChatSession — 对话会话管理

**文件：** `agents/chat_session.py`

**职责：** 协调所有 Agent，管理对话上下文

```
ChatSession
├── llm: LLMClient          ← DeepSeek API
├── router: IntentRouter    ← 意图分类
├── serial: SerialEngine    ← 串口通信
├── loader: ExcelTestLoader ← Excel 用例加载
├── test_agent: TestAgent   ← 测试生成与执行
├── defect_agent: DefectAgent ← 缺陷管理
├── knowledge_agent: KnowledgeAgent ← 知识查询
├── messages: list          ← 对话历史 (最多50条)
└── context: dict           ← 运行时状态
    ├── port, baudrate      ← 串口配置
    ├── model               ← 模组型号
    ├── current_plan        ← 当前测试计划
    └── current_result      ← 最近执行结果
```

**支持两种模式：**
- **Web UI 模式** — 通过 `handle()` 接收用户输入，返回响应列表
- **CLI 模式** — `main()` 提供终端交互式对话

### 5.3 IntentRouter — 意图路由器

**文件：** `agents/intent_router.py`

使用 LLM 进行意图分类（`INTENT_CLASSIFICATION_PROMPT`），正则提取参数。

**意图类型：** `serial | test | defect | knowledge | greeting | help | unknown`

**参数提取：**
- 测试：模块名（中英文匹配）、测试级别（P0/P1）、模组型号
- 串口：端口号、波特率、操作类型（打开/关闭/扫描）
- 知识：AT 指令正则匹配

### 5.4 SerialEngine — 串口引擎

**文件：** `engines/serial_engine.py`

**核心方法：**

| 方法 | 说明 |
|------|------|
| `list_ports()` | 扫描可用串口 |
| `open(port, baudrate)` | 打开串口 |
| `close()` | 关闭串口（含流式接收线程清理） |
| `send(data)` | 发送数据 |
| `send_at(at_command)` | 发送 AT 指令（自动加 \r\n） |
| `read(size)` | 读取数据 |
| `send_and_wait(command, patterns, timeout)` | 发送并等待匹配 |
| `wait_for(patterns, timeout)` | 等待直到匹配正则或超时 |
| `start_stream(callback)` | 启动后台流式接收 |

**关键设计：**
- 线程安全（`threading.Lock`）
- 支持模式匹配（正则列表，任一匹配即成功）
- 超时控制（默认 5s）
- 日志输出（`[Serial] >>>` / `[Serial] <<<`）

### 5.5 ExcelTestLoader — Excel 用例加载器

**文件：** `engines/excel_loader.py`

**支持 23 个模块：**

| 模块 | 说明 | Excel 文件 |
|------|------|-----------|
| mqtt | MQTT协议测试 | mqtt_test_configs.xlsx |
| mqttcfg | MQTT配置测试 | mqttcfg_test_configs.xlsx |
| tcp | TCP协议测试 | tcp_test_configs.xlsx |
| http | HTTP协议测试 | http_test_configs.xlsx |
| sms | 短信功能测试 | sms_test_configs.xlsx |
| gnss | GNSS定位测试 | gnss_test_configs.xlsx |
| fota | FOTA升级测试 | fotacfg_test_configs.xlsx |
| ssl | SSL/TLS测试 | mssl_test_configs.xlsx |
| dns | DNS解析测试 | dns_test_configs.xlsx |
| ntp | NTP时间同步 | ntp_test_configs.xlsx |
| ftp | FTP文件传输 | mftp_test_configs.xlsx |
| wifi | WiFi测试 | wifi_test_configs.xlsx |
| gpio | GPIO测试 | mgpio_test_configs.xlsx |
| dialup | 拨号测试 | dialup_test_configs.xlsx |
| sim | SIM卡测试 | sms_test_configs.xlsx |
| networkservice | 网络服务测试 | networkservice_test_configs.xlsx |
| packet_domain | PDP上下文测试 | packet_domain_test_configs.xlsx |
| dmp | 设备管理测试 | dmp_test_configs.xlsx |
| adc | ADC测试 | adc_test_configs.xlsx |
| pm | 电源管理测试 | pmcfg_test_configs.xlsx |
| me_control | ME控制测试 | me_control_command_test_configs.xlsx |
| extended | 扩展AT指令测试 | extended_command_test_configs.xlsx |
| mled | LED灯测试 | mled_test_configs.xlsx |
| mping | 网络Ping测试 | mping_test_configs.xlsx |

**关键设计：**
- 模块名→文件名映射 (`MODULE_MAP`)
- 表头标准化 (`_normalize_header`)
- Excel 行→TestCase dataclass
- 支持模组型号过滤（`ALL` / `ALL|excluded` / 特定型号）
- Workbook 缓存避免重复打开

### 5.6 TestExecutor — 测试执行引擎

**文件：** `engines/test_executor.py`

**核心流程：**
```
TestCase → _generate_command() → ExecutableCase
    → serial.send_at() → serial.wait_for()
    → ResultMatcher.match() → 判定 PASS/FAIL
    → add_case_run() 记录到 DB
    → 回调通知 UI
```

**指令生成策略（优先级）：**
1. 若 params 中有 `send_data` → 直接使用
2. 调用 `test_at_link/common/command_*.py` 的 `set_*` 函数生成真实 AT 指令
3. 降级：按 key=value 拼接

**指令模块映射（`_call_command_module`）：**
- sheet 名 -> module_name 映射（27 个前缀 → 17 个模块）
- 参数别名（Excel 字段名 → 函数参数名）
- 反射调用 `set_*` 函数

### 5.7 ResultMatcher — 结果匹配器

**文件：** `engines/result_matcher.py`

| 方法 | 说明 |
|------|------|
| `match(response, patterns)` | 正则匹配 |
| `has_error(response)` | 检测 ERROR / +CME ERROR / +CMS ERROR |

### 5.8 DefectAgent — 缺陷管理 Agent

**文件：** `agents/defect_agent.py`

**功能：**
- `generate_description()` — LLM 生成标准缺陷报告
- `generate_title()` — 生成缺陷标题
- `create_local()` — 创建本地缺陷（SQLite + JSON）
- `submit_to_lingji()` — 提交单个缺陷到灵畿
- `submit_batch()` — 批量提交（间隔 0.5s 防限流）
- `sync_check()` — 校验本地与灵畿一致性

### 5.9 KnowledgeAgent — 知识图谱 Agent

**文件：** `agents/knowledge_agent.py`

**查询优先级：**
1. 统计概览 → `get_statistics()`
2. 模组能力 → `get_model_capabilities()`
3. 错误码查询 → `find_similar_failures()` + LLM 解释
4. AT 指令查询 → `find_errors_for_command()`
5. 自由搜索 → `search()`
6. 兜底 → LLM 自由回答

### 5.10 LLMClient — DeepSeek API 客户端

**文件：** `llm/llm_client.py`

| 参数 | 值 |
|------|-----|
| API Key | 硬编码在 `config/config.json` |
| Base URL | `https://api.deepseek.com/v1` |
| Model | `deepseek-v4-flash` |
| 超时 | 30s |
| 默认 temperature | 0.3 |
| 默认 max_tokens | 2048 |

**⚠️ 安全风险：** API Key 明文存储在 `config/config.json` 中，已提交到 Git 仓库。需要立即处理。

### 5.11 LingjiSync — 灵畿平台同步

**文件：** `defect/lingji_sync.py`

**核心方法：**

| 方法 | 说明 |
|------|------|
| `check_login()` | 校验登录状态 (`lc checkin`) |
| `login(token)` | 登录 (`lc login`) |
| `create_bug(title, desc, ...)` | 创建缺陷 (先关闭只读模式 → `lc bug create` → 标题搜索获取 ID) |
| `list_bugs(limit)` | 列出灵畿缺陷 (`lc bug list --pretty`) |
| `get_bug(bug_id)` | 查看缺陷详情 (`lc bug view`) |
| `delete_bug(bug_id)` | 删除缺陷 |
| `list_projects()` | 获取项目列表 (`lc space project linked`) |
| `list_handlers()` | 提取责任人列表 |

**关键设计：**
- `bug create` 不返回 ID，通过标题关键字搜索获取（延迟 1.5s 等索引）
- 使用 `NODE_EXTRA_CA_CERTS` 环境变量配置证书
- 默认 workspace: `CMIOTonemoredcap`

---

## 6. 数据模型

### 6.1 SQLite 表结构

#### test_sessions（测试会话）

| 列 | 类型 | 说明 |
|----|------|------|
| id | INTEGER PK | 自增主键 |
| name | TEXT | 会话名称 |
| module | TEXT | 测试模块 |
| port | TEXT | 串口号 |
| baudrate | INTEGER | 波特率 |
| model | TEXT | 模组型号 |
| case_level | TEXT | 用例级别 |
| status | TEXT | running/completed |
| total_cases | INTEGER | 总用例数 |
| passed | INTEGER | 通过数 |
| failed | INTEGER | 失败数 |
| started_at | TIMESTAMP | 开始时间 |
| ended_at | TIMESTAMP | 结束时间 |
| summary | TEXT | 结果摘要 |

#### test_case_runs（用例执行记录）

| 列 | 类型 | 说明 |
|----|------|------|
| id | INTEGER PK | 自增主键 |
| session_id | INTEGER FK | 关联 test_sessions |
| sheet_name | TEXT | Excel Sheet 名 |
| case_name | TEXT | 用例名称 |
| case_level | TEXT | P0/P1/P2 |
| at_command | TEXT | 实际发送的 AT 指令 |
| expected_result | TEXT | 预期结果 |
| actual_result | TEXT | 实际返回 |
| duration_ms | INTEGER | 执行耗时 |
| status | TEXT | PASS/FAIL/ERROR/PENDING |
| fail_reason | TEXT | 失败原因 |
| ai_analysis | TEXT | AI 分析 |

#### local_defects（本地缺陷）

| 列 | 类型 | 说明 |
|----|------|------|
| id | INTEGER PK | 自增主键 |
| title | TEXT | 缺陷标题 |
| description | TEXT | 缺陷描述 |
| severity | INTEGER | 严重程度 1-4 |
| priority | INTEGER | 优先级 1-3 |
| status | TEXT | local/submitted/synced |
| lingji_id | TEXT | 灵畿缺陷 ID |
| test_session_id | INTEGER FK | 关联测试会话 |
| created_at | TIMESTAMP | 创建时间 |
| submitted_at | TIMESTAMP | 提交时间 |

#### knowledge_triples（知识图谱三元组）

| 列 | 类型 | 说明 |
|----|------|------|
| id | INTEGER PK | 自增主键 |
| subject | TEXT | 主体（模组/指令/错误码） |
| predicate | TEXT | 关系（执行指令/返回错误/根因/测试通过） |
| object | TEXT | 客体 |
| context | TEXT | 上下文 JSON |
| confidence | REAL | 置信度 0-1 |
| source | TEXT | 来源 |
| session_id | INTEGER | 关联会话 |

### 6.2 Python Dataclass

```
TestCase → Excel 行 → 测试用例定义
ExecutableCase → 已转换 AT 指令的用例
TestPlan → 测试计划（含用例列表）
TestCaseRun → 单次执行结果
TestResult → 批量执行结果汇总
```

### 6.3 JSON 文件结构

```
data/
├── test_plans/          ← 方案 (name_plan.json)
│   └── {name, created, loop_count, global_delay, test_set_names[]}
├── test_sets/           ← 测试集 (name_set.json + name_cases.json)
│   └── {name, created, case_count, cases[{source, at_cmd, ...}]}
├── custom_cmds/         ← 自定义指令库
│   └── custom_cmds.json
└── last_exec_result.json ← 最近执行结果

defects/                 ← 缺陷 JSON 导出 (defect_NNNN.json)
```

---

## 7. 接口设计

### 7.1 DeepSeek API

```
POST https://api.deepseek.com/v1/chat/completions
Headers: Authorization: Bearer {api_key}
Body: {
  "model": "deepseek-v4-flash",
  "messages": [...],
  "temperature": 0.3,
  "max_tokens": 2048,
  "stream": false
}
```

**调用场景：**
- 意图分类 (temperature=0.1, max_tokens=50)
- 缺陷描述生成 (temperature=0.2, max_tokens=1024)
- 失败分析 (FAIL_ANALYSIS_PROMPT)
- 知识问答兜底 (temperature=0.3, max_tokens=512)
- 自由对话 (temperature=0.5, max_tokens=1024)

### 7.2 灵畿 CLI 接口

```
lc checkin                              ← 登录校验
lc login <token>                        ← 登录
lc readonly off --duration 5m           ← 关闭只读模式
lc bug create -t <title> -D <desc> ...  ← 创建缺陷
lc bug list -w <workspace> -l <limit>    ← 列出缺陷
lc bug view <id> -w <workspace>         ← 查看缺陷
lc bug delete <id> -w <workspace> --yes  ← 删除缺陷
lc space project linked --workspace-key <ws> --size 50  ← 列出项目
```

### 7.3 Gradio UI 事件流

```
用户操作 → Gradio Event → Python Handler → 返回更新 UI 组件

关键事件链：
  plan_table.select → on_plan_select → 刷新 set_table + set_header
  set_table.select → on_set_select → 刷新 case_table + case_header
  exec_plan_btn.click → do_exec_plan → 执行测试循环
  defect_table.select → view_defect_by_row_fn → 显示缺陷详情
```

---

## 8. 部署与运行

### 8.1 环境要求

| 组件 | 要求 |
|------|------|
| Python | 3.10+ |
| pip 包 | gradio>=6.15.0, pyserial>=3.5, pandas>=2.0, openpyxl, httpx |
| Node.js (可选) | @lingji/lc@0.3.2 |
| OS | 树莓派 5 / Ubuntu / Debian / macOS |

### 8.2 启动

```bash
cd ai_uart_tool
source venv/bin/activate
python webui.py
# → http://localhost:7860
```

### 8.3 CLI 模式

```bash
python main.py scan          # 扫描串口
python main.py modules       # 列出模块
python main.py plan mqtt     # 预览测试计划
python main.py quick mqtt    # 快速测试
python main.py chat          # AI 对话模式
```

---

## 9. 待完善项

### 9.1 🔴 严重问题

| ID | 问题 | 影响 |
|----|------|------|
| SEC-01 | API Key 明文在 config.json 中，已提交 Git | Key 泄露风险 |
| BUG-01 | webui.py 存在重复的 `gr.Tab("📋 测试方案")` 定义（第 843 行和第 850 行重复） | UI 行为不确定 |
| BUG-02 | `functions.py` 与 `webui.py` 的函数大量重复 | 代码维护困难，`functions.py` 似乎是旧版本残留 |

### 9.2 🟡 功能缺失

| ID | 问题 | 建议 |
|----|------|------|
| FEAT-01 | 无 Mock 模式，无串口时无法验证测试流程 | 实现 MockEngine 继承 SerialEngine |
| FEAT-02 | 无单元测试 | 测试用例集庞大但工具本身无测试保障 |
| FEAT-03 | 知识图谱无独立 UI 标签页 | 查询功能分散在对话和缺陷页面中 |
| FEAT-04 | 无测试报告导出（PDF/HTML） | 只能看 UI 上的进度输出 |
| FEAT-05 | 串口日志未入库 | serial_logs 表已定义但未使用 |

### 9.3 🟢 代码优化

| ID | 问题 | 建议 |
|----|------|------|
| REF-01 | `webui.py` 1500+ 行，UI 和业务逻辑混杂 | 拆分为 UI 层和 Handler 层 |
| REF-02 | 全局变量过多（`_suite_cases`、`_DEFECT_CACHE` 等） | 封装到 Session 类或状态管理中 |
| REF-03 | Excel 模块映射硬编码在 `excel_loader.py` 和 `test_executor.py` 两处 | 统一到配置文件 |
| REF-04 | config.json 含敏感信息 | 改为 .env 文件 + 环境变量 |
| REF-05 | `functions.py` 似乎是旧版 webui.py 的提取，已被 webui.py 替代 | 确认后删除 |

---

## 附录：文件清单

```
ai_uart_tool/
├── webui.py                ← Web UI 主入口 (1500+ 行)
├── main.py                 ← CLI 入口
├── functions.py            ← (疑似旧版，待清理)
├── CLAUDE.md               ← 项目上下文
│
├── agents/
│   ├── chat_session.py     ← 对话会话管理
│   ├── intent_router.py    ← 意图分类与参数提取
│   ├── test_agent.py       ← 测试 Agent
│   ├── defect_agent.py     ← 缺陷 Agent
│   └── knowledge_agent.py  ← 知识图谱 Agent
│
├── engines/
│   ├── serial_engine.py    ← 串口引擎 (pyserial)
│   ├── excel_loader.py     ← Excel 用例加载器
│   ├── test_executor.py    ← 测试执行引擎
│   └── result_matcher.py   ← 结果匹配器
│
├── models/
│   ├── schemas.py          ← 数据类定义
│   ├── database.py         ← SQLite 表结构 + 查询
│   └── test_plan_manager.py ← 方案/测试集 CRUD
│
├── llm/
│   ├── llm_client.py       ← DeepSeek API 客户端
│   └── prompts.py          ← 提示词模板
│
├── defect/
│   ├── local_defect_store.py ← 本地缺陷存储
│   └── lingji_sync.py      ← 灵畿平台同步
│
├── knowledge/
│   ├── knowledge_store.py  ← 三元组提取与存储
│   └── knowledge_querier.py ← 知识查询引擎
│
├── config/
│   └── config.json         ← ⚠️ 含 API Key
│
├── test_at_link/common/    ← AT 指令模块 (27 个 command_*.py)
├── test_data/              ← 23+ Excel 测试配置文件
├── data/                   ← 运行时数据 (DB + JSON)
├── defects/                ← 缺陷 JSON 导出
└── test_*.py               ← 测试脚本 (4 个)
```

---

> **文档维护者：** Claude Code | **最后更新：** 2026-05-30
