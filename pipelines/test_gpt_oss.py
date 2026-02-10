from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="not-needed"
)

resp = client.chat.completions.create(
    model="openai/gpt-oss-120b",  # brug den model-id LM Studio viser
    messages=[
        {"role": "system", "content": "Svar kort på dansk."},
        {"role": "user", "content": "Hvad er 2+2+17?"}
    ],
)

print(resp.choices[0].message.content)