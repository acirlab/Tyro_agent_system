# 双工语音 Agent MVP 简化架构

## 一、整体架构

```text
用户麦克风
    │
    ▼
语音输入层
VAD → ASR → EOT
    │
    ▼
对话控制层
判断用户说了什么、是否打断、是否开启任务
    │
    ▼
Agent 执行层
LLM → Tool → LLM → Tool
    │
    ▼
语音输出层
进度反馈 → TTS → 扬声器
```

系统运行时实际上有两条同时工作的链路：

```text
链路一：实时语音链路
收音、判断用户是否说完、监听打断、停止播放

链路二：任务执行链路
调用 LLM、执行 Tool、运行 Skill、产生任务结果
```

两条链路必须分开。即使 Agent 正在执行一个耗时一分钟的任务，语音系统仍然要能接收用户讲话和打断。

---

# 二、核心模块

## 1. Audio Runtime：音频运行模块

负责麦克风和扬声器。

```text
麦克风
→ 音频格式转换
→ 回声消除 AEC
→ 输出 16kHz 单声道音频
```

主要职责：

* 持续读取麦克风。
* 播放 TTS 音频。
* 将扬声器播放内容送给 AEC。
* 用户打断时立即清空播放缓冲。

主要接口：

```python
class AudioTransport:
    async def read_frames(self):
        """持续读取麦克风音频"""

    async def play_frame(self, frame):
        """播放一帧音频"""

    async def clear_playback(self):
        """立即停止当前播放"""
```

---

## 2. User Turn Engine：用户轮次判断模块

负责判断：

> 用户什么时候开始说话，什么时候真正说完。

内部流程：

```text
pVAD 检测开口
    │
    ▼
收集用户语音
    │
    ▼
短暂静音
    │
    ▼
SenseVoice ASR
    │
    ▼
FireRed EOT
    │
    ├── 用户说完：提交本轮
    └── 用户没说完：继续等待
```

保留三个状态即可：

```text
IDLE        等用户开口
SPEECH      用户正在说话
EXTRA_WAIT  用户暂时停顿，等待继续说
```

输出一个统一对象：

```python
class UserTurn:
    text: str
    audio: bytes
    eot_probability: float
```

主要接口：

```python
class UserTurnEngine:
    async def push_audio(self, frame):
        """输入一帧音频"""

    async def get_completed_turn(self) -> UserTurn:
        """取得一个完整用户轮次"""

    async def inject_audio(self, frames):
        """将打断时缓存的音频送回来"""
```

---

## 3. Interruption Controller：打断控制模块

这个模块只在机器人说话时重点工作。

流程：

```text
机器人正在播放
    │
用户开始说话
    │
高阈值 pVAD 连续检测
    │
确认是真人插话
    │
立即停止 TTS
    │
将用户开口部分音频交给 User Turn Engine
```

打断时只立即停止：

* 当前播放。
* 当前 TTS。
* 当前直接回复的 LLM 输出。

不要默认取消：

* 正在运行的后台 Tool。
* 整个 Agent 任务。

例如用户说：

```text
“先别说话，继续查。”
```

任务应该继续，只停止语音播报。

主要接口：

```python
class InterruptionController:
    async def on_audio(self, frame):
        """播放期间检测用户插话"""

    async def interrupt_speech(self):
        """停止当前机器人语音"""

    async def cancel_task(self):
        """用户明确要求取消时才取消任务"""
```

---

## 4. Conversation Controller：对话控制模块

负责理解用户这一轮话的用途。

它需要区分：

```text
普通聊天
开始新任务
修改正在执行的任务
询问任务进度
暂停任务
取消任务
简单回应，例如“嗯”“好的”
```

例如：

```text
用户：帮我查三款手机的区别
→ 开启任务

用户：把价格也加进去
→ 修改当前任务

用户：先停一下
→ 暂停任务

用户：继续
→ 恢复任务
```

主要接口：

```python
class ConversationController:
    async def handle_turn(self, turn: UserTurn):
        """处理完整用户轮次"""

    async def classify_intent(self, text: str):
        """判断聊天、任务或任务控制"""
```

---

## 5. Agent Runtime：任务执行模块

负责真正执行任务。

基本循环：

```text
产生一条进度反馈
    │
调用 LLM 决定下一步
    │
    ├── 直接回答
    ├── 调用 Tool
    ├── 询问用户
    └── 完成任务
```

伪代码：

```python
while task.not_finished:
    feedback.say("我正在确认下一步")

    decision = await llm.next_action(task)

    if decision.type == "tool":
        result = await tool_executor.run(decision)
        task.add_result(result)

    elif decision.type == "ask_user":
        await speech.say(decision.question)
        break

    elif decision.type == "finish":
        await speech.say(decision.answer)
        break
```

关键点：

> 每次调用 LLM 前，都先安排一条简短反馈，但不等待反馈播放结束。

反馈和 LLM 可以同时开始：

```text
开始播放：“我正在检查结果。”
同时调用 LLM
```

主要接口：

```python
class AgentRuntime:
    async def start_task(self, goal: str):
        ...

    async def update_task(self, text: str):
        ...

    async def pause_task(self):
        ...

    async def cancel_task(self):
        ...

    async def run_loop(self):
        ...
```

---

## 6. Feedback Controller：反馈模块

负责把内部执行状态变成用户能理解的话。

例如：

```text
LLM 开始
→ “我正在确认下一步。”

开始搜索
→ “我正在搜索相关资料。”

开始分析
→ “我正在整理找到的信息。”

Tool 出错
→ “刚才的查询没有成功，我在换一种方式。”
```

不要把模型内部推理过程念给用户，只播报动作和进度。

主要接口：

```python
class FeedbackController:
    async def on_llm_start(self):
        ...

    async def on_tool_start(self, tool_name: str):
        ...

    async def on_tool_progress(self, message: str):
        ...

    async def on_task_complete(self):
        ...
```

---

## 7. Speech Scheduler：语音调度模块

所有语音都必须经过它，不能让业务模块直接调用 TTS。

它负责：

* 语音优先级。
* 语音排队。
* 打断。
* 合并重复进度。
* 删除已经过时的反馈。

优先级可以简单分为：

```text
最高：权限确认、重要错误
其次：需要用户回答的问题
其次：最终回答
其次：普通回复
最低：任务进度
```

主要接口：

```python
class SpeechScheduler:
    async def say(self, text: str, priority: int):
        ...

    async def interrupt(self):
        ...

    async def replace_progress(self, text: str):
        ...
```

---

## 8. Tool Registry：工具注册模块

Tool 是一个最小能力，例如：

```text
网页搜索
读取网页
查询数据库
获取时间
创建日程
控制机器人动作
```

统一接口：

```python
class Tool:
    name: str
    description: str

    async def execute(
        self,
        arguments: dict,
        progress_callback,
        cancel_token,
    ):
        ...
```

新增 Tool 时只需要：

1. 实现 `Tool` 接口。
2. 注册到 `ToolRegistry`。
3. 在对应 Skill 中声明允许使用。

---

## 9. Skill Registry：技能模块

Skill 是一组 Tool 加一套任务规则。

例如：

```text
网页调研 Skill
├── web_search
├── read_webpage
├── 调研提示词
├── 反馈文案
└── 调研状态
```

Skill 可以简单定义为：

```yaml
name: web_research
description: 搜索并整理公开资料

tools:
  - web_search
  - read_webpage

feedback:
  start: 我开始搜索相关资料。
  analyze: 我正在整理找到的信息。
```

主要接口：

```python
class SkillRegistry:
    def register(self, skill):
        ...

    def get(self, name: str):
        ...

    async def match(self, user_text: str):
        """根据用户请求选择 Skill"""
```

---

# 三、模块之间如何通信

建议使用一个简单的事件总线。

```text
UserTurnEngine
    │ 发布 UserTurnCompleted
    ▼
ConversationController
    │ 发布 TaskStarted
    ▼
AgentRuntime
    │ 发布 ToolStarted / LLMStarted
    ▼
FeedbackController
    │ 创建 SpeechJob
    ▼
SpeechScheduler
```

MVP 使用 `asyncio.Queue` 就够了：

```python
class EventBus:
    async def publish(self, event):
        ...

    def subscribe(self, event_type):
        ...
```

---

# 四、推荐代码目录

```text
voice_agent/
├── audio/
│   ├── transport.py
│   ├── aec.py
│   └── runtime.py
│
├── turn/
│   ├── vad.py
│   ├── asr.py
│   ├── eot.py
│   ├── engine.py
│   └── interruption.py
│
├── speech/
│   ├── tts.py
│   ├── scheduler.py
│   └── feedback.py
│
├── conversation/
│   └── controller.py
│
├── agent/
│   ├── runtime.py
│   ├── planner.py
│   └── task.py
│
├── tools/
│   ├── base.py
│   ├── registry.py
│   └── builtin/
│
├── skills/
│   ├── registry.py
│   └── packages/
│
├── infrastructure/
│   └── event_bus.py
│
└── main.py
```

---

# 五、最重要的三个边界

## 边界一

```text
语音模块不能直接执行 Tool。
```

语音模块只负责产生完整的 `UserTurn`。

## 边界二

```text
Tool 不能直接调用 TTS。
```

Tool 只能上报结构化进度，由 `FeedbackController` 决定是否说出来。

## 边界三

```text
用户打断语音，不等于取消任务。
```

停止播放、停止当前回复和取消后台任务必须是三个不同操作。

---

# 六、MVP 最小组合

第一版只需要：

```text
AudioTransport
AEC
FireRed pVAD
SenseVoice ASR
FireRed EOT
InterruptionController
ConversationController
AgentRuntime
FeedbackController
SpeechScheduler
Kokoro TTS
ToolRegistry
SkillRegistry
```

先实现两个 Tool：

```text
fake_long_task
web_search
```

先实现两个 Skill：

```text
general_chat
web_research
```

这样就可以完整验证：

```text
用户说话
→ 判断说完
→ Agent 开始任务
→ 持续语音反馈
→ 调用 Tool
→ 用户随时打断
→ 修改或取消任务
→ 最终语音回答
```
