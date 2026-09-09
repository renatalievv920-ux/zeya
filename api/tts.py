import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler


OPENAI_URL = "https://api.openai.com/v1/audio/speech"


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
                "message": "Zeya TTS работает"
            }
        )

    def do_POST(self):
        try:
            api_key = os.environ.get("OPENAI_API_KEY")

            if not api_key:
                raise Exception(
                    "OPENAI_API_KEY не найден в Vercel."
                )

            content_length = int(
                self.headers.get("Content-Length", "0")
            )

            body = self.rfile.read(content_length)

            data = json.loads(
                body.decode("utf-8")
            )

            text = str(
                data.get("text", "")
            ).strip()

            language = str(
                data.get("language", "ru")
            ).lower()

            if not text:
                self.send_json(
                    400,
                    {
                        "error": "Текст пустой"
                    }
                )
                return

            language_instructions = {
                "ru": (
                    "Говори естественно на русском языке. "
                    "Чёткое произношение, спокойный женский голос."
                ),
                "tr": (
                    "Türkçe konuş. "
                    "Türkçe kelimeleri doğal ve doğru telaffuz et. "
                    "Konuşman akıcı, sıcak ve profesyonel olsun. "
                    "İstanbul Türkçesine yakın doğal bir telaffuz kullan."
                ),
                "en": (
                    "Speak naturally in English. "
                    "Use clear pronunciation and a warm professional voice."
                ),
                "de": (
                    "Sprich natürlich auf Deutsch. "
                    "Klare Aussprache und eine warme professionelle Stimme."
                ),
                "fr": (
                    "Parle naturellement en français. "
                    "Utilise une prononciation claire et une voix chaleureuse."
                ),
                "es": (
                    "Habla naturalmente en español. "
                    "Usa una pronunciación clara y una voz cálida."
                ),
                "it": (
                    "Parla naturalmente in italiano. "
                    "Usa una pronuncia chiara e una voce calda."
                ),
                "ar": (
                    "تحدث باللغة العربية بشكل طبيعي "
                    "وبنطق واضح وصوت دافئ."
                ),
                "uk": (
                    "Говори природно українською мовою. "
                    "Чітка вимова та теплий професійний голос."
                ),
                "pl": (
                    "Mów naturalnie po polsku. "
                    "Używaj wyraźnej wymowy i ciepłego głosu."
                )
            }

            instructions = language_instructions.get(
                language,
                language_instructions["ru"]
            )

            request_data = {
                "model": "gpt-4o-mini-tts",
                "voice": "marin",
                "input": text,
                "instructions": instructions,
                "response_format": "mp3",
                "speed": 1.0
            }

            request = urllib.request.Request(
                OPENAI_URL,
                data=json.dumps(
                    request_data
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

                    audio = response.read()

            except urllib.error.HTTPError as e:

                error_text = e.read().decode(
                    "utf-8",
                    errors="ignore"
                )

                raise Exception(
                    "OpenAI TTS error: " + error_text
                )

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "audio/mpeg"
            )

            self.send_header(
                "Content-Length",
                str(len(audio))
            )

            self.send_header(
                "Access-Control-Allow-Origin",
                "*"
            )

            self.send_header(
                "Cache-Control",
                "no-cache"
            )

            self.end_headers()

            self.wfile.write(audio)

        except Exception as e:

            self.send_json(
                500,
                {
                    "error": str(e)
                }
            )
