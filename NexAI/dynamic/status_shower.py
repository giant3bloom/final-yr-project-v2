"""Live status dashboard — runs as a child process during optimization."""
from __future__ import annotations

import json
import queue
import socket
import socketserver
import threading
import tkinter as tk
from datetime import datetime
from tkinter import ttk

from NexAI.dynamic.ssm import get_ssm


class _StatusHandler(socketserver.StreamRequestHandler):
    server: "_StatusServer"

    def handle(self) -> None:
        raw = self.rfile.readline()
        if not raw:
            return
        try:
            message = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            message = {"text": raw.decode("utf-8", errors="replace"), "status": True}
        self.server.event_queue.put(message)


class _StatusServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def __init__(self, host: str, port: int, event_queue: queue.Queue):
        self.event_queue = event_queue
        super().__init__((host, port), _StatusHandler)


class StatusShowerApp:
    def __init__(self, ssm: dict):
        self.ssm = ssm
        self.event_queue: queue.Queue = queue.Queue()
        self.history_limit = ssm["state"]["history_limit"]
        self.appearance = ssm["appearance"]

        host = ssm["dynamics"]["host"]
        port = ssm["dynamics"]["port"]

        self.server = _StatusServer(host, port, self.event_queue)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()

        self.root = tk.Tk()
        self.root.title(self.appearance["title"])
        self.root.geometry(
            f"{ssm['geometry']['width']}x{ssm['geometry']['height']}"
        )
        self.root.configure(bg="#1e1e1e")
        self.root.protocol("WM_DELETE_WINDOW", self.shutdown)

        self._build_ui()
        self.root.after(100, self._poll_events)

    def _build_ui(self) -> None:
        font = (self.appearance["font_family"], self.appearance["font_size"])

        header = tk.Label(
            self.root,
            text=self.appearance["title"],
            bg="#1e1e1e",
            fg="#ecf0f1",
            font=(self.appearance["font_family"], 14, "bold"),
        )
        header.pack(fill="x", padx=12, pady=(12, 4))

        self.phase_var = tk.StringVar(value="Phase: idle")
        tk.Label(
            self.root,
            textvariable=self.phase_var,
            bg="#1e1e1e",
            fg="#bdc3c7",
            font=font,
            anchor="w",
        ).pack(fill="x", padx=12, pady=2)

        self.score_var = tk.StringVar(value="Score: —")
        tk.Label(
            self.root,
            textvariable=self.score_var,
            bg="#1e1e1e",
            fg="#3498db",
            font=(self.appearance["font_family"], 12, "bold"),
            anchor="w",
        ).pack(fill="x", padx=12, pady=(2, 8))

        self.error_var = tk.StringVar(value="")
        tk.Label(
            self.root,
            textvariable=self.error_var,
            bg="#1e1e1e",
            fg=self.appearance["failure_color"],
            font=font,
            anchor="w",
            wraplength=self.ssm["geometry"]["width"] - 24,
            justify="left",
        ).pack(fill="x", padx=12, pady=(0, 8))

        frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        self.log_box = tk.Text(
            frame,
            bg="#2b2b2b",
            fg="#ecf0f1",
            insertbackground="#ecf0f1",
            font=font,
            wrap="word",
            yscrollcommand=scrollbar.set,
            state="disabled",
        )
        self.log_box.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.log_box.yview)

        self.log_box.tag_config("ok", foreground=self.appearance["success_color"])
        self.log_box.tag_config("fail", foreground=self.appearance["failure_color"])
        self.log_box.tag_config("idle", foreground=self.appearance["idle_color"])

    def _format_score(self, score) -> str:
        if score is None:
            return "—"
        return str(score)

    def _append_log(self, text: str, status: bool | None, ts: str) -> None:
        tag = "ok" if status else "fail" if status is False else "idle"
        icon = "✓" if status else "✗" if status is False else "·"
        line = f"[{ts}] {icon} {text}\n"

        self.log_box.configure(state="normal")
        self.log_box.insert("end", line, tag)
        self.log_box.see("end")

        line_count = int(self.log_box.index("end-1c").split(".")[0])
        if line_count > self.history_limit:
            self.log_box.delete("1.0", f"{line_count - self.history_limit}.0")

        self.log_box.configure(state="disabled")

    def _poll_events(self) -> None:
        while True:
            try:
                message = self.event_queue.get_nowait()
            except queue.Empty:
                break
            self._apply_message(message)

        self.root.after(100, self._poll_events)

    def _apply_message(self, message: dict) -> None:
        text = message.get("text", "")
        status = message.get("status")
        phase = message.get("phase")
        score = message.get("score", message.get("code score"))
        error = message.get("error")
        ts = datetime.now().strftime("%H:%M:%S")

        if phase:
            self.phase_var.set(f"Phase: {phase}")
            self.ssm["state"]["phase"] = phase

        if "score" in message or "code score" in message:
            self.ssm["state"]["score"] = score
            self.score_var.set(f"Score: {self._format_score(score)}")

        if error:
            self.ssm["state"]["last_error"] = error
            preview = error if len(error) <= 120 else error[:117] + "..."
            self.error_var.set(f"Error: {preview}")
        elif message.get("clear_error"):
            self.ssm["state"]["last_error"] = None
            self.error_var.set("")

        self.ssm["state"]["current_step"] = text
        self._append_log(text, status, ts)

    def shutdown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    from NexAI.runtime.bootstrap import bootstrap

    bootstrap()
    ssm = get_ssm("nexai_status_shower")
    app = StatusShowerApp(ssm)
    app.run()


if __name__ == "__main__":
    main()
