import asyncio
import copy
import inspect
import pandas as pd
import json

from typing import Union, List, Dict, Any, Callable
from abc import ABC, abstractmethod
from functools import partial

from .tool_ability import ToolAbility
from .executor_manager import ExecutorManager
from .memory_manager import MemoryManager
from .knowledge_manager import KnowledgeManager
from ..template import Template
from ..dataset import Dataset

class Runnable(ABC, ToolAbility, ExecutorManager):
    """
    实现基本可运行类，定义了可运行的基本接口。
    只要继承该类，就可以作为智能体的工具使用。
    """

    def __init__(
        self,
        # 线程组
        threads_group: str = None,
        # 是否自动停止
        continue_running=True,
        **kwargs
    ):
        """
        Runnable 的构造函数，主要包括：
        - 初始化线程组
        - 工具：作为工具的Runnable列表，在发现工具后是否执行工具的标记等
        """
        self.continue_running = continue_running

        ExecutorManager.__init__(self, threads_group)
        ToolAbility.__init__(self, **kwargs)

    @property
    def is_running(self):
        return self.continue_running

    def start(self):
        self.continue_running = True

    def stop(self):
        self.continue_running = False

    @abstractmethod
    def call(self, prompt: Union[str, List[dict], Template], *args, **kwargs):
        raise NotImplementedError("子类必须实现 call 方法")

    async def async_call(self, *args, **kwargs):
        """
        默认的异步调用，通过多线程实现。
        请注意，这会制造出大量线程，并不是最佳的性能优化方案。
        虽然不适合大规模部署，但这一方案可以在无需额外开发的情况下支持在异步环境中调用，快速验证业务逻辑。
        """
        loop = asyncio.get_running_loop()
        for block in await self.run_in_executor(self.call, *args, **kwargs):
            yield block

    async def run_in_executor(self, sync_function: Callable, *args, **kwargs):
        loop = asyncio.get_running_loop()
        func = partial(sync_function, *args, **kwargs)
        return await loop.run_in_executor(self.executor, func)

    def clone(self, **kwargs) -> "Runnable":
        """
        克隆当前对象，返回一个新的对象。

        如果提供 kwargs 参数，你就可以在克隆的同时修改对象属性。
        """
        return self.__class__(
            threads_group=kwargs.pop("threads_group") or self.threads_group,
            continue_running=kwargs.pop("continue_running") or self.continue_running,
            **kwargs
        )

class BaseAgent(Runnable, KnowledgeManager, MemoryManager):
    """
    实现基础的智能体类，支持知识管理、记忆管理和变量的发布订阅机制。
    
    基于 BaseAgent 子类可以实现多智能体协作。
    """

    def __init__(
        self,
        *args,
        memory: List[Union[str, "Template", Dict[str, Any]]] = None,
        k: int = 10,
        desk: Dict[str, Any] = None,
        **kwargs
    ):
        desk = desk or {}
        self.task = desk.get('task', None)
        self.draft = desk.get('draft', None)
        self.outline = desk.get('outline', None)
        self.data = desk.get('data', {})
        self.state = desk.get('state', {})

        super().__init__(*args, **kwargs)
        MemoryManager.__init__(self, memory, k)
        KnowledgeManager.__init__(self, desk.get('knowledge', []))

    def clone(self, **kwargs) -> "BaseAgent":
        """
        克隆当前对象，返回一个新的对象。

        如果提供 kwargs 参数，你就可以在克隆的同时修改对象属性。
        """
        return self.__class__(
            # 以下为 ExecutorManager 的参数
            threads_group=kwargs.pop("threads_group") or self.threads_group,
            # 以下为 Runnable 的参数
            continue_running=kwargs.pop("continue_running") or self.continue_running,
            # 以下为 MemoryManager参数
            memory=kwargs.pop("memory") or copy.deepcopy(self.init_memory),
            # 以下为 BaseAgent 的参数
            k=kwargs.pop("k") or self.remember_rounds,
            desk=kwargs.pop("desk") or copy.deepcopy(self.desk),
            **kwargs
        )

    @property
    def desk(self) -> Dict[str, Any]:
        """
        使用工作台变量实现跨智能体变量传递。
        这是 BaseAgent 子类的实例对象多有的统一规格。

        obj.desk 是一个只读属性，可以访问工作台变量的字典，字典中的键值主要包括：

        | 变量       | 生命周期       | 详细说明 |
        |:----------|:-------------:|:-----------------------------------------------------|
        | knowledge | 可手工维护    | 检索增强，添加方法 add_knowledge(knowledge: List[str])    |
        | data      | 可手工维护    | 数据分析，添加执行方法 add_data(data: pandas.DataFrame)    |
        | task      | 运行时修改    | 提问或输入，大模型调用开始自动修改                |
        | output    | 运行时修改    | 结果或输出，大模型调用结束自动修改                |
        | draft     | 运行时修改    | 写作任务中已完成的草稿，例如扩写任务中自动修改      |
        | outline   | 运行时修改    | 扩写提纲，在扩写任务中自动生成                   |
        | state     | 定制时使用    | 以上不够用时，建议使用state字典来定制状态数据      |
        """
        return {
            "task": self.task,
            "draft": self.draft,
            "outline": self.outline,
            "data": self.data,
            "state": self.state,
            # knowledge 在 KnowledgeManager 中定义
            "knowledge": self._knowledge,
            # output 在 MemoryManager 中作为只读属性定义
            "output": self.output,
        }
    
    def set_task(self, task: str):
        self.task = task

    def set_draft(self, draft: str):
        self.draft = draft

    def set_outline(self, outline: str):
        self.outline = outline

    def add_dataset(self, name: str, df: pd.DataFrame, desc: str=None):
        self.data[name] = Dataset(df, desc or name)

    def get_dataset(self, name: str):
        return self.data.get(name)
    
    def get_dataset_names(self):
        return list(self.data.keys())