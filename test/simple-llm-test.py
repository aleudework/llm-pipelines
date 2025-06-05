import lmstudio as lms
import time

model = lms.llm("qwen/qwen3-235b-a22b")

try:
    stream = model.respond_stream("What is the meaning of life? Explain in Danish")
except Exception as e:
    print(f"Fejl ved model.respond_stream: {e}")
    stream = None

if stream:
    buffer = []
    token_counter = 0
    group_start_time = time.time()

    try:
        for fragment in stream:
            token = getattr(fragment, "content", "")
            buffer.append(token)
            token_counter += 1

            if token_counter % 50 == 0:
                group_end_time = time.time()
                group_time = group_end_time - group_start_time
                tokens_sec = 50 / group_time if group_time > 0 else 0

                print(f"\n[{token_counter} tokens] {''.join(buffer)}")
                print(f"Tokens/sec (last 50): {tokens_sec:.2f}")

                buffer = []
                group_start_time = time.time()

        # Print resterende tokens
        if buffer:
            group_end_time = time.time()
            group_time = group_end_time - group_start_time
            tokens_sec = len(buffer) / group_time if group_time > 0 else 0

            print(f"\n[{token_counter} tokens total] {''.join(buffer)}")
            print(f"Tokens/sec (last group): {tokens_sec:.2f}")

        result = stream.result()
        print(f"\nSlut. Stop reason: {result.stats.stop_reason}")

    except Exception as e:
        print(f"Fejl under stream/result: {e}")