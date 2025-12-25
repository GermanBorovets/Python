'''
Ну в целом тут тоже все просто, не стал как-то сильно тут импровизировать. 
Команды для запуска: python server.py
Можно создать задачу через запрос к серваку, например:
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/tasks" `
  -ContentType "application/json" `
  -Body '{"title":"Gym","priority":"low"}'
  
Можно получить список задач:
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/tasks"

Можно выполнить задачу:
Invoke-WebRequest -Method Post -Uri "http://127.0.0.1:8000/tasks/1/complete"

Если выполнить задачу, которой нет, то отправит 404, кастомный вывод ошибки не делал
'''


from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from urllib.parse import urlparse

TASKS_FILE = "tasks.txt"

tasks = []
next_id = 1  


def load_tasks():
    global tasks, next_id
    if not os.path.exists(TASKS_FILE):
        tasks = []
        next_id = 1
        return

    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                tasks = []
                next_id = 1
                return
            tasks = json.loads(content)

        max_id = 0
        for t in tasks:
            if isinstance(t, dict) and "id" in t and isinstance(t["id"], int):
                max_id = max(max_id, t["id"])
        next_id = max_id + 1

    except Exception:
        tasks = []
        next_id = 1


def save_tasks():
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False)


class TaskHandler(BaseHTTPRequestHandler):
    def _send_json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_empty(self, code):
        self.send_response(code)
        self.end_headers()

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b""
        if not raw:
            return None
        return json.loads(raw.decode("utf-8"))

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/tasks":
            self._send_json(200, tasks)
            return

        self._send_empty(404)

    def do_POST(self):
        global next_id, tasks
        path = urlparse(self.path).path

        if path == "/tasks":
            try:
                data = self._read_json_body()
                if not isinstance(data, dict):
                    self._send_empty(400)
                    return

                title = data.get("title")
                priority = data.get("priority")

                if not isinstance(title, str) or not title.strip():
                    self._send_empty(400)
                    return
                if priority not in ("low", "normal", "high"):
                    self._send_empty(400)
                    return

                task = {
                    "title": title,
                    "priority": priority,
                    "isDone": False,
                    "id": next_id
                }
                next_id += 1
                tasks.append(task)
                save_tasks()
                self._send_json(200, task)
                return

            except Exception:
                self._send_empty(400)
                return

        parts = path.strip("/").split("/")
        if len(parts) == 3 and parts[0] == "tasks" and parts[2] == "complete":
            try:
                task_id = int(parts[1])
            except ValueError:
                self._send_empty(404)
                return

            for t in tasks:
                if t.get("id") == task_id:
                    t["isDone"] = True
                    save_tasks()
                    self._send_empty(200)
                    return

            self._send_empty(404)
            return

        self._send_empty(404)

    def log_message(self, format, *args):
        return


def run(host="127.0.0.1", port=8000):
    load_tasks()
    server = HTTPServer((host, port), TaskHandler)
    print(f"Server started: http://{host}:{port}")
    print("Endpoints:")
    print("  POST /tasks")
    print("  GET  /tasks")
    print("  POST /tasks/<id>/complete")
    server.serve_forever()


if __name__ == "__main__":
    run()
