import os

def ping_space():
    # 访问具体的 Space 页面，确保空间保持活跃
    url = "https://huggingface.co/spaces/ka1q/shang"
    exit_code = os.system(f"curl -s -o /dev/null -w '%{{http_code}}' {url}")
    if exit_code == 0:
        print("Access successful, space should stay alive!")
    else:
        print("Access failed, space may be unreachable.")

if __name__ == "__main__":
    ping_space()
