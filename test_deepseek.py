from openai import OpenAI

client = OpenAI(
    api_key="sk-lsppjamzxrcfktjogxxakhpvebzdpcusuvystaziktgfsmfy",
    base_url="https://api.siliconflow.cn/v1"
)

response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1",
    messages=[
        {"role": "user", "content": "请简要介绍SiliconFlow平台的特点。"}
    ],
    stream=True  # 启用流式输出
)

for chunk in response:
    if not chunk.choices:
        continue
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)
    if hasattr(delta, "reasoning_content") and delta.reasoning_content:
        print(delta.reasoning_content, end="", flush=True)
