import lmstudio as lms


model = lms.llm("meta-llama-3.1-8b-instruct")
result = model.respond("Give me a short answer")

print(result)
