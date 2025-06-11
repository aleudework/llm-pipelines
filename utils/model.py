import logging
import json
import lmstudio as lms


def response(prompt, idx, model, config=None, log_every=100):
    """
    Response with logged stats
    """
    try:
        if config:
            prediction_stream = model.respond_stream(prompt, config=config)
        else:
            prediction_stream = model.respond_stream(prompt)
    except Exception as e:
        logging.error(f"Fejl ved model.respond_stream for idx {idx}: {e}")
        return None

    try:
        for fragment in prediction_stream:
            pass
        result = prediction_stream.result()
    except Exception as e:
        logging.error(f"Fejl under stream/result for idx {idx}: {e}")
        return None
    
    try:

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
    except Exception as e:
        logging.warning(f"Kunne ikke logge stats for idx {idx}: {e}")

    return result.content


def default_schema(schema):
    if isinstance(schema, dict):
        return {key: None for key in schema.keys()}
    return {}  # fallback hvis schema ikke er dict


def response_structured(prompt, idx, model, schema, config=None, log_every=100):
    try:
        if config:
            prediction_stream = model.respond_stream(prompt, response_format=schema, config=config)
        else:
            prediction_stream = model.respond_stream(prompt, response_format=schema)
    except Exception as e:
        logging.error(f"Fejl ved model.respond_stream for idx {idx}: {e}")
        return None
    
    try:
        for fragment in prediction_stream:
            pass
        result = prediction_stream.result()
    except Exception as e:
        logging.error(f"Fejl under stream/result for idx {idx}: {e}")
        return None

    try:
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
    except Exception as e:
        logging.warning(f"Kunne ikke logge stats for idx {idx}: {e}")

    content = getattr(result, "content", None)
    if isinstance(content, str):
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError for idx {idx}: {e}")
            logging.error(f"Indhold: {repr(content)}")
            return default_schema(schema)
        except Exception as e:
            logging.error(f"Anden fejl ved JSON parsing for idx {idx}: {e}")
            return default_schema(schema)
    return content



def response_image_input(prompt, idx, model, images, config=None, log_every=100):
    image_handles = []
    for image in images:
        try:
            image_handle = lms.prepare_image(image)
            image_handles.append(image_handle)
        except Exception as e:
            logging.error(f"Fejl ved billede {image}: {e}")

    if not image_handles:
        logging.error(f"Ingen gyldige billeder til idx {idx}")
        return None

    chat = lms.Chat()
    chat.add_user_message(prompt, images=image_handles)
    
    try:
        if config:
            result = model.respond(
                chat,
                config=config
            )
        else:
            result = model.respond(
                chat
            )
    except Exception as e:
        logging.error(f"Fejl ved model.respond for idx {idx}: {e}")
        return None
    

    if (idx + 1) % log_every == 0:
        logging.info(f"Kørte model.respond for række {idx + 1}")
    
    return result.content

