import lmstudio as lms
chat = lms.Chat()
model = lms.llm("google/gemma-3-27b")

help(chat.add_user_message)