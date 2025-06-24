import os, subprocess, shutil, requests, time, sys, re, psutil, concurrent.futures, threading

processes = []
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
kuwa_root = os.getenv("KUWA_ROOT", os.path.join(base_dir, "kuwa_root"))
os.makedirs(os.path.join(base_dir, "logs"), exist_ok=True)
log_path = os.path.join(base_dir, "logs", "start.log")
def wait_and_remove(path, retry_interval=0.5, timeout=60):
    start_time = time.time()
    while os.path.exists(path):
        try:
            os.remove(path)
            print(f"Removed: {path}")
            return
        except PermissionError:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Timed out waiting to delete: {path}")
            time.sleep(retry_interval)
wait_and_remove(log_path)

log_lock = threading.Lock()

class Logger:
    def __init__(self, stream, path):
        self.stream, self.path = stream, path
        self.lock = threading.Lock()
    def write(self, msg):
        self.stream.write(msg); self.stream.flush()
        with self.lock:
            with open(self.path, 'a', encoding='utf-8') as f:
                f.write(msg); f.flush()
    def flush(self): self.stream.flush()

sys.stdout = Logger(sys.stdout, log_path)
sys.stderr = Logger(sys.stderr, log_path)

def logged_input(prompt=""):
    if prompt: print(prompt, end='', flush=True)
    line = sys.__stdin__.readline()
    if line == '': raise EOFError
    print(line.rstrip('\n'))
    return line.rstrip('\n')
input = logged_input

def run_background(cmd, cwd=None):
    print(f"Starting: {cmd}")
    env = os.environ.copy()

    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        env=env, encoding="utf-8"
    )

    processes.append(proc)

    def log_output():
        with open(log_path, 'a', encoding='utf-8') as f:
            try:
                for line in proc.stdout:
                    print(line, end='')
                    f.write(line)
            except Exception:
                "Skipped"

    threading.Thread(target=log_output, daemon=True).start()
    return proc

def terminate_proc(proc, current_pid):
    try:
        if proc.info['pid'] == current_pid: return
        if proc.info.get('exe', '').startswith(os.path.abspath(os.path.join(base_dir, '..'))):
            print(f"Terminating process {proc.pid}: {proc.info['exe']}")
            proc.terminate()
            try: proc.wait(timeout=2)
            except psutil.TimeoutExpired:
                print(f"Force killing {proc.pid}")
                proc.kill()
    except (psutil.NoSuchProcess, psutil.AccessDenied): pass

def hard_exit(restart):
    services = [
        ("Redis", "redis-cli.exe shutdown", os.path.join(base_dir, "packages", os.environ.get("redis_folder") or "redis")),
        ("Laravel worker", "php artisan worker:stop", os.path.abspath("../src/multi-chat"))
    ]

    http_server_runtime = os.environ.get("HTTP_Server_Runtime", "nginx")
    if (http_server_runtime == "nginx"):
        services = [("Nginx", r'.\nginx.exe -s quit', os.path.join(base_dir, "packages", os.environ.get("nginx_folder") or "nginx"))] + services

    for name, cmd, cwd in services:
        try:
            subprocess.call(cmd, cwd=cwd, shell=True)
            print(f"{name} shutdown issued.")
        except Exception as e:
            print(f"Failed to stop {name}: {e}")
            
    current_pid = os.getpid()
    current_proc = None
    futures = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for p in psutil.process_iter(['pid', 'exe']):
            if p.pid == current_pid:
                current_proc = p
            else:
                futures.append(executor.submit(terminate_proc, p, current_pid))
        concurrent.futures.wait(futures)

    if restart:
        subprocess.Popen(["start.bat"], shell=True, encoding="utf-8")

    if current_proc:
        print(f"Terminating current Python process (PID {current_pid}) last.")
        current_proc.terminate()
    os._exit(0)

def extract_packages():
    zip_path = os.path.abspath("../scripts/windows-setup-files/package.zip")
    multi_chat = os.path.abspath("../src/multi-chat")
    env_file = os.path.join(multi_chat, ".env")
    
    if not os.path.exists(env_file):
        shutil.copyfile(os.path.join(multi_chat, ".env.dev"), env_file)
    
    shutil.rmtree(os.path.join(multi_chat, "storage\framework\cache"), ignore_errors=True)
    if os.path.exists(zip_path):
        for f in ["bin", "database", "custom", "bootstrap/bot"]:
            os.makedirs(os.path.join(kuwa_root, f), exist_ok=True)
        shutil.copytree("../src/bot/init", os.path.join(kuwa_root, "bootstrap/bot"), dirs_exist_ok=True)
        shutil.copytree("../src/tools", os.path.join(kuwa_root, "bin"), dirs_exist_ok=True)
        shutil.rmtree(os.path.join(kuwa_root, "bin", "test"), ignore_errors=True)
        print("Filesystem initialized.")
        for cmd in [
            "php artisan key:generate --force",
            "php artisan db:seed --class=InitSeeder --force",
            "php artisan migrate --force",
            "php artisan storage:link",
            "php ../../windows/packages/composer.phar dump-autoload --optimize",
            "php artisan route:cache",
            "php artisan view:cache",
            "php artisan optimize",
            "npm.cmd run build",
            "php artisan config:cache",
            "php artisan config:clear"]:
            subprocess.call(cmd, cwd=multi_chat, shell=True)
        os.remove(zip_path)
    if os.path.exists(os.path.abspath("init.txt")):
        with open("init.txt") as f:
            env = dict(line.strip().split("=", 1) for line in f if "=" in line)

        username = env.get("username", "")
        name = username.split("@")[0]
        password = env.get("password", "")
        autologin = env.get("autologin", "").lower() == "true"

        subprocess.call(f"php artisan create:admin-user --name={name} --email={username} --password={password}", cwd=multi_chat, shell=True)

        if autologin:
            with open(env_file, encoding="utf-8") as f:
                content = f.read()
            content = re.sub(
                r'^APP_AUTO_EMAIL=.*$', '', content, flags=re.MULTILINE
            ).strip()
            content += f"\nAPP_AUTO_EMAIL={username}\n"
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(content)
            for cmd in [
                "php artisan config:clear",
                "php artisan cache:clear",
                "php artisan config:cache",]:
                subprocess.call(cmd, cwd=multi_chat, shell=True)
        os.remove(os.path.abspath("init.txt"))
    if not os.path.exists("packages\composer.bat"):
        with open("packages\composer.bat", 'w') as f:
            f.write('php "%~dp0composer.phar" %*\n')

def extract_executor_access_code(path):
    with open(path) as f:
        for line in f:
            if line.lower().startswith('set '):
                m = re.match(r'set\s+EXECUTOR_ACCESS_CODE\s*=\s*(.*)', line, re.I)
                if m: return m.group(1).strip()
    return None

def start_servers():
    redis_path = os.path.join(base_dir, "packages", os.environ.get("redis_folder", "redis"))
    rdb = os.path.join(redis_path, "dump.rdb")
    if os.path.exists(rdb): os.remove(rdb)
    run_background("redis-server.exe redis.conf", cwd=redis_path)

    web_path = os.path.abspath("../src/multi-chat")
    subprocess.call('php artisan web:config --settings="updateweb_path=%PATH%"', cwd=web_path, shell=True)
    run_background("php artisan worker:start 10", cwd=web_path)

    kernel_path = os.path.abspath("../src/kernel")
    try: os.remove(os.path.join(kernel_path, "records.pickle"))
    except FileNotFoundError: pass
    run_background("kuwa-kernel", cwd=kernel_path)

    while True:
        try: requests.get("http://127.0.0.1:9000", timeout=1); break
        except: time.sleep(1)

    exclude_args = []
    executors_dir = os.path.join(base_dir, "executors")
    folder_paths = [
        os.path.join(executors_dir, folder)
        for folder in os.listdir(executors_dir)
        if os.path.isdir(os.path.join(executors_dir, folder))
    ]

    def process_folder(folder_path):
        run_bat = os.path.join(folder_path, "run.bat")
        init_bat = os.path.join(folder_path, "init.bat")
        try:
            if os.path.exists(init_bat) and not os.path.exists(run_bat):
                subprocess.call("init.bat quick", cwd=folder_path, shell=True)
            if os.path.exists(run_bat):
                subprocess.call("run.bat", cwd=folder_path, shell=True)
                code = extract_executor_access_code(run_bat)
                if code:
                    return f"--exclude={code}"
        except Exception as e:
            print(f"Error processing {folder_path}: {e}")
        return None

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_folder, path) for path in folder_paths]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                exclude_args.append(result)

    if exclude_args:
        subprocess.call(
            f"php artisan model:prune --force {' '.join(exclude_args)}",
            cwd=web_path,
            shell=True
        )
    http_server_runtime = os.environ.get("HTTP_Server_Runtime", "nginx")
    if (http_server_runtime == "apache"):
        apache_folder = os.path.join("Apache_" + os.environ.get("apache_folder", "apache"), "Apache24")
        apache_htdocs = os.path.join(base_dir, "packages", apache_folder, "htdocs")
        if os.path.exists(apache_htdocs):
            try: os.unlink(apache_htdocs)
            except OSError: shutil.rmtree(apache_htdocs, ignore_errors=True)
        subprocess.run(f'mklink /j "{apache_htdocs}" "{os.path.abspath("../src/multi-chat/public")}"', shell=True, check=True)
        
        fcgid_path = os.path.join(base_dir, "packages", apache_folder, "conf", 'extra', 'httpd-fcgid.conf')
        with open(fcgid_path, encoding='utf-8') as f:
            t = f.read()
        with open(fcgid_path, 'w', encoding='utf-8') as f:
            f.write(re.sub(r'(FcgidWrapper\s+")([^"]*)("\s+\.php)', lambda m: m.group(1) + os.path.join(base_dir, "packages", os.environ.get("php_folder", "php"), 'php-cgi.exe').replace("\\","/") + m.group(3), t))
    
        run_background("httpd.exe", cwd=os.path.join(base_dir, "packages", apache_folder, "bin"))
        print("Apache started!")
    elif (http_server_runtime == "nginx"):
        php_path = os.path.join(base_dir, "packages", os.environ.get("php_folder", "php"))
        for port in range(9101, 9111):
            run_background(f"php-cgi.exe -b 127.0.0.1:{port}", cwd=php_path)
        run_background(f"php-cgi.exe -b 127.0.0.1:9123", cwd=php_path)
        nginx_folder = os.environ.get("nginx_folder", "nginx")
        nginx_html = os.path.join(base_dir, "packages", nginx_folder, "html")
        if os.path.exists(nginx_html):
            try: os.unlink(nginx_html)
            except OSError: shutil.rmtree(nginx_html, ignore_errors=True)
        subprocess.run(f'mklink /j "{nginx_html}" "{os.path.abspath("../src/multi-chat/public")}"', shell=True, check=True)

        run_background("nginx.exe", cwd=os.path.join(base_dir, "packages", nginx_folder))
        print("Nginx started!")

    subprocess.call("php artisan model:reset-health", cwd=web_path, shell=True)
    time.sleep(4)
    subprocess.call("src\\import_bots.bat", shell=True)
    time.sleep(1)

    print("System initialized. Press Ctrl+C or type 'stop' to exit.")
    subprocess.call('start http://127.0.0.1', shell=True)

def command_loop():
    while True:
        try:
            cmd = input("Enter a command (stop, seed, hf login, reload): ").strip().lower()
            if cmd == "stop": hard_exit(False)
            elif cmd == "seed":
                print("Running seed command...")
                seed_path = os.path.abspath("../src/multi-chat/executables/bat")
                subprocess.call("AdminSeeder.bat", cwd=seed_path, shell=True)
            elif cmd == "hf login":
                print("Running HuggingFace login...")
                subprocess.call("huggingface-cli.exe login", shell=True)
            elif cmd == "reload":
                print("Restarting script...")
                hard_exit(True)
            else:
                print("Unknown command.")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            hard_exit(False)

if __name__ == "__main__":
    extract_packages()
    start_servers()
    command_loop()
