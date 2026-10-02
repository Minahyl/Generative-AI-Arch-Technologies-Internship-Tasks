import requests


OLLAMA_URL = "http://127.0.0.1:11434/api/chat"

MODEL_NAME = "qwen2.5:0.5b"


def generate_response(messages):

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=300,
        )

        response.raise_for_status()

        data = response.json()

        return data["message"]["content"]

    except requests.exceptions.ConnectionError:

        return (
            "⚠️ Could not connect to Ollama.\n\n"
            "Please make sure Ollama is running."
        )

    except requests.exceptions.Timeout:

        return (
            "⚠️ Qwen took too long to respond."
        )

    except requests.exceptions.RequestException as error:

        return (
            f"⚠️ Ollama request failed:\n\n{error}"
        )

    except (KeyError, ValueError):

        return (
            "⚠️ Invalid response received from Ollama."
        )