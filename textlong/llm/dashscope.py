from typing import Union, List, Optional
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.human import HumanMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.memory.chat_memory import BaseChatMemory

from http import HTTPStatus
from ...io import TextBlock, stream_log
from ...config import get_env

import dashscope
import json

def qwen(
    prompt: Union[str, List[dict]],
    model: str="qwen-max",
    **kwargs):
    """
    Args:
    - prompt 支持字符串提示语或消息列表。

    Example:
        messages = [
            {'role':'system','content':'you are a helpful assistant'},
            {'role': 'user','content': '你是谁？'}
        ]

        stream(qwen, messages)
    """

    # 转换消息格式
    _messages = None
    _prompt = None
    if isinstance(prompt, str):
        _prompt = prompt
    else:
        _messages = prompt

    # 调用生成接口
    responses = dashscope.Generation.call(
        model="qwen-max",
        messages=_messages,
        prompt=_prompt,
        seed=1234,
        top_p=0.8,
        result_format='message',
        max_tokens=1500,
        temperature=0.85,
        repetition_penalty=1.0,
        stream=True,
        incremental_output=True,
        **kwargs
        )

    # 流输出
    for response in responses:
        if response.status_code == HTTPStatus.OK:
            ai_output = response.output.choices[0].message
            if 'tool_calls' not in ai_output:
                content = ai_output.content
                yield TextBlock("chunk", content)
            else:
                for func in ai_output.tool_calls:
                    yield TextBlock("tools_call", json.dumps(func))
        else:
            yield TextBlock("info", ('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            )))