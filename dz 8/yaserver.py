#!/usr/bin/env python3
# ya.py
import os
import time
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests

YADISK_API = "https://cloud-api.yandex.net/v1/disk"


def get_ext_from_url(url: str) -> str:
    """
    Достаём расширение из пути URL (последняя часть после точки).
    Если не получается — вернём 'bin'.
    """
    try:
        path = urllib.parse.urlparse(url).path
    except Exception:
        return "bin"

    filename = path.rsplit("/", 1)[-1]
    if "." in filename and not filename.endswith("."):
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext and all(ch.isalnum() for ch in ext) and len(ext) <= 10:
            return ext
    return "bin"


def get_filename_from_url(url: str) -> str | None:
    """
    Достаём имя файла из URL (последний сегмент пути).
    Возвращаем None, если сегмента нет или он пустой.
    """
    try:
        path = urllib.parse.urlparse(url).path
    except Exception:
        return None

    name = path.rsplit("/", 1)[-1].strip()
    if not name or name.endswith("/"):
        return None
    return name


def upload_by_url(token: str, file_url: str, disk_path: str):
    """
    Запуск загрузки по URL на Яндекс.Диск.
    Возвращает (status_code, text_response).
    """
    endpoint = f"{YADISK_API}/resources/upload"
    headers = {"Authorization": f"OAuth {token}"}
    params = {"url": file_url, "path": disk_path}

    resp = requests.post(endpoint, headers=headers, params=params, timeout=20)
    return resp.status_code, resp.text


def list_uploaded_names(token: str, folder_path: str = "/Uploads", limit: int = 200) -> set[str]:
    """
    Получаем список файлов в папке на Диске (одним API-запросом)
    и возвращаем множество имён (name) элементов.
    """
    endpoint = f"{YADISK_API}/resources"
    headers = {"Authorization": f"OAuth {token}"}
    params = {"path": folder_path, "limit": str(limit)}

    resp = requests.get(endpoint, headers=headers, params=params, timeout=20)
    if resp.status_code != 200:
        # Если папки нет или токен неверный — просто считаем, что ничего не загружено.
        return set()

    data = resp.json()
    items = (data.get("_embedded") or {}).get("items") or []
    names = set()
    for it in items:
        n = it.get("name")
        if isinstance(n, str) and n:
            names.add(n)
    return names


class Handler(BaseHTTPRequestHandler):
    # Список "кандидатов", которые будут показаны на странице
    # (можете заменить на любые свои)
    CANDIDATE_URLS = [
        "https://speed.hetzner.de/100MB.bin",
        "https://speed.hetzner.de/10MB.bin",
        "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "https://upload.wikimedia.org/wikipedia/commons/3/3f/Fronalpstock_big.jpg",
    ]

    def _send(self, status: int, body: str, content_type: str = "text/plain; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path != "/":
            self._send(404, "not found")
            return

        token = os.environ.get("YADISK_TOKEN", "").strip()

        uploaded_names: set[str] = set()
        if token:
            uploaded_names = list_uploaded_names(token, "/Uploads")

        # Строим список: если имя файла уже есть в uploaded_names -> подсвечиваем.
        lis = []
        for url in self.CANDIDATE_URLS:
            name = get_filename_from_url(url)
            if not name:
                # если нет имени, всё равно покажем, но сопоставление будет грубым
                ext = get_ext_from_url(url)
                name = f"(no-filename).{ext}"

            style = ""
            if name in uploaded_names:
                # ВАЖНОЕ требование задания:
                style = " style='background-color: rgba(0, 200, 0, 0.25);'"

            # data-url нужно, чтобы JS мог взять URL по клику
            lis.append(
                f"<li{style} data-url='{html_escape(url)}'>"
                f"<b>{html_escape(name)}</b><br>"
                f"<small>{html_escape(url)}</small>"
                f"</li>"
            )

        token_hint = ""
        if not token:
            token_hint = (
                "<p style='color:#b00'>"
                "Не задан <code>YADISK_TOKEN</code>. "
                "GET / покажет список, но подсветка и загрузка работать не будут."
                "</p>"
            )

        html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Yandex Disk uploader</title>
  <style>
    body {{ font-family: Arial, sans-serif; padding: 16px; }}
    ul {{ padding-left: 0; }}
    li {{
      list-style: none;
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 10px;
      margin: 8px 0;
      cursor: pointer;
    }}
    li:hover {{ border-color: #999; }}
    .hint {{ color: #555; }}
  </style>
</head>
<body>
  <h2>Загрузка на Яндекс.Диск по URL</h2>
  {token_hint}
  <p class="hint">Кликните по элементу списка, чтобы загрузить файл в <code>/Uploads</code>.</p>

  <ul id="list">
    {''.join(lis)}
  </ul>

  <script>
    const list = document.getElementById("list");
    list.addEventListener("click", async (e) => {{
      const li = e.target.closest("li");
      if (!li) return;

      const url = li.dataset.url;
      if (!url) return;

      try {{
        const resp = await fetch("/download", {{
          method: "POST",
          headers: {{ "Content-Type": "text/plain; charset=utf-8" }},
          body: url
        }});

        const text = await resp.text();
        alert(text);
        // после загрузки обновим страницу -> сервер заново спросит API и подсветит
        location.reload();
      }} catch (err) {{
        alert("Ошибка: " + err);
      }}
    }});
  </script>
</body>
</html>
"""
        self._send(200, html, "text/html; charset=utf-8")

    def do_POST(self):
        if self.path != "/download":
            self._send(404, "not found")
            return

        token = os.environ.get("YADISK_TOKEN", "").strip()
        if not token:
            self._send(500, "YADISK_TOKEN is not set")
            return

        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length)
        file_url = raw.decode("utf-8", errors="replace").strip()

        if not file_url:
            self._send(400, "empty url")
            return
        if not (file_url.startswith("http://") or file_url.startswith("https://")):
            self._send(400, "url must start with http:// or https://")
            return

        # Делаем понятный путь на диске: /Uploads/<filename>
        filename = get_filename_from_url(file_url)
        if filename:
            disk_path = f"/Uploads/{filename}"
        else:
            ext = get_ext_from_url(file_url)
            ts = int(time.time())
            disk_path = f"/Uploads/{ts}.{ext}"

        status, yadisk_resp_text = upload_by_url(token, file_url, disk_path)

        self._send(
            status,
            f"disk_path={disk_path}\nstatus={status}\nresponse={yadisk_resp_text}\n",
        )

    def log_message(self, fmt, *args):
        return


def html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&#39;")
    )


def main():
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8080"))
    httpd = HTTPServer((host, port), Handler)
    print(f"Open: http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
