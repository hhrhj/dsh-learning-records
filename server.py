# -*- coding: utf-8 -*-
"""
我的 DSH 学习记录的本地服务器
只用 Python 自带的库，不需要 pip install 任何东西。

启动方式：双击同目录的「启动学习记录页.bat」
或者命令行：python server.py
"""

import json
import os
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

# 本文件所在的文件夹
BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "records.json")
PORT = 8765

_lock = threading.Lock()


def read_records():
    """读数据文件；文件不存在或损坏就返回空列表"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            recs = data.get("records", [])
        else:
            recs = data
        return recs if isinstance(recs, list) else []
    except Exception as e:
        print("读取数据文件失败：", e)
        return []


def write_records(records):
    """先写临时文件再替换，避免写到一半断电把数据弄坏"""
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(
            {"_version": 1, "records": records},
            f,
            ensure_ascii=False,
            indent=2,
        )
    os.replace(tmp, DATA_FILE)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE, **kwargs)

    def log_message(self, fmt, *args):
        # 只打印重要信息，不刷新一堆访问日志
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = self.path.split("?")[0]
        if route == "/api/records":
            with _lock:
                recs = read_records()
            return self._json({"ok": True, "records": recs})
        return super().do_GET()

    def do_POST(self):
        route = self.path.split("?")[0]
        if route != "/api/records":
            return self._json({"ok": False, "error": "接口不存在"}, 404)

        try:
            length = int(self.headers.get("Content-Length", "0") or 0)
            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8"))
        except Exception as e:
            return self._json({"ok": False, "error": "数据格式不对：" + str(e)}, 400)

        recs = data.get("records") if isinstance(data, dict) else data
        if not isinstance(recs, list):
            return self._json({"ok": False, "error": "缺少 records 列表"}, 400)

        try:
            with _lock:
                write_records(recs)
        except Exception as e:
            return self._json({"ok": False, "error": "保存失败：" + str(e)}, 500)

        return self._json({"ok": True, "count": len(recs)})


def main():
    print("=" * 46)
    print("  我的 DSH 学习记录 —— 本地服务器")
    print("=" * 46)
    print("数据文件：" + DATA_FILE)
    print("打开网址： http://127.0.0.1:%d/" % PORT)
    print("")
    print("这个黑窗口不能关。关掉 = 服务器停止。")
    print("要停止就按 Ctrl + C，或者直接关窗口。")
    print("=" * 46)

    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")


if __name__ == "__main__":
    main()
