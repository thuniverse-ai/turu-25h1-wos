import os, subprocess, time, psutil, concurrent.futures

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
def terminate_proc(proc, current_pid):
    try:
        if proc.info['pid'] == current_pid: return
        if proc.info.get('exe', '').startswith(os.path.abspath(os.path.join(base_dir, '..'))):
            print(f"Terminating process {proc.pid}: {proc.info['exe']}")
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except psutil.TimeoutExpired:
                print(f"Force killing {proc.pid}")
                proc.kill()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

def hard_exit():
    services = [
        ("Redis", "redis-cli.exe shutdown", os.path.join(base_dir, "packages", os.environ.get("redis_folder", "redis"))),
        ("Laravel worker", "php artisan worker:stop", os.path.abspath("../../src/multi-chat"))
    ]

    http_server_runtime = os.environ.get("HTTP_Server_Runtime", "nginx")
    if http_server_runtime == "nginx":
        services.insert(0, ("Nginx", r'.\nginx.exe -s quit', os.path.join(base_dir, "packages", os.environ.get("nginx_folder", "nginx"))))

    for name, cmd, cwd in services:
        try:
            subprocess.call(cmd, cwd=cwd, shell=True)
            print(f"{name} shutdown issued.")
        except Exception as e:
            print(f"Failed to stop {name}: {e}")

    current_pid = os.getpid()
    current_proc = None
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(terminate_proc, p, current_pid) for p in psutil.process_iter(['pid','exe']) if p.pid != current_pid or (current_proc:=p)]
        concurrent.futures.wait(futures)

    time.sleep(5)
    if current_proc:
        print(f"Terminating current Python process (PID {current_pid}) last.")
        current_proc.terminate()
    os._exit(0)

if __name__ == "__main__":
    hard_exit()
