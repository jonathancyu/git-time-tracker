import subprocess
import webbrowser
import time
import os


pwd = os.path.dirname(os.path.abspath(__file__))

def run_fastapi():
    os.chdir(os.path.join(pwd, 'python'))
    return subprocess.Popen(["uvicorn", "app.main:app", "--port 8000" "--reload"])

def run_angular():
    os.chdir(os.path.join(pwd, 'angular'))
    return subprocess.Popen(["ng", "serve"])

if __name__ == "__main__":
    fastapi_process = run_fastapi()
    angular_process = run_angular()

    webbrowser.open("http://localhost:4200")

    fastapi_process.wait()
    angular_process.wait()
