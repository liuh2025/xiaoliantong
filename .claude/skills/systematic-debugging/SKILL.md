---
name: systematic-debugging
description: 系统性调试方法，找到根因前禁止提出修复方案。当遇到 bug、测试失败、异常行为时调用。
user-invocable: true
argument-hint: "[问题描述或错误信息]"
---

你现在作为调试专家工作，使用系统性方法定位和修复问题。

## Iron Law

**找到根因前禁止提出修复方案。违反则停止，重新开始。**

```
错误示例：
❌ "可能是缓存问题，让我清一下试试"
❌ "让我先改改这里看看"
❌ "我猜是 X，改一下"

正确做法：
✅ 先收集证据 → 形成假设 → 验证假设 → 确认根因 → 再修复
```

## 调试四阶段

### Phase 1: 根因调查（必须完成）

**1. 仔细阅读错误信息**
```
❌ 不要跳过！错误信息通常包含解决方案
✅ 完整阅读，包括堆栈跟踪
✅ 理解每个字段的含义
```

**2. 稳定复现**
```bash
# 能可靠触发吗？步骤是什么？
# 记录最小复现步骤

# 示例：
1. 打开页面 /users
2. 点击"添加用户"
3. 输入邮箱：test@example.com
4. 提交 → 报错 500
```

**3. 检查近期变更**
```bash
git log --oneline -10
git diff HEAD~3..HEAD
git blame <problem-file>
```

**4. 多组件系统诊断**
```python
# 在每个组件边界添加日志
def component_a():
    result = call_component_b()
    print(f"[component_a] received: {result}")  # 诊断日志
    return process(result)
```

### Phase 2: 模式分析

**1. 找可工作的类似代码**
```bash
# 搜索类似实现
grep -r "类似功能" src/
git log -p --all -S "类似功能" | head -50
```

**2. 对比差异**
```bash
# 工作的代码 vs 不工作的代码
diff -u working_code.py broken_code.py
```

**3. 完整阅读参考实现**
```
❌ 不要略读
✅ 逐行理解
✅ 注意边界情况处理
```

### Phase 3: 假设验证

**单一假设格式：**
```
"我认为 [X] 是根因，因为 [Y] 证据"

示例：
"我认为数据库连接池耗尽是根因，因为：
 1. 错误信息显示 'connection timeout'
 2. 问题在高并发时出现
 3. 监控显示连接数达到上限"
```

**最小验证：**
```bash
# 一次只改一个变量
# 验证假设，不是修 bug

# 假设：连接池大小不够
# 验证：临时增大连接池，观察
export DB_POOL_SIZE=100
pytest tests/ -k "test_concurrent"
```

**验证结果：**
```
✅ 假设确认 → 继续 Phase 4
❌ 假设错误 → 新假设，回 Phase 3
❌ 假设错误 ≥ 3 次 → 回 Phase 1 重新调查
```

### Phase 4: 实现修复

**1. 先写失败测试（必须有）**
```python
def test_bug_xxx_reproduced():
    """复现 bug 的测试"""
    # 最小复现步骤
    result = buggy_function(input_xxx)
    assert result == expected_xxx  # 当前会失败
```

**2. 单一修复**
```bash
# 一次一个变更
# 不要同时改多处
```

**3. 验证**
```bash
pytest tests/unit/test_xxx.py -v
pytest tests/integration/ -v  # 确保无回归
```

**4. 修复失败？**
```
< 3 次 → 回 Phase 1
≥ 3 次 → 停止，质疑架构设计，向 TL 汇报
```

---

## 高级调试技巧

### 条件等待模式

用于异步/竞态条件调试：

```python
import time

def wait_for_condition(condition_fn, timeout=10, interval=0.1):
    """等待条件满足或超时"""
    start = time.time()
    while time.time() - start < timeout:
        if condition_fn():
            return True
        time.sleep(interval)
    raise TimeoutError(f"Condition not met within {timeout}s")

# 使用
wait_for_condition(lambda: element.is_visible())
```

### 污染者查找

找出引入 bug 的 commit：

```bash
#!/bin/bash
# find-polluter.sh - 二分查找引入问题的 commit

git bisect start
git bisect bad HEAD           # 当前版本有问题
git bisect good v1.0.0        # 这个版本没问题

# Git 会自动二分，每次运行测试
git bisect run pytest tests/unit/test_xxx.py

# 找到后
git bisect reset
```

### 测试压力模式

**模式 1：重复执行**
```bash
# 检测间歇性失败
for i in {1..100}; do
    pytest tests/unit/test_flaky.py -v || echo "Failed at run $i"
done
```

**模式 2：并发执行**
```bash
# 检测竞态条件
pytest -n 10 tests/integration/test_concurrent.py
```

**模式 3：边界值轰炸**
```python
@pytest.mark.parametrize("value", [
    0, 1, -1,           # 边界
    2**31 - 1, -2**31,  # 整数边界
    float('inf'),       # 特殊值
    "", None, [],       # 空值
])
def test_boundary_bombing(value):
    result = process(value)
    assert result is not None
```

---

## Red Flags（发现立即停止）

```
❌ "快速修复，稍后调查"
❌ "试试改 X 看看"
❌ "一次改多个地方"
❌ "跳过测试，手动验证"
❌ "可能是 X，让我修复"
❌ "不确定但试试这个"
❌ "我之前遇到过类似问题"
```

**正确做法：** 停止，回 Phase 1，收集证据。

---

## 调试日志级别

| 级别 | 用途 | 示例 |
|------|------|------|
| **ERROR** | 确认失败 | `logger.error(f"API 调用失败: {response.status_code}")` |
| **WARN** | 可疑但未失败 | `logger.warning(f"重试 {attempt}/3")` |
| **INFO** | 关键流程节点 | `logger.info(f"处理订单 {order_id}")` |
| **DEBUG** | 详细诊断 | `logger.debug(f"请求参数: {params}")` |

**调试完成后删除临时日志。**

---

## 完成报告

修复完成后报告：

```
## 调试报告

### 问题描述
{原始问题}

### 根因
{确认的根因，包含证据}

### 调试过程
1. Phase 1: {调查发现}
2. Phase 2: {模式分析}
3. Phase 3: {假设验证}
4. Phase 4: {修复实现}

### 修复内容
- 文件：{file}
- 变更：{change description}
- 测试：{test file}

### 验证
- [x] 失败测试已添加
- [x] 修复后测试通过
- [x] 无回归
```

---

## 调用示例

```bash
# 遇到 bug 时
/systematic-debugging "登录接口返回 500 错误"

# 测试失败时
/systematic-debugging "test_user_auth 失败：AssertionError"

# 异常行为
/systematic-debugging "页面加载后数据不显示"
```

## 关联 Skills

**被调用：**
- `implementer-prompt.md` - 开发过程中遇到 bug 时调用
- `m3-tl-bug-fix` - M4 测试失败后 TL 分析根因时调用

**不被调用：**
- Tester 角色 - Tester 只负责发现问题并记录到 TEST-REPORT，不负责调试和修复
- QA 角色 - QA 只负责审查，不负责调试和修复

**调用原则：**
- 只有 **DEV** 和 **TL** 角色可以调用此 skill
- Tester/QA 发现问题时，记录到 TEST-REPORT 后派发给 TL
- 由 TL 指派 DEV 进行根因分析和修复

**引用规则：**
- `docs/rules/RL-redlines.md` - RL-DB-0001: 猜测性修复禁止
