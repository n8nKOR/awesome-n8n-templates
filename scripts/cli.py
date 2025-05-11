import os
from typing import Literal, Optional

import fire
import orjson
import requests
from dotenv import load_dotenv
from tqdm import tqdm


class CLI:
    def __init__(self):
        load_dotenv()

        self.provider_url = {
            "openai": "https://api.openai.com/v1/responses",
            "anthropic": "https://api.anthropic.com/v1/messages",
            "xai": "https://api.x.ai/v1/chat/completions",
            "gemini": None,
        }

        self.api_key = {
            "openai": os.getenv("OPENAI_API_KEY", None),
            "anthropic": os.getenv("ANTHROPIC_API_KEY", None),
            "xai": os.getenv("XAI_API_KEY", None),
            "gemini": os.getenv("GEMINI_API_KEY", None),
        }
        self.system_prompt = (
            "You are a professional translator. "
            "Your sole task is to translate content from English to Korean. "
            "Do not add explanations, commentary, or any extra text. "
            "Only return the translated result in Korean."
        )

        self.user_prompt = """### Instruction
Translate the following text from English to Korean.
Return only the translated Korean text, without any additional explanation or formatting.

### Input
{input_text}

### Output
"""

    def __convert_request_body(
        self, prompt: str, model: str, provider: Literal["openai", "anthropic", "xai", "gemini"], temp: float = 0.7
    ) -> tuple[dict, dict, str]:
        if provider == "openai":
            return (
                {
                    "model": model,
                    "input": [
                        {"role": "system", "content": [{"type": "input_text", "text": self.system_prompt}]},
                        {
                            "role": "user",
                            "content": [{"type": "input_text", "text": self.user_prompt.format(input_text=prompt)}],
                        },
                    ],
                },
                {"Authorization": f"Bearer {self.api_key[provider]}"},
                self.provider_url[provider],
            )
        elif provider == "anthropic":
            return (
                {
                    "model": model,
                    "max_tokens": 1024,
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": self.user_prompt.format(input_text=prompt)},
                    ],
                },
                {
                    "x-api-key": self.api_key[provider],
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                self.provider_url[provider],
            )
        elif provider == "xai":
            return (
                {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": self.user_prompt.format(input_text=prompt)},
                    ],
                },
                {"Authorization": f"Bearer {self.api_key[provider]}"},
                self.provider_url[provider],
            )
        elif provider == "gemini":
            return (
                {
                    "model": model,
                    "contents": [
                        {
                            "role": "user",
                            "parts": [
                                {"text": self.system_prompt},
                                {"text": self.user_prompt.format(input_text=prompt)},
                            ],
                        }
                    ],
                    "generationConfig": {"responseMimeType": "text/plain"},
                },
                None,
                "https://generativelanguage.googleapis.com/v1beta/models/${model}:${GENERATE_CONTENT_API}?key=${self.api_key[provider]}",
            )

    def __llm_api_call(
        self, prompt: str, model: str, provider: Literal["openai", "anthropic", "xai", "gemini"], temp: float = 0.7
    ) -> str:
        json_data, headers, url = self.__convert_request_body(prompt, model, provider, temp)
        res = requests.post(url=url, headers=headers, json=json_data)
        res = res.json()
        return res["choices"][0]["message"]["content"]

    def run(
        self,
        file: str,
        model: Literal[
            "grok-3-mini-beta",
            "gpt-4o-mini",
            "claude-3-5-sonnet-20240620",
            "gpt-4o",
            "claude-3-5-sonnet",
            "gemini-1.5-flash-002",
            "gemini-1.5-pro-002",
        ],
        provider: Literal["openai", "anthropic", "xai", "gemini"] = "openai",
        temp: Optional[float] = 0.7,
    ):
        if not os.path.exists(file):
            raise FileNotFoundError(f"존재하지 않는 파일 : {file}")

        try:
            # json 파일 로드
            with open(file, mode="r", encoding="utf-8") as f:
                root_node = orjson.loads(f.read())
        except Exception as e:
            raise e

        original_nodes = root_node["nodes"]

        # 스티키 노트 노드만 필터링
        nodes = [(i, node) for i, node in enumerate(original_nodes)]
        sticky_nodes = [(i, node) for (i, node) in nodes if node["type"] == "n8n-nodes-base.stickyNote"]

        for i, sticky_node in tqdm(sticky_nodes):
            content = self.__llm_api_call(sticky_node["parameters"]["content"], model, provider, temp)
            original_nodes[i]["parameters"]["content"] = content

        root_node["nodes"] = original_nodes

        with open(file, "w", encoding="utf-8") as f:
            f.write(orjson.dumps(root_node, option=orjson.OPT_INDENT_2).decode("utf-8"))


if __name__ == "__main__":
    fire.Fire(CLI)
