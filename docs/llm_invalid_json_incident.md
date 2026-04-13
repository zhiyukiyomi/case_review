# LLM 非法 JSON 问题复盘

## 背景

在“测试用例覆盖度评估 Agent”运行过程中，前端轮询任务状态接口时，后端返回了如下失败结果：

```json
{
  "task_id": "4f5696a5114349879a933c68a11c226c",
  "status": "failed",
  "result": null,
  "error": "LLM returned invalid JSON: Expecting ',' delimiter: line 35 column 383 (char 9815)"
}
```

该问题发生在异步分析链路中，属于 LLM 结构化输出不稳定导致的任务失败。

## 问题现象

### 用户侧现象

- 页面长时间显示“评估中”
- 前端持续轮询 `GET /api/analysis/jobs/{task_id}`
- 最终任务状态变为 `failed`
- 后端返回 `LLM returned invalid JSON`

### 接口层现象

- `POST /api/analysis/jobs` 成功，说明任务已创建
- `GET /api/analysis/jobs/{task_id}` 在一段时间内持续返回 `status=running`
- 最终返回 `status=failed`

### 日志侧现象

- 后端能正常收到创建任务和查询任务请求
- 失败不是发生在上传阶段，而是发生在异步任务执行阶段

## 根因分析

### 直接原因

LLM 在生成结构化结果时返回了格式错误的 JSON，导致本地 JSON 解析失败。

错误信息：

```text
Expecting ',' delimiter
```

这通常意味着：

- JSON 某处缺少逗号
- 某个字符串没有正确转义
- 长输出被中途破坏
- 模型返回“看起来像 JSON、其实不合法”的文本

### 深层原因

该项目的单次 LLM 输出任务较重，包含：

- 需求点抽取
- 覆盖关系映射
- 补充建议
- 缺失测试用例生成

如果需求文档较长、测试用例较多，就会出现：

- prompt 输入变大
- 单次输出 JSON 体量变大
- 嵌套字段增多
- 模型更容易输出非法 JSON

### 为什么开启 JSON Mode 仍然会发生

项目中已经在 [deepseek_client.py](../backend/app/llm/deepseek_client.py) 使用了：

```python
response_format={"type": "json_object"}
```

JSON Mode 的作用是降低风险，但不能绝对保证：

- 所有字段都符合 schema
- 长 JSON 一定完整
- 字符串一定正确转义
- 模型在复杂结构输出下永不出错

因此，JSON Mode 只能减少问题概率，不能替代本地校验和兜底机制。

## 之前的解决方式

为了解决这类 `invalid JSON` 问题，我们对后端做了“更稳的 JSON 输出链路”改造，主要包括以下几项。

### 1. 保留本地严格 JSON 校验

在 [json_utils.py](../backend/app/utils/json_utils.py) 中继续保留：

- 去除代码块包裹
- 提取 JSON 主体
- 本地 `json.loads(...)`
- Pydantic schema 校验

并新增：

- 清理非法控制字符

这样即使模型输出里夹带不可见脏字符，也不会直接导致解析失败。

### 2. 在 LLM 客户端增加“JSON 修复”调用

在 [deepseek_client.py](../backend/app/llm/deepseek_client.py) 中新增了：

- 首次按 JSON Mode 请求
- 如果解析失败，触发一次“修复 JSON”调用
- 修复调用只做一件事：
  - 把原始非法 JSON 修成合法 JSON
  - 不允许增加 schema 外字段

这比单纯“原样重试”更有效，因为它针对的是输出格式问题，而不是重新做完整推理。

### 3. 将覆盖评估改成分批调用

在 [coverage_agent.py](../backend/app/agent/coverage_agent.py) 中：

- 不再一次性让模型评估所有需求点
- 改为按 `coverage_batch_size` 分批执行
- 每批只处理一小组 requirement points
- 最后在本地合并 mappings 和 suggestions

这样做的效果：

- 降低单次 prompt 体积
- 降低单次返回 JSON 体积
- 降低模型返回非法 JSON 的概率

### 4. 对 prompt 中的文本做裁剪

在 [prompts.py](../backend/app/agent/prompts.py) 中增加了：

- 对 `source_text`
- `steps`
- `expected_result`
- `description`

等字段做截断和压缩，避免把非常长的文本直接塞入 prompt。

目标是减少：

- 输入 token
- 输出体量
- LLM 在长结构化结果下的格式失稳

### 5. 对 prompt 增加更强约束

在 [prompts.py](../backend/app/agent/prompts.py) 中进一步强调：

- 只输出 JSON
- 不输出解释文字
- `rationale`、`missing_reason` 控制长度
- `suggested_case.steps` 与 `expected_result` 保持简洁

这样可以降低模型因为“解释过多”而破坏 JSON 的概率。

### 6. 给缺失 requirement 增加本地兜底

分批评估后，如果某个 requirement 没有被模型返回覆盖结果，则在本地自动补一个默认 mapping：

- `covered=false`
- `missing_reason=模型未返回该需求点的覆盖判断，请人工复核。`

这样可以避免模型漏返回某个 requirement 时，整个评估结果结构不完整。

## 改造后的收益

改造完成后，链路在稳定性上有以下提升：

- 非法控制字符不会直接导致 JSON 解析失败
- 非法 JSON 有机会通过修复调用恢复
- 单次输出变小，复杂任务更稳定
- 某批数据出问题时，影响范围更小
- 结果缺项时有本地兜底，不至于整批不可用

## 仍然存在的边界

即使做了以上优化，仍然不能保证 100% 不出错。主要边界包括：

- 模型长时间无响应
- 网络连接问题
- DeepSeek 余额不足或接口限流
- 单批数据仍然过大
- 复杂嵌套结构下模型偶发性格式失稳

因此，这类链路应始终视为：

- LLM 负责语义判断
- 本地代码负责结构校验与兜底

## 推荐的进一步优化

如果后续还要进一步提升稳定性，建议继续做以下优化：

### 快速模式

- 先只做覆盖评估
- 暂不生成缺失测试用例
- 用于演示和大文件快速出结果

### 更短超时

当前 `.env` 中的超时和重试偏保守，可考虑调整：

```env
LLM_TIMEOUT=30
LLM_MAX_RETRIES=1
LLM_REPAIR_RETRIES=1
COVERAGE_BATCH_SIZE=8
PROMPT_TEXT_PREVIEW_CHARS=180
```

### 前端展示阶段状态

建议在前端增加：

- 正在提取需求点
- 正在分批评估覆盖
- 正在修复 JSON
- 正在生成补充用例

这样用户不会误以为系统“卡住”。

### 任务总超时

建议给异步任务增加总超时限制，避免任务长时间处于 `running`。

## 相关代码位置

- LLM 客户端：[deepseek_client.py](../backend/app/llm/deepseek_client.py)
- JSON 解析工具：[json_utils.py](../backend/app/utils/json_utils.py)
- 覆盖评估主流程：[coverage_agent.py](../backend/app/agent/coverage_agent.py)
- Prompt 约束：[prompts.py](../backend/app/agent/prompts.py)
- 任务状态管理：[task_service.py](../backend/app/services/task_service.py)

## 总结

本次问题的本质不是前端轮询接口出错，也不是任务创建失败，而是：

> LLM 在复杂结构化输出场景下返回了非法 JSON，导致本地解析失败。

解决这个问题的核心思路不是“让模型永不出错”，而是：

> 通过分批输出、格式修复、本地校验、字段限长和兜底合并，把 LLM 输出链路做得更稳。
