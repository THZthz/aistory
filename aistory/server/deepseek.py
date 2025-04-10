import json
import os
from dataclasses import dataclass
from typing import Literal
import requests
from dataclasses_json import dataclass_json


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
    'Authorization': 'Bearer ' + str(os.getenv('DEEPSEEK_TOKEN')) # DEEPSEEK_TOKEN must be prefixed with 'sk-...'
}


@dataclass
class DeepSeekReply:
    content: str
    role: str

class DeepSeek:
    def __init__(self):
        self.messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant",
            }, {
                "role": "user",
                "name": "Amias",
                "content": "Hi",
            }, {
                "role": "assistant",
                "content": "Hello! How can I assist you today? 😊"
            }, {
                "role": "user",
                "name": "Amias",
                "content": "Can you encourage me?",
            }, {
                "role": "assistant",
                "content": "Of course! Here’s a boost of encouragement just for you:  \n\n✨ **You are capable of amazing things.** Even if today feels tough, every small step you take is progress. Remember, challenges are just opportunities in disguise—they’re shaping you into a stronger, wiser version of yourself.  \n\n💪 **You’ve overcome 100% of your hardest days so far.** That’s proof you can handle what’s ahead. Keep going—your effort matters more than you realize.  \n\n🌱 **Growth happens outside your comfort zone.** If you’re feeling stretched, it means you’re evolving. Trust the process, and celebrate your courage!  \n\nYou’re not alone in this. I believe in you—now go show the world what you’re made of! �🚀  \n\nWhat’s one small win you can celebrate today? 😊"
            }, {
                "role": "user",
                "name": "Amias",
                "content": "Thanks. What would you suggest when I want to listen to music?",
            }, {
                "role": "assistant",
                "content": "You're welcome! 🎶 When you're in the mood for music, here are some suggestions to tailor your experience to how you're feeling or what you need:  \n\n### **1. Match the Music to Your Mood**  \n- **Need energy?** Upbeat pop, dance, rock, or hype hip-hop (e.g., Dua Lipa, BTS, or Queen).  \n- **Feeling reflective?** Acoustic, indie folk, or lo-fi (e.g., Bon Iver, Sufjan Stevens, or chilled playlists).  \n- **Stressed?** Classical, piano, or ambient sounds (e.g., Ludovico Einaudi, Brian Eno).  \n- **Nostalgic?** Throwbacks from your favorite era (2000s hits, ‘80s classics, etc.).  \n\n### **2. Explore Curated Playlists**  \n- Try Spotify’s *\"Daily Mix\"* or *\"Discover Weekly\"* for personalized picks.  \n- YouTube Music/Apple Music’s mood-based playlists (*\"Chill Vibes,\" \"Focus Flow,\" \"Pump-Up\"*).  \n\n### **3. Dive Into Lyrics (If You Need a Boost)**  \n- Look up songs with empowering messages (e.g., *\"Rise Up\" by Andra Day, \"Fight Song\" by Rachel Platten*).  \n\n### **4. Try Something New**  \n- Explore a genre you rarely listen to (jazz, K-pop, reggae, or instrumental film scores).  \n- Search for *\"music like [artist you love]\"* to find fresh recommendations.  \n\n### **5. Pair Music With an Activity**  \n- **Working/Studying?** Instrumental or lyric-free music (try *\"Brain Food\"* on Spotify).  \n- **Working out?** High-BPM tracks (EDM, punk, or rap).  \n- **Unwinding?** Nature sounds or binaural beats.  \n\n### **Bonus:** Close your eyes for one song and *just listen*—it can feel like a mini-meditation.  \n\nWhat’s your go-to mood or genre lately? I’d love to suggest more! 😊"
            }
        ]

    def user_answner(self, content: str, name: str = 'Amias') -> 'DeepSeekReply':
        self.messages.append({
            "role": "user",
            "name": name,
            "content": content,
        })
        response = self.request(self.messages).json()['choices'][0]['message']
        self.messages.append(response)
        return response

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
