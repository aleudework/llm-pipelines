import lmstudio as lms
import logging


import logging

logging.basicConfig(
    level=logging.INFO,                      # Vælg log-niveau (INFO, DEBUG, ERROR osv.)
    format='%(levelname)s: %(message)s'     # Enkel visning af logbeskeder
)




def create_chat(system_prompt):
    return lms.Chat(system_prompt)

def add_message(chat, message, idx, model, model_config=None, log_every=100):

    try:
        response = ""
        chat.add_user_message(message)
        
        if model_config:
            prediction_stream = model.respond_stream(chat, on_message=chat.append, config=model_config)
        else:
            prediction_stream = model.respond_stream(chat, on_message=chat.append)

    except Exception as e:
        logging.error(f"Fejl ved model.respond_stream for idx {idx}: {e}")
        return None
    
    try:
        for fragment in prediction_stream:
            response += fragment.content
        result_info = prediction_stream.result()
        print(prediction_stream.result().stats)

    except Exception as e:
        logging.error(f"Fejl under stream/result for idx {idx}: {e}")
        return None
    
    try:
        if log_every != -1:
            if (idx + 1) % log_every == 0:
                time_to_first_token = result_info.stats.timeToFirstTokenSec
                prompt_token_count = result_info.stats.promptTokensCount
                token_count = result_info.stats.predicted_tokens_count
                tokens_sec = result_info.stats.tokens_per_second
                stop_reason = result_info.stats.stop_reason
                msg = (
                    f"[Row {idx+1}] "
                    f"Prompt tokens: {prompt_token_count} | "
                    f"Time to first token: {time_to_first_token} | "
                    f"Tokens/sec: {tokens_sec:.2f} | "
                    f"Total tokens: {token_count} | "
                    f"Stop reason: {stop_reason}"
                )
                logging.info(msg)
    except Exception as e:
        logging.warning(f"Kunne ikke logge stats for idx {idx}: {e}")

    return response, chat

    
model_ = lms.llm('qwen/qwen3-235b-a22b')


sys = 'Du er en super hjælpsom chatbot'
msg = 'Hvordan er vejret i København?'
msg2 = 'Hvad har jeg lige spurgt dig om?'

dic = {
    'temperature': 0.9
}

ch = create_chat(sys)
print(ch)
res1, ch = add_message(ch, msg, 0, model_, dic, 1)
res2, ch = add_message(ch, msg2, 0, model_, {'max_tokens': 5}, 1)

print(res2)
print(ch)
