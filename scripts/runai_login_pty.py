import os
import pty
import re
import select
import sys
import time

RUNAI = "/home/jovyan/work/causal-mind-v2/.runai-cli/bin/runai"
LOG = "/tmp/runai-login.log"
URL_FILE = "/tmp/runai-login-url.txt"
CODE_FILE = "/tmp/runai-code.txt"
TIMEOUT_S = 3600

pid, fd = pty.fork()
if pid == 0:
    os.execv(RUNAI, [RUNAI, "login", "remote-browser"])

with open(LOG, "wb") as log:
    buf = b""
    url_saved = False
    code_sent = False
    deadline = time.time() + TIMEOUT_S
    while time.time() < deadline:
        r, _, _ = select.select([fd], [], [], 5)
        if r:
            try:
                data = os.read(fd, 65536)
            except OSError:
                break
            if not data:
                break
            buf += data
            log.write(data)
            log.flush()
        if not url_saved:
            m = re.search(rb"https://\S+", buf)
            if m:
                with open(URL_FILE, "wb") as u:
                    u.write(m.group(0) + b"\n")
                url_saved = True
        if url_saved and not code_sent and os.path.exists(CODE_FILE):
            with open(CODE_FILE, "rb") as c:
                code = c.read().strip()
            if code:
                os.write(fd, code + b"\n")
                code_sent = True
                os.unlink(CODE_FILE)
        try:
            wpid, status = os.waitpid(pid, os.WNOHANG)
        except ChildProcessError:
            break
        if wpid == pid:
            break
