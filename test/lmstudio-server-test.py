import lmstudio as lms


model = lms.llm("openai/gpt-oss-120b")
result = model.respond("Give me a short answer")

print(result)
