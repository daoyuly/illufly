import copy
import pandas as pd
import asyncio

from typing import Union, List, Dict, Any, Callable, Generator, AsyncGenerator

from .tool_ability import ToolAbility
from ...dataset import Dataset
from ..base import Runnable
from ....io import EventBlock

class BaseAgent(Runnable, ToolAbility):
    """    
    基于 BaseAgent 子类可以实现多智能体协作。

    什么时候直接从 BaseAgent 继承？
    - 需要 Runnable 基类的能力的同时
    - 还需要作为工具被使用
    - 例如，多模态模型

    什么时候转而使用ChatAgent？
    - 需要管理记忆、知识、数据等上下文
    - 例如，对话模型
    """

    def __init__(
        self,
        func: Callable=None,
        async_func: Callable=None,
        **kwargs
    ):
        Runnable.__init__(self, **kwargs)
        ToolAbility.__init__(self, func=func, async_func=async_func, **kwargs)

        desc = kwargs.get("description", func.__doc__ if func and func.__doc__ else "")
        if desc:
            self.description = desc

    @property
    def runnable_info(self):
        info = super().runnable_info
        info.update({
            "agent_name": self.name,
            "agent_description": self.description,
        })
        return info

    def call(self, *args, **kwargs):
        if not isinstance(self.func, Callable):
            raise ValueError("func must be a callable")

        resp = self.func(*args, **kwargs)
        if isinstance(resp, Generator):
            yield from resp
        else:
            yield EventBlock("chunk", resp)

    async def async_call(self, *args, **kwargs):
        if self.async_func:
            # 使用 asyncio.iscoroutinefunction 判断是否为协程函数
            if asyncio.iscoroutinefunction(self.async_func):
                resp = await self.async_func(*args, **kwargs)
            else:
                resp = self.async_func(*args, **kwargs)
        else:
            resp = self.func(*args, **kwargs)
        if isinstance(resp, Generator):
            for block in resp:
                yield block
        elif isinstance(resp, AsyncGenerator):
            async for block in resp:
                yield block
        else:
            yield EventBlock("chunk", resp)