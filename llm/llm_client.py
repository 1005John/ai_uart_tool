#!/usr/bin/env python3
"""LLM 客户端 — 支持 DeepSeek / Aliyun 等多个 Provider，密钥从本地安全文件加载"""
import json
import os
import httpx
from pathlib import Path
from typing import Optional


# ── 密钥加载 ──

# 密钥文件优先级（先找到哪个用哪个）
KEY_PATHS = [
    Path.home() / ".ai_uart_keys.json",               # 内置硬盘（推荐，永不提交）
    Path.home() / ".claude" / "ai_uart_keys.json",    # Claude Code 配置目录
]


def _load_keys() -> dict:
    """加载 API 密钥，按优先级依次尝试"""
    for p in KEY_PATHS:
        if p.exists():
            try:
                with open(p) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                continue
    # 降级：项目内 config.example.json（模板，不含真实密钥）
    fallback = Path(__file__).parent.parent / "config" / "config.example.json"
    if fallback.exists():
        with open(fallback) as f:
            return json.load(f)
    return {}


def _get_provider_config(provider: str = None) -> dict:
    """获取指定 provider 的配置"""
    keys = _load_keys()
    active = provider or keys.get("active_provider", "deepseek")
    cfg = keys.get(active, {})
    if not cfg.get("api_key") or "YOUR_" in str(cfg.get("api_key", "")):
        raise RuntimeError(
            f"❌ Provider '{active}' 的 API Key 未配置。\n"
            f"请在 ~/.ai_uart_keys.json 中填入真实密钥。\n"
            f"模板参考: config/config.example.json"
        )
    return cfg


class LLMClient:
    """
    LLM API 客户端

    支持多 provider:
    - deepseek (DeepSeek V4 Flash)
    - aliyun   (阿里云通义千问 Qwen3.6-Plus)

    密钥从 ~/.ai_uart_keys.json 加载（内置硬盘，不提交 Git）
    """

    def __init__(self, provider: str = None):
        """
        Args:
            provider: 指定 provider 名称，None 则使用 active_provider
        """
        cfg = _get_provider_config(provider)

        self.provider = provider or _load_keys().get("active_provider", "deepseek")
        self.api_key = cfg["api_key"]
        self.base_url = cfg["base_url"]
        self.model = cfg.get("model", "deepseek-chat")

        self.client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )

    # ── 对话 ──

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
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            error_detail = ""
            if hasattr(e, "response") and e.response:
                try:
                    error_detail = e.response.text[:200]
                except Exception:
                    error_detail = str(e.response)
            return f"[LLM Error] {e}\n{error_detail}"

    # ── 流式对话 ──

    def chat_stream(self, messages: list, temperature: float = 0.3,
                    max_tokens: int = 2048):
        """流式对话接口（生成器）"""
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
                            delta = data["choices"][0]["delta"]
                            if "content" in delta:
                                yield delta["content"]
                        except Exception:
                            continue
        except Exception as e:
            yield f"[LLM Error] {e}"

    # ── 工具方法 ──

    def count_tokens(self, text: str) -> int:
        """估算 token 数（中英文混合粗略估算）"""
        return len(text) // 2

    def test_connection(self) -> bool:
        """测试 API 连通性"""
        try:
            resp = self.chat([{"role": "user", "content": "Hello"}])
            return "Error" not in resp and resp.strip() != ""
        except Exception:
            return False

    # ── 动态切换 provider ──

    @classmethod
    def switch_provider(cls, provider: str):
        """创建指定 provider 的新实例"""
        return cls(provider=provider)

    @staticmethod
    def list_available_providers() -> list[str]:
        """列出所有已配置密钥的 provider"""
        keys = _load_keys()
        available = []
        for name in ("deepseek", "aliyun"):
            cfg = keys.get(name, {})
            key = cfg.get("api_key", "")
            if key and "YOUR_" not in str(key):
                available.append(name)
        return available


# ── 兼容旧代码的快捷函数 ──

def load_config() -> dict:
    """
    兼容旧代码，返回当前活动 provider 的配置
    新代码请用 LLMClient() 直接实例化
    """
    cfg = _get_provider_config()
    return {cfg.get("model", "deepseek-chat").split("-")[0]: cfg}


if __name__ == "__main__":
    print(f"可用 Provider: {LLMClient.list_available_providers()}")
    for p in LLMClient.list_available_providers():
        try:
            llm = LLMClient(provider=p)
            ok = llm.test_connection()
            print(f"  {p}: model={llm.model}  {'✅ 连通' if ok else '❌ 失败'}")
        except RuntimeError as e:
            print(f"  {p}: {e}")
