import json
import os
from dataclasses import dataclass
from typing import Literal
import requests
from dataclasses_json import dataclass_json

from aistory.constants import PATH


@dataclass_json
@dataclass
class ToolFuncParam:
    description: str
    type: str = 'string'


@dataclass_json
@dataclass
class ToolFuncParams:
    properties: dict[str, ToolFuncParam]
    required: list[str]
    type: str = 'object'


@dataclass_json
@dataclass
class ToolFunction:
    name: str
    description: str
    parameters: ToolFuncParams


@dataclass_json
@dataclass
class Tool:
    function: ToolFunction
    type: str = 'function'


def get_tool(func_name: str, func_desc: str, parameters: list[tuple[str, str]], required: list[str]) -> Tool:
    """
    :param func_name:
    :param func_desc:
    :param parameters: tuple[str, str], parameter's name and description.
    :param required: list required parameters' name.
    :return:
    """

    properties = {}
    for name, desc in parameters:
        properties[name] = ToolFuncParam(description=desc)
    parameters = ToolFuncParams(required=required, properties=properties)
    function = ToolFunction(name=func_name, description=func_desc, parameters=parameters)
    return Tool(function=function)


URL_COMPLETIONS = "https://api.deepseek.com/chat/completions"

HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + str(os.getenv('DEEPSEEK_API_KEY')) # DEEPSEEK_API_KEY must be prefixed with 'sk-...'
}


@dataclass
class DeepSeekReply:
    content: str
    role: str

class DeepSeek:
    def __init__(self):
        with open(PATH('database/deepseek.histories.json'), 'r', encoding='utf-8') as file:
            self.messages = json.load(file)['messages']

    def save(self):
        with open(PATH('database/deepseek.histories.json'), 'w', encoding='utf-8') as file:
            file.write(json.dumps({"messages": self.messages}, indent=4))

    def user_answner(self, content: str, name: str = 'Amias') -> 'DeepSeekReply':
        self.messages.append({
            "role": "user",
            "name": name,
            "content": content,
        })

        try:
            res_json = self.request(self.messages).json()
            print(res_json)
            res = res_json['choices'][0]['message']
            self.messages.append(res)
            return res
        except Exception as e:
            print(f'{type(e).__name__}: {e}')
            res = DeepSeekReply(content="*Error occured when connecting to DeepSeek's server.*", role='assistant')
            self.messages.append(res)
            return res

    @staticmethod
    def request(messages,
                temperature=1,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                max_tokens=2048,
                stop: str | list[str] | None = None,
                tools: Tool = None,
                tool_choice: object | str = 'auto',
                logprobs=False,
                top_logprobs=None,
                response_format: Literal['text', 'json_object'] = 'text') -> 'requests.Response':
        payload = json.dumps({
            "messages": messages,
            "model": "deepseek-chat",
            "frequency_penalty": frequency_penalty,
            "max_tokens": max_tokens,
            "presence_penalty": presence_penalty,
            "response_format": {
                "type": response_format
            },
            "stop": stop,
            "stream": False,
            "stream_options": None,
            "temperature": temperature,
            "top_p": top_p,
            "tools": tools.to_json() if tools else None,
            "tool_choice": tool_choice,
            "logprobs": logprobs,
            "top_logprobs": top_logprobs
        })

        response = requests.request("POST", URL_COMPLETIONS, headers=HEADERS, data=payload)
        return response
