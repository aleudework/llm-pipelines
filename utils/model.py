import logging
import json

def response_structured(prompt, idx, model, schema, config=None, log_every=100):
    """
    Generate a structured response from the LLM and log relevant statistics.

    Args:
        prompt (str): The prompt to send to the model.
        idx (int): The current row index (0-based).
        model: The model object (from lmstudio).
        schema: Pydantic schema or dict for response parsing.
        config (dict, optional): Model parameters. If None, defaults are used.
        log_every (int): Log statistics every Nth row.

    Returns:
        dict or Pydantic model: The model's response, either as an object or dict.
    """

    # Start prediction stream, with config if provided
    if config:
        prediction_stream = model.respond_stream(prompt, response_format=schema, config=config)
    else:
        prediction_stream = model.respond_stream(prompt, response_format=schema)

    # Iterate through the stream (we only use the final result)
    for fragment in prediction_stream:
        pass  # You could print(fragment.content) here to see streaming output

    # Retrieve the final result and its statistics
    result = prediction_stream.result()

    # Log statistics for this row at the chosen interval
    if (idx + 1) % log_every == 0:
        token_count = result.stats.predicted_tokens_count
        tokens_sec = result.stats.tokens_per_second
        stop_reason = result.stats.stop_reason
        msg = (
            f"[Row {idx+1}] "
            f"Tokens/sec: {tokens_sec:.2f} | "
            f"Total tokens: {token_count} | "
            f"Stop reason: {stop_reason}"
        )
        logging.info(msg)

    # Return content as dict if it's a JSON string, otherwise return as object
    content = result.content
    if isinstance(content, str):
        return json.loads(content)
    return content