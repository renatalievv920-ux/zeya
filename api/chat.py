import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler
OPENAI_URL = "https://api.openai.com/v1/responses"
MODEL = "gpt-5.6-luna"
HOTEL_KNOWLEDGE = """
ОТЕЛЬ:
Selectum Noa Belek, Belek, Antalya, Türkiye.
Ты — Зея, AI-консьерж именно этого отеля.
ВАЖНО:
- Пользователь уже находится в контексте Selectum Noa Belek.
- Никогда не спрашивай: "В каком отеле вы находитесь?"
- Никогда не спрашивай название отеля.
- Не предлагай выбрать отель.
- Всегда считай, что вопросы относятся к Selectum Noa Belek.
ПИТАНИЕ — SUMMER 2026:
Main Restaurant:
Завтрак: 07:00–10:30
Обед: 12:30–14:30
Ужин: 18:00–21:00
Seven Twenty Four Restaurant:
Работает в часы, когда Main Restaurant закрыт.
Международная кухня à la carte.
Бронирование не требуется.
Feel Good Grab to Go Snack Restaurant:
12:00–16:00
Food Corner:
12:00–16:00
Gözleme House:
11:00–16:00
Patisserie:
12:00–18:00
Tabla Kebap Türk A la Carte Restaurant:
19:00–22:00
Требуется бронирование.
Harbour Sea & Salt Balık A la Carte Restaurant:
19:00–22:00
Требуется бронирование.
Primavio Cucina Italiana A la Carte Restaurant:
19:00–22:00
Требуется бронирование.
ОСНОВНЫЕ УСЛУГИ:
- пляж
- бассейны
- SPA
- фитнес
- спортивные активности
- развлечения
- детские активности
- рестораны и бары
- трансфер
- экскурсии
ПРАВИЛО ТОЧНОСТИ:
Если точной информации в этой базе нет, НЕ придумывай её.
Не выдумывай цены, расписание анимации, номера комнат, правила, расположение объектов или другие конкретные данные.
В таком случае скажи пользователю, что точной информации у тебя сейчас нет.
Если информация может меняться по сезону или по решению администрации, предупреди об этом.
Отвечай естественно и дружелюбно.
"""
LANGUAGES = {
    "ru": "русском языке",
    "tr": "турецком языке",
    "en": "английском языке",
    "de": "немецком языке",
    "fr": "французском языке",
    "es": "испанском языке",
    "it": "итальянском языке",
    "ar": "арабском языке",
    "uk": "украинском языке",
    "pl": "польском языке"
}
def ask_openai(message, language):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise Exception(
            "OPENAI_API_KEY не найден в Vercel."
        )
    language_name = LANGUAGES.get(
        language,
        LANGUAGES["ru"]
    )
    instructions = f"""
Ты — Зея, AI-консьерж Selectum Noa Belek.
Пользователь выбрал {language_name}.
ОБЯЗАТЕЛЬНО:
Отвечай на выбранном языке.
Если выбран турецкий:
- отвечай естественным современным турецким;
- используй нормальную турецкую грамматику;
- не переходи на английский или русский без необходимости.
Если выбран русский — отвечай по-русски.
Если выбран английский — отвечай по-английски.
{HOTEL_KNOWLEDGE}
Пользовательский вопрос:
{message}
Ответь непосредственно на вопрос пользователя.
Не спрашивай название отеля.
"""
    data = {
        "model": MODEL,
        "instructions": instructions,
        "input": message
    }
    request = urllib.request.Request(
        OPENAI_URL,
        data=json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8"),
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
    for item in result.get(
        "output",
        []
    ):
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
    return "Не удалось получить ответ от ИИ."
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
                "message": "Зея Selectum Noa Belek работает"
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
            language = str(
                data.get(
                    "language",
                    "ru"
                )
            ).lower()
            if not message:
                self.send_json(
                    400,
                    {
                        "error": "Сообщение пустое"
                    }
                )
                return
            reply = ask_openai(
                message,
                language
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
