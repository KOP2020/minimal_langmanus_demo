# Langgraph预研

## 1. langchain为什么不好（或者说不够？

一个最典型的langchain（有retrival能力的：

  `chain = setup\_and\_retrieval | prompt | model | output\_parser`

但是很显然的一个问题是：如果我们把链中的组件想象成Graph中的节点，组件之间的联系想象成Graph中的边，那么这个链就是一个有向无环图(DAG）。 **即在一次Chain运行中，一个调用节点无法重复/循环进入。**也就是说 **简单的链（Chain）**天然的欠缺loop的能力

可我们要是想做agent的话呢？要知道 agent 重要的就是ReAct的能力。即：*多次Reason（推理）-Act（行动）的反复与**循环**，直到完成任务。*

langchain不是不能做到，他可以借助AgentExecutor调度的Agent做到：

```python
agent = (  
    {input:{输入信息}, agent_scratchpad:{中间步骤}}  
    | prompt  
    | model  
    | AgentOutputParser()  
)  
  
"""  
注意：Agent需要使用agent_executor调用，以增加上述两个能力  
"""  
agent_executor = AgentExecutor(agent=agent, tools=tool_list, verbose=True)  
agent_executor.invoke({"input": "whats the weather in New york?"})
```

这个loop的过程是AgentExecutor赋予的。相对于Chain.invoke()直接运行一个预设好的workflow 这里的 **Agent_executor的作用就是为了能够实现多次循环ReAct的动作，以最终完成任务。** 具体来说：

1. 通过大模型来决定采取什么行动 使用什么工具 或者向用户输出响应（如运行结束时）；
2. 执行1步骤中的行动 比如调用某个工具， 并把结果继续交给大模型来决定，即返回步骤1；

这里的AgentExecute存在的问题是： 过于黑盒 所有的决策过程隐藏在AgentExecutor背后。 更重要的是 他缺乏更精细的控制能力。因为他的re（决定）的过程是llm决定的（llm+特定的提示此来做这个reasoning的）。这和我们现在用的qwen所做的agent的逻辑类似。 

这在构建复杂的、要求更精细的Agent控制能力的时候受限 。

## 2. Langraph？

LangGraph的实现方式是把之前基于AgentExecutor的黑盒调用过程用一种新的形式来构建。我们可以粗暴的认为LangGraph就是把我上述提到的黑盒的AgentExecutor揉碎掰开 允许你定义内部的细节结构（用图的方式），从而实现更强大的功能。 那么我们当然可以用LangGraph来重新实现原来的AgentExecutor，即实现一个最基础的ReAct范式的Agent应用

（网上找了个demo ：

<img src="C:\Users\94958\AppData\Roaming\Typora\typora-user-images\image-20250401003341359.png" alt="image-20250401003341359" style="zoom:88%;" />

```python
 # 定义一个Graph，传入state定义（参考上图state属性）  
workflow = StateGraph(AgentState)  
  
# 两个节点  
  
#节点1: 推理节点，调用LLM决定action，省略了runreason细节  
workflow.add_node("reason", run_reason)  
  
#节点2: 行动节点，调用tools执行action，省略executetools细节  
workflow.add_node("action", execute_tools)  
  
#入口节点：总是从推理节点开始  
workflow.set_entry_point("reason")  
  
#条件边：根据推理节点的结果决定下一步  
workflow.add_conditional_edges(  
    "reason",  
    should_continue, #条件判断函数（自定义，根据状态中的推理结果判断（key））  
    {  
        "continue": "action", #如果条件函数返回continue，进action节点  
        "end": END, #如果条件函数返回end，进END节点  
    },  # key-nodename路由表（下文中，条件函数的第一个写法）
)  
  
#普通边：action结束后，总是返回reason  
workflow.add_edge("action", "reason")  
  
#编译成app  
app = workflow.compile()  
  
#可以调用app了，并使用流式输出  
inputs = {"input": "you task description", "chat_history": []}  
for s in app.stream(inputs):  
    print(list(s.values())[0])  
    print("----")
        
      
```

优势也很明显了：

1. 每个步骤（推理、决策、行动）都明确定义为节点节点之间的 ，关系通过边和条件边清晰表达

2. 为什么说精细的控制点？

   - 可以在任何节点之间插入自定义逻辑（比如上述的：should_continue, #条件判断函数（自定义，根据状态中的推理结果判断））

   - 可以根据状态的任何部分做出复杂的路由决策

   - 可以添加额外的节点处理特殊情况

3. state透明。这依赖于langgraph的state，使用 stream方法 可以实时监控执行过程 我会在后面展开说。

4. 不限限于简单的循环，可以实现复杂的分支和合并。毕竟图本身就是最灵活的 几乎可以表达任何逻辑过程的一种形式。**换句话说 langchain就是在用流程图的方式，做到一切现实世界的逻辑。**用代码实现 封装 编译 然后去执行（在Python里写Python的感觉？很微妙hhh)

## 3. 细节介绍

先来简单介绍一下Langgraph，三个核心：

- **State**: 如同变数表
- **Node**: 做事情 / function
- **Edge**: 流程控制

（如果大家用过传统的生命周期法 来做系统的分析和设计 应该对数据流程图很熟悉。这里 构建langgraph的过程 也很像： 这个state 是一个能统领全局的info存储表，所以function之后 所产生或要更新的info 都会update到我们的state上。

#### 3.1 具体来说 state是什么？：

```python
from typing import TypedDict
from langgraph.graph import StateGraph

class MyState(TypedDict):
    i: int
    j: int
    
...
def fn2(state: MyState):


...
workflow = StateGraph(state_schema=MyState)
```

（1）state是什么？他是怎么声明的？

class MyState(TypedDict): 。我们可以看到 很简单 他是继承了python的TypedDict数据结构 或者说在做了一层封装。这个typeddict也很简单 用起來跟字典 `dict`一模一样 只不过他写了自己的Key名和期望的value类型。那为什么要它？在创建StateGraph对象也就是workflow的时候，声明state_schema=dict或者tpeddict（不再封装一层）不也是一样（而且其实是不会报错的）？

不一样！如果单纯用StateGraph(state_schema=dict) 那LangGraph就会不知道 每个node回传的Key重不重要。更通俗说 其结果就是 如果有个Node因为其具体判定结果没有return某个key的新value，那下一步 就会失去这个key的信息。所以我们必须要在TypedDict外面再封装一层 然后申明好这两个value

（2）state的第二个优点 我把它形容为信息更新的控制反转。我先给一个例子：

```python
class ChatState(TypedDict):
    """聊天状态，存储对话历史"""
    messages: Annotated[list, add_messages]  # 使用 add_messages 注解自动追加消息
    
#注意 我这里用add_messages 这是一个langgraph一个写好的函数（from langgraph.graph.message import add_messages）这里我们是可以自己写逻辑的
#（langgraph里成为外挂reducer函数）
```

这个“信息更新的控制反转”源自Annotated和add_messages。

`Annotated` 里面，第一个是类型声明，之后的是注释。

以 schema 的每个 key 为单位，LangGraph 会先看过 key 的类型声明

- 如果有 Annotated 就取注释的第一个（例如 `add_messages` 函数）

- 对于该 key，LangGraph 将**原来的 state** 和 **节点返回值** 一起处理：将两者放入那个 function，其返回值将成为这个 key 的新 state。那有人会说，这个逻辑不就是简单的append吗？那我们在具体的function（也就是node）里写 不就行了？比如：

  ```python
  class MyState(TypedDict):
      reassign: list
      inplace: list
  
  def fn1(state: MyState):
      state["reassign"] = [9, 8, 7]
      state["inplace"].append(4)
      return None
  ```

这样是可以。但是state的做法还是更精妙 状态更新逻辑在类型定义中声明 而非散布在各个node的函数中。这样，节点函数不需要关心如何正确地追加消息，只需返回新消息即可。框架保证消息会被正确追加，无论是第一条消息还是后续消息。
网上博主的解释 我也觉得很好：*目前个人偏见：在 node function 里更改 state 有点破坏「node 独立执行、彼此通讯」的设计；state 不会只在 node 边界被改变，可能未来 debug 会有一点困难*

#### 3.2 Node是什么？

最开始说了： **Node**: 做事情 / function。

做什么事？通常是 “改变state”。也就是return的值，要么是state类中的message变量（需要记住上下文的 也就是我前文说的有add_messages的）和状态变量（不需要apend到List后 而是直接覆盖、更新）

注意 光是声明function还不够 还要把他绑到我们的graph上 并给每个Node一个名字 他才是一个node。`workflow.add_node("node1", fn1)`

#### 3.3 edge

普通边: 创建节点间的固定连接，无条件执行。

```
# 定义普通边
graph_builder.add_edge("源节点", "目标节点")
```

条件边: 根据路由函数的返回值决定下一个节点。

> 路由函数是条件边的核心，决定执行流程的方向。
>
> 路由函数特点
>
> - 接收当前状态作为输入
> - 返回路由键（1）或直接返回目标节点名称（2）
> - 不修改状态，只负责决策
> - 通常是纯函数，没有副作用

```
graph_builder.add_conditional_edges(
    "source node",           # 条件分支的起点
    路由函数,           # 决定路由方向的函数
    {
        "键1": "目标node1",  # 路由映射表
        "键2": "目标node2",
        ...
    }
)
```

以上是一种写法， ：下面（1）写法+ 路由表（返回一个state[key] ，然后让路由表去matching这个key和具体的Nodename）.而这种写发的sourcenode应该是个判断逻辑的node节点

用第二种写法的话 直接返回nodename了

（1）返回路由键的函数

```
# 返回路由键，用于查找路由表
def get_route_key(state):
    return state["某个字段key（state中定义的状态字段）"]
```

（2）直接返回节点名称的函数

```
# 直接返回目标节点名称或特殊常量
def decide_next_node(state):
    if 某个条件:
        return "NodeA"
    elif 另一个条件:
        return "NodeB"
    else:
        return END
```

## 4.LangGraph的一些awesome features

### 4.1 同时执行多节点:  Superstep

什么事superstep?

![image-20250401023043871](C:\Users\94958\AppData\Roaming\Typora\typora-user-images\image-20250401023043871.png)

如图 1；2和3；4就是superstep 1,2,3.由于一个步骤可以运行一个或多个节点，所以称作 **superstep**

- 注意，在这里，n4 在这个中只会执行一次 ，因为同一个 superstep 2的 n2 n3 后面都是紧接着 n4（super step3）

但下一个例子：
**多连一** ：

![image-20250401023301546](C:\Users\94958\AppData\Roaming\Typora\typora-user-images\image-20250401023301546.png)

如图 红色的是一个superstep。

```python
  graph.set_entry_point("start")

  graph.add_edge("start", "left_1")
  graph.add_edge("start", "right_1")
  graph.add_edge("left_1", "merge")
  graph.add_edge("right_1", "right_2")
  graph.add_edge("right_2", "right_3")
  graph.add_edge("right_3", "merge")
  graph.add_edge("merge", END)
```

这是 mermage节点先在superstep3中 ，后又在5中 故而会执行两次。（superstep的逻辑实际上是：**当某个上游被执行到了以后，就通知下游「数据更新了，换你做事」**）

那有没有办法让他等待r3执行完后再执行 只执行一次？

有的兄弟有的：

```python
  graph.add_edge("start", "left_1")
  graph.add_edge("start", "right_1")
  graph.add_edge("right_1", "right_2")
  graph.add_edge("right_2", "right_3")
  graph.add_edge(["left_1", "right_3"], "merge")  # 合成 list
  graph.add_edge("merge", END)
```

让 left_1 和 right_3 变成一个整体，变成 merge 的共同上游，就ok啦

### 4.2 checkpointer！

> **Checkpointer = 游戏存档系统**

（1）是什么？

可以把 LangGraph 想象成一个“流程型游戏”，每一次流程的运行都像玩家玩一局。Checkpointer 的作用就是：

- 记录当前 graph 的运行进度（包括节点状态、结果、中间变量等）
- 支持断点续跑（比如中断后恢复、跨 session 继续）
- 支持多个“存档”（不同用户 / session 不互相影响）

设想有这样一个流程图：

```
start → step1 → step2 → step3
```

用 `.invoke()` 执行时，它一步步执行这个流程。

没有 checkpointer  那么每次调用 `.invoke()` 都是“全新的一次执行”。所有状态、变量、过程，执行完就丢了，无法续接

有 checkpointer 也就是这存档呢？ 每次调用 `.invoke()` 都会“存档”    下次可以从上次停下来的地方继续（像 RPG 的 save/load）

（2）一个最简单用 checkpointer 的例子

```python
from langgraph.checkpoint import MemorySaver

...
graph = workflow.compile(
    checkpointer=MemorySaver()
)

config = {"configurable": {"thread_id": "John-9527"}}
r = graph.invoke(
    {"i": 1000, "j": 123},
    config=config
)
```

LangGraph 把每次执行的“上下文”存在 `thread_id` 的 key 下面。可以理解为：

- `thread_id = 存档编号`
- 同一个 `thread_id`：续接之前的执行
- 不同的 `thread_id`：不同玩家，和上一个玩家互不干扰，分别维护属于各自的“图状态”

```
r1 = graph.invoke(..., config={"configurable": {"thread_id": "user-A"}})
r2 = graph.invoke(..., config={"configurable": {"thread_id": "user-B"}})
```

而checkpointer要在图编译时实现，可选的有：checkpointer=MemorySaver()（把所有状态保存在内存中）  `SqliteSaver()`：保存到 SQLite 文件中

`RedisSaver()`：保存到 Redis   etc...



