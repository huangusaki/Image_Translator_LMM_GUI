"""
Gemini 模型列表获取模块
使用 OpenAI 兼容 API 从 Google AI 获取可用的 Gemini 模型列表。
"""

from typing import List, Optional


def fetch_gemini_models(api_key: str, proxy_url: Optional[str] = None) -> List[str]:
    """
    使用 OpenAI 兼容 API 获取 Gemini 可用模型列表。
    Args:
        api_key: Gemini API Key
        proxy_url: 可选的代理 URL (例如 "http://127.0.0.1:7890")
    Returns:
        以 'gemini' 开头的模型名称列表（已去除 'models/' 前缀），按字母排序
    """
    try:
        from openai import OpenAI
        import httpx

        http_client = None
        if proxy_url:
            http_client = httpx.Client(proxy=proxy_url)
        client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            http_client=http_client,
        )
        models = client.models.list()
        gemini_models = []
        for model in models:
            model_id = model.id
            if model_id.startswith("models/"):
                model_id = model_id[7:]
            if model_id.startswith("gemini"):
                gemini_models.append(model_id)
        return sorted(gemini_models)
    except ImportError:
        print("警告: openai 库未安装，无法获取模型列表")
        return []
    except Exception as e:
        print(f"获取 Gemini 模型列表失败: {e}")
        return []


DEFAULT_GEMINI_MODELS = [
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash",
    "gemini-1.5-pro-latest",
    "gemini-1.5-pro",
    "gemini-2.0-flash-exp",
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.5-pro-preview-06-05",
]
