import customtkinter as ctk
import subprocess
import threading
import os
import sys
import json
import requests
import shlex
import logging
from tkinter import filedialog
from PIL import Image
from io import BytesIO

# ------------------- Logging Setup -------------------
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='debug.log',
                    filemode='w')
# ----------------------------------------------------


# ------------------- Configuration -------------------
APP_NAME = "OneStepUpdate (GH Edition)"
CONFIG_FILE = "gh_config.json"
# ----------------------------------------------------

def get_resource_path(relative_path):
    """Get path for resources."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_path, relative_path)
    logging.info(f"Resource path: {path}")
    return path

def get_config_path():
    """Get path for configuration file."""
    return os.path.join(os.path.expanduser("~"), ".onestepupdate_gh_config.json")

class LoginView(ctk.CTkFrame):
    def __init__(self, master, view_manager):
        super().__init__(master)
        self.view_manager = view_manager

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Cover Image
        try:
            cover_image_path = get_resource_path("onestepupdate.png")
            img = Image.open(cover_image_path)
            self.cover_image = ctk.CTkImage(light_image=img, dark_image=img, size=(400, 200))
            image_label = ctk.CTkLabel(self, image=self.cover_image, text="")
            image_label.grid(row=0, column=0, pady=(20, 10))
        except Exception as e:
            logging.error(f"Failed to load cover image: {e}")
            pass

        # Welcome Title
        title_label = ctk.CTkLabel(self, text="Welcome to OneStepUpdate", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=1, column=0, pady=(0, 20), sticky="n")

        # Login Button
        self.login_button = ctk.CTkButton(self, text="Login with GitHub", command=self.login, height=40, font=ctk.CTkFont(size=16))
        self.login_button.grid(row=2, column=0, padx=50, pady=(0, 50), sticky="ew")

    def login(self):
        self.login_button.configure(state="disabled", text="Logging in...")
        threading.Thread(target=self._login_thread, daemon=True).start()
    
    def _login_thread(self):
        self.view_manager.log("请在浏览器中完成授权...")
        code, out, err = self.view_manager.run_cmd(["gh", "auth", "login", "--web", "--hostname", "github.com", "-p", "https"], show_window=True)
        if code == 0:
            self.view_manager.log("授权成功！")
            self.view_manager.after(100, self.view_manager.check_login_status)
        else:
            self.view_manager.log("授权失败或被取消。")
            self.view_manager.log(err)
            self.view_manager.after(100, lambda: self.login_button.configure(state="normal", text="Login with GitHub"))
            self.view_manager.after(100, lambda: self.view_manager.show_view("LoginView"))


class MainView(ctk.CTkFrame):
    def __init__(self, master, view_manager):
        super().__init__(master, fg_color="transparent")
        self.view_manager = view_manager

        self.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Header Section ---
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        theme_btn_text = "☀️" if self.view_manager.current_theme == "light" else "🌙"
        self.theme_button = ctk.CTkButton(header_frame, text=theme_btn_text, width=30, command=self.view_manager.toggle_theme)
        self.theme_button.pack(side="left", padx=10, pady=5)
        
        user_info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        user_info_frame.pack(side="right", padx=10, pady=5)
        self.avatar_label = ctk.CTkLabel(user_info_frame, text="")
        self.username_label = ctk.CTkLabel(user_info_frame, text="Checking...")
        self.username_label.pack(side="right")
        self.avatar_label.pack(side="right", padx=(0, 5))

        # --- Form Section ---
        form_frame = ctk.CTkFrame(self)
        form_frame.grid(row=1, column=0, columnspan=3, sticky="new", padx=10)
        form_frame.grid_columnconfigure(1, weight=1)

        # 1. Repo
        ctk.CTkLabel(form_frame, text="GitHub 仓库:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.repo_menu = ctk.CTkOptionMenu(form_frame, values=["加载中..."])
        self.repo_menu.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        # 2. Local Path
        ctk.CTkLabel(form_frame, text="本地仓库路径:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.repo_path_entry = ctk.CTkEntry(form_frame, placeholder_text="例如: C:\\path\\to\\your\\repo")
        self.repo_path_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.browse_button = ctk.CTkButton(form_frame, text="浏览...", command=self.browse_directory, width=60)
        self.browse_button.grid(row=1, column=2, padx=(0, 10), pady=10)

        # 3. Files
        ctk.CTkLabel(form_frame, text="添加的文件:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.files_entry = ctk.CTkEntry(form_frame, placeholder_text="用空格分隔 (这些文件将作为 Release 附件上传)")
        self.files_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        self.file_browse_button = ctk.CTkButton(form_frame, text="选择...", command=self.browse_files, width=60)
        self.file_browse_button.grid(row=2, column=2, padx=(0, 10), pady=10)

        # 4. Commit Msg (Kept for UI consistency, used as fallback release title or note)
        ctk.CTkLabel(form_frame, text="提交/分支:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.commit_entry = ctk.CTkEntry(form_frame, placeholder_text="main (目标分支)")
        self.commit_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        self.commit_entry.insert(0, "main")

        # 5. Tag
        ctk.CTkLabel(form_frame, text="标签名称 (Tag):").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.tag_entry = ctk.CTkEntry(form_frame)
        self.tag_entry.grid(row=4, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        self.tag_entry.insert(0, "v1.0.0")

        # 6. Title
        ctk.CTkLabel(form_frame, text="Release 标题:").grid(row=5, column=0, padx=10, pady=10, sticky="w")
        self.release_title_entry = ctk.CTkEntry(form_frame)
        self.release_title_entry.grid(row=5, column=1, columnspan=2, padx=10, pady=10, sticky="ew")
        self.release_title_entry.insert(0, "v1.0.0")

        # 7. Notes
        ctk.CTkLabel(form_frame, text="Release 描述:").grid(row=6, column=0, padx=10, pady=10, sticky="w")
        self.release_notes_entry = ctk.CTkTextbox(form_frame, height=60)
        self.release_notes_entry.grid(row=6, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        # 8. Button
        self.execute_button = ctk.CTkButton(form_frame, text="开始上传", command=self.on_create_click, height=40)
        self.execute_button.grid(row=7, column=0, columnspan=3, padx=10, pady=20, sticky="ew")

        # --- Log Section ---
        self.log_box = ctk.CTkTextbox(self, wrap="word")
        self.log_box.grid(row=2, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="nsew")
        self.log_box.configure(state="disabled")
        
        self.update_widget_colors()
    
    def update_widget_colors(self):
        button_color = "black" if self.view_manager.current_theme == "light" else "white"
        button_text_color = "white" if self.view_manager.current_theme == "light" else "black"
        hover_color = "#333333" if self.view_manager.current_theme == "light" else "#CCCCCC"

        self.theme_button.configure(fg_color=button_color, hover_color=hover_color, text_color=button_text_color)
        self.repo_menu.configure(fg_color=button_color, button_color=button_color, button_hover_color=hover_color, text_color=button_text_color)
        self.execute_button.configure(fg_color=button_color, hover_color=hover_color, text_color=button_text_color)
        
        self.browse_button.configure(fg_color=button_color, hover_color=hover_color, text_color=button_text_color)
        self.file_browse_button.configure(fg_color=button_color, hover_color=hover_color, text_color=button_text_color)

    # --- Browse Functions ---
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.repo_path_entry.delete(0, "end")
            self.repo_path_entry.insert(0, directory)

    def browse_files(self):
        repo_path = self.repo_path_entry.get()
        initialdir = repo_path if (repo_path and os.path.isdir(repo_path)) else os.getcwd()
        
        files = filedialog.askopenfilenames(title="选择文件", initialdir=initialdir)
        if files:
            quoted_files = [f'\"{f}\"' if " " in f else f for f in files]
            self.files_entry.delete(0, "end")
            self.files_entry.insert(0, " ".join(quoted_files))

    # --- Execution ---
    def on_create_click(self):
        self.execute_button.configure(state="disabled", text="处理中...")
        threading.Thread(target=self._create_release_thread, daemon=True).start()

    def _create_release_thread(self):
        repo = self.repo_menu.get()
        local_path = self.repo_path_entry.get().strip()
        files_str = self.files_entry.get().strip()
        target = self.commit_entry.get().strip()
        tag = self.tag_entry.get().strip()
        title = self.release_title_entry.get().strip()
        notes = self.release_notes_entry.get("1.0", "end-1c").strip()
        
        if not tag:
            self.view_manager.log("错误: 必须填写 Tag (版本号)。")
            self.reset_btn()
            return
            
        self.view_manager.log(f"--- 任务开始 ---")
        self.view_manager.log(f"目标仓库: {repo}")
        self.view_manager.log(f"版本: {tag}")
        
        if files_str:
            files_to_upload = shlex.split(files_str)
        else:
            files_to_upload = []

        cmd = ["gh", "release", "create", tag]
        cmd.extend(files_to_upload)
        cmd.extend(["--repo", repo])
        if target:
            cmd.extend(["--target", target])
        cmd.extend(["--title", title])
        cmd.extend(["--notes", notes])
        
        self.view_manager.log(f"执行 gh release create...")
        code, out, err = self.view_manager.run_cmd(cmd)
        
        if code == 0:
            self.view_manager.log("成功！GitHub Release 已创建。")
            self.view_manager.log(out)
        else:
            self.view_manager.log("创建失败。")
            self.view_manager.log(err)
            
        self.reset_btn()

    def reset_btn(self):
        self.view_manager.after(0, lambda: self.execute_button.configure(state="normal", text="开始上传"))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("OneStepUpdate")
        self.geometry("500x750")
        
        icon_path = get_resource_path("OneStepUpdate.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except:
                pass

        self.current_theme = "dark"
        self.user_data = None
        self.user_avatar = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.views = {}
        # Only initialize LoginView at startup
        login_view = LoginView(self.container, self)
        self.views["LoginView"] = login_view
        login_view.grid(row=0, column=0, sticky="nsew")

        self.load_config()
        self.show_view("LoginView")
        self.after(100, self.check_env_and_login)

    def show_view(self, page_name):
        if page_name in self.views:
            frame = self.views[page_name]
            frame.tkraise()
        else:
            self.log(f"View {page_name} not found")

    def load_config(self):
        config_path = get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    self.current_theme = config.get("theme", "dark")
            except:
                pass
        ctk.set_appearance_mode(self.current_theme)

    def save_config(self):
        config = {"theme": self.current_theme}
        try:
            with open(get_config_path(), "w") as f:
                json.dump(config, f)
        except:
            pass

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
        else:
            self.current_theme = "dark"
        
        ctk.set_appearance_mode(self.current_theme)
        self.save_config()
        if "MainView" in self.views:
            self.views["MainView"].update_widget_colors()

    def log(self, msg):
        logging.info(msg)
        print(msg) # Also print to console for immediate feedback
        if "MainView" in self.views and self.views["MainView"].winfo_exists():
            log_box = self.views["MainView"].log_box
            log_box.configure(state="normal")
            log_box.insert("end", str(msg) + "\n")
            log_box.see("end")
            log_box.configure(state="disabled")

    def run_cmd(self, cmd, show_window=False):
        try:
            startupinfo = None
            creation_flags = 0
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                if not show_window:
                    creation_flags = subprocess.CREATE_NO_WINDOW

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                     text=True, encoding='utf-8', startupinfo=startupinfo, 
                                     creationflags=creation_flags)
            stdout, stderr = process.communicate()
            return process.returncode, stdout, stderr
        except Exception as e:
            logging.error(f"Command failed: {e}")
            return -1, "", str(e)

    def check_env_and_login(self):
        threading.Thread(target=self._check_env_thread, daemon=True).start()

    def _check_env_thread(self):
        self.log("正在检查环境...")
        code, out, err = self.run_cmd(["gh", "--version"])
        
        if code != 0:
            self.log("未检测到 Github CLI (gh)。请先安装。")
            # In a real app, you would show an InstallView here
            return

        self.check_login_status()

    def check_login_status(self):
        self.log("检查登录状态...")
        code, out, err = self.run_cmd(["gh", "api", "user"])
        
        if code != 0:
            self.log("未登录 GitHub CLI。")
            self.show_view("LoginView")
        else:
            try:
                if "MainView" not in self.views:
                    main_view = MainView(self.container, self)
                    self.views["MainView"] = main_view
                    main_view.grid(row=0, column=0, sticky="nsew")

                user_data = json.loads(out)
                self.user_data = user_data
                login = user_data.get("login", "Unknown")
                
                main_view = self.views["MainView"]
                main_view.username_label.configure(text=login)
                self.log(f"已登录: {login}")
                self.load_avatar(user_data.get("avatar_url"))
                self.load_repos()
                self.show_view("MainView")
            except Exception as e:
                self.log(f"解析用户信息失败: {e}")
                self.show_view("LoginView")

    def load_avatar(self, url):
        if not url: return
        try:
            response = requests.get(url, stream=True)
            img = Image.open(BytesIO(response.content)).resize((24, 24))
            self.user_avatar = ctk.CTkImage(light_image=img, dark_image=img, size=(24, 24))
            self.views["MainView"].avatar_label.configure(image=self.user_avatar)
        except Exception as e:
            self.log(f"Failed to load avatar: {e}")

    def load_repos(self):
        self.log("正在加载仓库列表...")
        code, out, err = self.run_cmd(["gh", "repo", "list", "--limit", "100", "--json", "nameWithOwner"])
        
        if code == 0:
            try:
                repos = json.loads(out)
                repo_names = [r["nameWithOwner"] for r in repos]
                if repo_names:
                    main_view = self.views["MainView"]
                    main_view.repo_menu.configure(values=repo_names)
                    main_view.repo_menu.set(repo_names[0])
                self.log("仓库列表加载完毕。")
            except Exception as e:
                self.log(f"仓库列表解析失败: {e}")
        else:
            self.log(f"加载仓库失败: {err}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
