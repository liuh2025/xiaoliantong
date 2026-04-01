# 开发计划编写规范（DEV-plan-writing-rules.md）

---

## 计划编写原则

**假设执行者：**
- 是熟练开发者，但对本项目零上下文
- 不了解本项目的工具集和问题域
- 不了解测试设计最佳实践
- 需要完整的文件路径、代码示例、命令和预期输出

**核心原则：**
- DRY（Don't Repeat Yourself）
- YAGNI（You Aren't Gonna Need It）
- TDD（Test-Driven Development）
- 频繁提交（Frequent Commits）

---

## 任务粒度（Bite-Sized Task Granularity）

**每个 task 是一个独立功能点（2-5 分钟完成）**

**每个 step 是一个原子操作：**
- Step 1: RED - 编写失败测试
- Step 2: 验证 RED - 观察失败
- Step 3: GREEN - 编写最小实现
- Step 4: 验证 GREEN - 观察通过
- Step 5: REFACTOR - 重构优化（消除重复、改进命名）

---

## 计划文档结构

### 文档头部（必须）

```markdown
# {项目名称} 开发实施计划

> **For Claude:** 本计划由 TL 编写，执行时使用 /m3-subagent-development 逐个派发 task。

**目标：** [一句话描述本次开发目标]

**架构方案：** [2-3 句话描述技术方案，来自 DESN]

**技术栈：** [关键技术/框架/库]

---
```

### Task 结构（必须）

````markdown
### Task N: [模块名 - 功能点]

**涉及文件：**
- 创建：`exact/path/to/file.py`
- 修改：`exact/path/to/existing.py:123-145`
- 测试：`tests/exact/path/to/test_file.py`

**实现目标：**
[清晰描述本 task 要实现什么功能]

**Step 1: RED - 编写失败测试**

```python
def test_specific_behavior():
    # 完整的测试用例代码
    result = function(input)
    assert result == expected
```

**Step 2: 验证 RED - 观察失败**

运行命令：`pytest tests/path/test_file.py::test_specific_behavior -v`
预期输出：FAIL with "function not defined"

**Step 3: GREEN - 编写最小实现**

```python
def function(input):
    # 最小实现代码
    return expected
```

**Step 4: 验证 GREEN - 观察通过**

运行命令：`pytest tests/path/test_file.py::test_specific_behavior -v`
预期输出：PASS

**Step 5: REFACTOR - 重构优化**

- 消除重复代码
- 改进命名
- 提取公共方法
- 保持测试通过

---
````

---

## 必须包含的内容

| 项目 | 要求 | 反例（禁止） |
|------|------|------------|
| 文件路径 | 精确的绝对路径 | "相关文件"、"对应的测试文件" |
| 代码示例 | 完整的可运行代码 | "添加验证逻辑"、"实现业务逻辑" |
| 命令 | 精确的命令和参数 | "运行测试"、"执行脚本" |
| 预期输出 | 明确的输出内容 | "测试通过"、"正常运行" |

---

## TDD 五步法（强制）

每个 task 必须严格遵循 Red-Green-Refactor 循环：

1. **RED - 编写失败测试**：先写测试用例，包含完整的输入和预期输出
2. **验证 RED - 观察失败**：执行测试，确认失败原因符合预期（功能缺失，不是语法错误）
3. **GREEN - 编写最小实现**：写刚好能让测试通过的最小代码
4. **验证 GREEN - 观察通过**：执行测试，确认全部通过
5. **REFACTOR - 重构优化**：消除重复、改进命名、提取公共方法，保持测试通过

---

## 示例：完整的 Task

````markdown
### Task 1: 用户管理 - 用户注册接口

**涉及文件：**
- 创建：`src/api/user.py`
- 创建：`tests/api/test_user.py`

**实现目标：**
实现用户注册接口 POST /api/v1/users，接收 username 和 password，返回用户 ID。

**Step 1: RED - 编写失败测试**

```python
# tests/api/test_user.py
def test_register_user():
    response = client.post('/api/v1/users', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 201
    assert 'user_id' in response.json()
```

**Step 2: 验证 RED - 观察失败**

运行命令：`pytest tests/api/test_user.py::test_register_user -v`
预期输出：FAIL with "404 Not Found"

**Step 3: GREEN - 编写最小实现**

```python
# src/api/user.py
from flask import Blueprint, request, jsonify

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/v1/users', methods=['POST'])
def register():
    data = request.json
    # 最小实现：直接返回固定 user_id
    return jsonify({'user_id': 1}), 201
```

**Step 4: 验证 GREEN - 观察通过**

运行命令：`pytest tests/api/test_user.py::test_register_user -v`
预期输出：PASS

**Step 5: REFACTOR - 重构优化**

- 检查是否有重复代码需要提取
- 检查命名是否清晰
- 当前代码已足够简洁，无需重构

---
````

---

## 常见错误（禁止）

| 错误       | 说明              | 正确做法                                        |
| -------- | --------------- | ------------------------------------------- |
| 跳过测试     | 直接写实现代码         | 必须先写测试                                      |
| 模糊路径     | "在相关文件中添加"      | 写精确路径 `src/api/user.py:45-60`               |
| 伪代码      | "添加验证逻辑"        | 写完整代码 `if not username: raise ValueError()` |
| 模糊命令     | "运行测试"          | 写精确命令 `pytest tests/api/test_user.py -v`    |
| 过度设计     | 一次实现多个功能        | 最小实现，刚好通过测试                                 |
| 大粒度 task | 一个 task 包含多个功能点 | 拆分为多个 2-5 分钟的 task                          |

---
