# 变更日志

## [v1.0.0] - 2026-05-30

### 新增
- 初始版本：Web UI (Gradio) + CLI 模式
- 串口控制（扫描/连接/断开/AT指令收发）
- 测试方案三级管理（方案→用例集→用例）
- 23+ 模块 Excel 用例加载
- AI 意图识别（DeepSeek V4 Flash）
- 缺陷自动生成 + 灵畿平台提交
- 知识图谱（三元组提取/相似失败查询）

### 修改
- 密钥从 config.json 迁移到 ~/.ai_uart_keys.json（安全整改）
- 串口扫描/连接改为跨平台（支持 Windows/macOS/Linux）
- lc 查找改为 shutil.which()（跨平台）

### 文档
- 按 DEV_STANDARDS 标准化：README / REQUIREMENTS / DESIGN / CLAUDE.md
