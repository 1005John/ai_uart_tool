# 变更日志

## [v1.1.0] - 2026-05-30

### 重构
- **Web UI 全新布局**：双标签页替代原四标签+三框下钻
  - 📦 用例集库：左侧用例集列表 + 右侧 HTML 表格显示用例 + 表单添加/删除
  - 📋 方案管理：左侧方案列表 + 用例集勾选 + 右侧 HTML 表格（只读）
  - 🐛 缺陷管理：保持不变
- 用例集独立维护 → 方案勾选组合的数据模型
- 用例显示用 HTML 美化表格（交替行色、等宽指令），替代 Gradio Dataframe
- 串口控制栏保持顶部固定

### 修复
- 删除本地函数 delete_plan 与导入模块命名冲突（RecursionError）
- list_test_sets() 尾部下划线导致 Radio choices 校验失败
- 方案管理 CheckboxGroup 改为手动保存模式（避免频繁刷新）
- merge_plan_to_exec_list 返回 dict 需转为 TestCase 对象

### 新增
- 方案执行功能：逐条串口发送 AT 指令，实时进度显示，FAIL 自动生成缺陷
- 方案管理 🔄 刷新按钮

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
