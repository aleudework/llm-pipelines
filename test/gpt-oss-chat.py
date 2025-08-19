import lmstudio as lms
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools")))

from model import create_chat, add_message


model_ = lms.llm('openai/gpt-oss-120b')

sys_prompt = "Du er en model, som skal analysere vejr"

chat = create_chat(sys_prompt)

msg1 = 'Hvilke type vejr er det, når det kommer ovenfra. Svar med 10 ord'

res1, chat, stats1 = add_message(chat, msg1, 10, model_, stats=True)

msg2 = "Hvilke type vejr er det, når det larmer. Svar med 10 ord"


res2, chat, stats2 = add_message(chat, msg2, 10, model_, stats=True)


print(stats2)

print(res1)
print(res2)

print('-----')

print(chat)
