import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL = "gpt-5.6-luna"

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/ask":
            self.send_json({"error": "Not found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length).decode())
        question = data.get("text", "").strip()
        if question.lower() in ["hello", "hi", "hey", "hello jarvis", "hi jarvis", "hey jarvis"]:
            self.send_json({"reply": "Hello Sir. I am JARVIS. Faheem Sir created me. How can I help you today?"})
            return

        if not API_KEY:
            self.send_json({"reply": "Server configuration error."})
            return

        payload = {
            "model": MODEL,
            "input": [
                {
                    "role": "system",
                    "content": "You are JARVIS, a helpful AI assistant. Answer naturally and clearly. Understand Hindi, Hinglish and English. Call the user Sir."
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        }

        req = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + API_KEY
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                result = json.loads(r.read().decode())

            reply = ""
            for item in result.get("output", []):
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        reply = content.get("text", "").strip()
                        break

            self.send_json({"reply": reply or "Sorry Sir, answer nahi mila."})

        except Exception as e:
            print("ERROR:", e)
            self.send_json({"reply": "Sir, AI connection problem hai."})

    def send_json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

print("JARVIS BACKEND READY")

HTTPServer(("0.0.0.0", 8090), Handler).serve_forever()
