import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler


OPENAI_URL = "https://api.openai.com/v1/responses"
MODEL = "gpt-5.6-luna"


def ask_openai(message):
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise Exception("OPENAI_API_KEY не найден в Vercel.")

    data = {
        "model": MODEL,
        "instructions": (
            "Ты Зея — дружелюбный AI-консьерж для отелей. "
            "Отвечай на языке пользователя. "
            "Помогай с вопросами об отеле, ресторанах, трансфере, "
            "экскурсиях, сервисах и путешествиях. "
            "Отвечай понятно и коротко. "
            "Никогда не придумывай часы работы, цены, правила отеля "
            "или другие факты, которых у тебя нет. "
            "Если точной информации нет — честно скажи об этом."
        ),
        "input": message
    }

    request = urllib.request.Request(
        OPENAI_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))

    except urllib.error.HTTPError as e:
        error_text = e.read().decode("utf-8", errors="ignore")
        raise Exception("OpenAI API error: " + error_text)

    # Получаем текст ответа
    if result.get("output_text"):
        return result["output_text"]

    texts = []

    for item in result.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                text = content.get("text", "")
                if text:
                    texts.append(text)

    if texts:
        return "\n".join(texts)

    return "Не удалось получить ответ от ИИ."


class handler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        body = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )
        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, OPTIONS"
        )
        self.end_headers()

        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json(200, {"ok": True})

    def do_GET(self):
        self.send_json(
            200,
            {
                "ok": True,
                "message": "Зея работает"
            }
        )

    def do_POST(self):
        try:
            content_length = int(
                self.headers.get("Content-Length", "0")
            )

            body = self.rfile.read(content_length)

            data = json.loads(
                body.decode("utf-8")
            )

            message = str(
                data.get("message", "")
            ).strip()

            if not message:
                self.send_json(
                    400,
                    {
                        "error": "Сообщение пустое"
                    }
                )
                return

            reply = ask_openai(message)

            self.send_json(
                200,
                {
                    "reply": reply
                }
            )

        except Exception as e:
            self.send_json(
                500,
                {
                    "error": str(e)
                }
            )
