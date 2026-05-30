#!/usr/bin/env python3
"""LLM 客户端 - DeepSeek API 封装"""
import json
import os
import httpx
from typing import Optional


def load_config() -> dict:
    """加载项目配置"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.json")
    with open(config_path) as f:
        return json.load(f)


class LLMClient:
    """
    LLM API 客户端

    支持:
    - 普通对话 (chat)
    - 流式输出 (stream)
    - 系统提示词
    - 对话历史管理
    """

    def __init__(self, config_path: str = None):
        if config_path:
            with open(config_path) as f:
                cfg = json.load(f)
        else:
            cfg = load_config()

        dsc = cfg['deepseek']
        self.api_key = dsc['api_key']
        self.base_url = dsc['base_url']
        self.model = dsc.get('model', 'deepseek-chat')
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )

    def chat(self, messages: list, temperature: float = 0.3,
             max_tokens: int = 2048, stream: bool = False) -> str:
        """
        对话接口

        Args:
            messages: [{"role": "system"/"user"/"assistant", "content": "..."}]
            temperature: 温度参数 (0.0-1.0)
            max_tokens: 最大输出 token 数
            stream: 是否流式输出

        Returns: 回复文本
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        try:
            response = self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            error_detail = ""
            if hasattr(e, 'response') and e.response:
                try:
                    error_detail = e.response.text[:200]
                except:
                    error_detail = str(e.response)
            return f"[LLM Error] {e}\n{error_detail}"

    def chat_stream(self, messages: list, temperature: float = 0.3,
                    max_tokens: int = 2048):
        """
        流式对话接口（生成器）
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        try:
            with self.client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data['choices'][0]['delta']
                            if 'content' in delta:
                                yield delta['content']
                        except:
                            continue
        except Exception as e:
            yield f"[LLM Error] {e}"

    def count_tokens(self, text: str) -> int:
        """估算 token 数（粗略）"""
        return len(text) // 2  # 中英文混合粗略估算

    def test_connection(self) -> bool:
        """测试 API 连通性"""
        try:
            resp = self.chat([{"role": "user", "content": "Hello"}])
            return "Error" not in resp and resp.strip() != ""
        except:
            return False


if __name__ == "__main__":
    llm = LLMClient()
    print(f"Model: {llm.model}")
    print(f"Test: {llm.test_connection()}")
    resp = llm.chat([{"role": "user", "content": "请用一句话介绍你自己"}])
    print(f"Response: {resp[:100]}")
