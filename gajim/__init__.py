import subprocess

__version__ = "0.99.2"

try:
    p = subprocess.Popen('git rev-parse --short=12 HEAD', shell=True,
                          stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    node = p.communicate()[0]
    if node:
        __version__ += '+' + node.decode('utf-8').strip()
except Exception:
    pass
