import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler


OPENAI_URL = "https://api.openai.com/v1/responses"
MODEL = "gpt-5.6-luna"


SYSTEM_INSTRUCTIONS = """
Ты — Зея, умный женский AI-консьерж для отелей и путешествий.

Твои ответы автоматически озвучиваются голосом приложения.

ВАЖНЫЕ ПРАВИЛА:

1. Никогда не говори пользователю:
   - «я не могу говорить»
   - «я не могу разговаривать»
   - «я отвечаю только текстом»
   - «голосовая функция недоступна»
   - «в этом чате я не могу говорить»

2. Не обсуждай техническую работу голосовой функции,
   если пользователь сам не спрашивает о технической стороне.

3. Отвечай на том языке, на котором пишет пользователь.

4. Если пользователь пишет по-турецки —
   отвечай естественным современным турецким языком.
   Используй правильную турецкую грамматику и естественные фразы.

5. Если пользователь пишет по-русски —
   отвечай по-русски.

6. Если пользователь пишет на другом языке —
   отвечай на этом языке.

7. Ты — женский AI-помощник по имени Зея.

8. Отвечай дружелюбно, естественно и не слишком длинно.

9. Не выдумывай конкретные факты об отеле:
   цены, расписание, часы работы, наличие мест,
   правила, адреса и другие данные.

10. Если точной информации нет,
    честно скажи об этом и предложи помочь другим способом.

11. Если пользователь просто хочет поговорить,
    поддерживай обычный разговор.

12. Если пользователь спрашивает:
    «Можешь говорить?»
    или похожий вопрос,
    не отвечай, что ты не умеешь говорить.
    Скажи естественно, например:
    «Конечно 😊 Я могу озвучивать свои ответы.»

13. Не добавляй технические пояснения в обычные ответы.

14. Не говори от имени отеля, если у тебя нет подтверждённой
    информации от самого отеля.

15. Для турецкого языка используй естественный стиль,
    подходящий для общения с туристами в Турции.

Ты — Зея. Отвечай как настоящий дружелюбный AI-консьерж.
"""


def ask_openai(message):

    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        raise Exception(
            "OPENAI_API_KEY не найден в Vercel."
        )

    data = {
        "model": MODEL,
        "instructions": SYSTEM_INSTRUCTIONS,
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

        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as e:

        error_text = e.read().decode(
            "utf-8",
            errors="ignore"
        )

        raise Exception(
            "OpenAI API error: " + error_text
        )

    if result.get("output_text"):

        return result["output_text"]


    texts = []

    for item in result.get("output", []):

        for content in item.get(
            "content",
            []
        ):

            if content.get(
                "type"
            ) == "output_text":

                text = content.get(
                    "text",
                    ""
                )

                if text:
                    texts.append(text)


    if texts:

        return "\n".join(texts)


    return "Извините, я не смогла сформировать ответ."


class handler(BaseHTTPRequestHandler):


    def send_json(
        self,
        status,
        data
    ):

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

        self.send_json(
            200,
            {
                "ok": True
            }
        )


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
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )


            body = self.rfile.read(
                content_length
            )


            data = json.loads(
                body.decode("utf-8")
            )


            message = str(
                data.get(
                    "message",
                    ""
                )
            ).strip()


            if not message:

                self.send_json(
                    400,
                    {
                        "error":
                        "Сообщение пустое"
                    }
                )

                return


            reply = ask_openai(
                message
            )


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
