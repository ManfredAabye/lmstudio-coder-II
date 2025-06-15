# -*- coding: utf-8 -*-
# lmsgui.py (Tkinter UI)
# # This file implements the GUI for the LMStudio AI Coder plugin using Tkinter.
#

import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from threading import Thread
from pathlib import Path
from tkinter import simpledialog

class LMSGUI:
    def __init__(self, plugin):
        self.plugin = plugin
        self.root = tk.Tk()
        self._setup_main_window()
        self._create_widgets()
        self._setup_bindings()
        logging.info("GUI initialized")

    def _setup_main_window(self):
        self.root.title("LMStudio AI Coder")
        #self.root.geometry("615x500")
        self.root.geometry("")  # Keine feste Größe setzen
        self.root.iconbitmap("icon.ico")  # Icon setzen (Datei muss existieren)
        self.style = ttk.Style()
        self.style.configure('TNotebook.Tab', padding=[20, 5])

    def _create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        
        # File Processing Tab
        self._build_file_tab()
        
        # GitHub Integration Tab
        self._build_git_tab()
        
        # Prompt Management Tab
        self._build_prompt_tab()
        
        # Evolution Tab
        self._build_evolution_tab()

        self.notebook.pack(expand=True, fill='both')

    def _build_file_tab(self):
        frame = ttk.Frame(self.notebook)
        
        # File Selection
        ttk.Label(frame, text="Target Path:").grid(row=0, column=0, sticky='w')
        self.path_entry = ttk.Entry(frame, width=60)
        self.path_entry.grid(row=0, column=1)
        ttk.Button(frame, text="Browse File", command=self._browse_file).grid(row=0, column=2)
        ttk.Button(frame, text="Browse Folder", command=self._browse_folder).grid(row=0, column=3)
        
        # Prompt Editors
        self._setup_prompt_editors(frame)
        
        # Control Buttons
        self._setup_control_buttons(frame)
        
        # Progress
        self.progress = ttk.Progressbar(frame, orient='horizontal', length=600, mode='determinate')
        self.progress.grid(row=5, columnspan=4, pady=10)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(frame, textvariable=self.status_var).grid(row=6, columnspan=4)
        
        self.notebook.add(frame, text="File Processing")

    def _setup_prompt_editors(self, parent):
        notebook = ttk.Notebook(parent)
        
        # Positive Prompt
        pos_frame = ttk.Frame(notebook)
        self.positive_text = scrolledtext.ScrolledText(pos_frame, wrap=tk.WORD, width=70, height=15)
        self.positive_text.pack(fill='both', expand=True)
        notebook.add(pos_frame, text="POSITIVE")
        
        # Negative Prompt
        neg_frame = ttk.Frame(notebook)
        self.negative_text = scrolledtext.ScrolledText(neg_frame, wrap=tk.WORD, width=70, height=15)
        self.negative_text.pack(fill='both', expand=True)
        notebook.add(neg_frame, text="NEGATIVE")
        
        notebook.grid(row=2, columnspan=4, pady=10)

    def _setup_control_buttons(self, parent):
        btn_frame = ttk.Frame(parent)
        
        self.start_btn = ttk.Button(btn_frame, text="Start", command=self._start_processing)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self._stop_processing, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="Exit", command=self._safe_exit).pack(side='right', padx=5)
        
        btn_frame.grid(row=4, columnspan=4, pady=10)

    def _build_git_tab(self):
        frame = ttk.Frame(self.notebook)
        
        # GitHub Authentication
        ttk.Label(frame, text="GitHub Token:").grid(row=0, column=0, sticky='e')
        self.token_entry = ttk.Entry(frame, width=50, show='*')
        self.token_entry.grid(row=0, column=1)
        ttk.Button(frame, text="Authenticate", command=self._authenticate).grid(row=0, column=2)
        
        # Repository Download
        ttk.Label(frame, text="Repository URL:").grid(row=1, column=0, sticky='e')
        self.repo_entry = ttk.Entry(frame, width=50)
        self.repo_entry.grid(row=1, column=1)
        ttk.Button(frame, text="Download", command=self._download_repo).grid(row=1, column=2)
        
        self.notebook.add(frame, text="GitHub")

    def _build_prompt_tab(self):
        frame = ttk.Frame(self.notebook)
        
        # Prompt List
        ttk.Label(frame, text="Saved Prompts:").grid(row=0, column=0, sticky='w')
        self.prompt_list = ttk.Combobox(frame, state='readonly', width=50)
        self.prompt_list.grid(row=0, column=1)
        self._update_prompt_list()
        
        # Prompt Actions
        btn_frame = ttk.Frame(frame)
        ttk.Button(btn_frame, text="Load", command=self._load_prompt).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Save", command=self._save_prompt).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Delete", command=self._delete_prompt).pack(side='left', padx=2)
        btn_frame.grid(row=1, columnspan=2, pady=5)
        
        self.notebook.add(frame, text="Prompts")

    def _build_evolution_tab(self):
        frame = ttk.Frame(self.notebook)
        
        ttk.Label(frame, text="Evolution Settings:").grid(row=0, column=0, sticky='w')
        
        self.auto_optimize = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame,
            text="Enable Automatic Prompt Optimization",
            variable=self.auto_optimize
        ).grid(row=1, column=0, sticky='w')
        
        ttk.Button(
            frame,
            text="Run Manual Optimization",
            command=self._run_optimization
        ).grid(row=2, column=0, pady=5)
        
        self.notebook.add(frame, text="Evolution")

    def _setup_bindings(self):
        self.root.protocol("WM_DELETE_WINDOW", self._safe_exit)
        self.root.bind("<Control-s>", lambda e: self._save_prompt())
        self.root.bind("<Control-o>", lambda e: self._load_prompt())

    def _browse_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def _browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def _authenticate(self):
        token = self.token_entry.get()
        if token:
            Thread(target=self.plugin.git_handler.authenticate, args=(token,), daemon=True).start()

    def _download_repo(self):
        url = self.repo_entry.get()
        path = self.path_entry.get()
        if url and path:
            self.plugin.git_handler.clone_repository(url, path)

    def _update_prompt_list(self):
        prompts = self.plugin.prompt_manager.list_prompts()
        self.prompt_list['values'] = prompts
        if prompts:
            self.prompt_list.current(0)

    def _load_prompt(self):
        name = self.prompt_list.get()
        if not name:
            return
        
        prompt = self.plugin.prompt_manager.load_prompt(name)
        if not prompt:
            self.show_error("Invalid prompt format")
            return
        
        try:
            # Clear existing content
            self.positive_text.delete(1.0, tk.END)
            self.negative_text.delete(1.0, tk.END)
            
            # Insert new content
            self.positive_text.insert(tk.END, prompt['positive'])
            self.negative_text.insert(tk.END, prompt['negative'])
            
            # Store in plugin
            self.plugin.current_prompt = {
                'positive': prompt['positive'],
                'negative': prompt['negative']
            }
            
            self.update_status(f"Loaded prompt: {name}")
        except Exception as e:
            self.show_error(f"Failed to load prompt: {str(e)}")
            logging.error(f"Prompt load error: {str(e)}")

    def _save_prompt(self):
        name = simpledialog.askstring("Save Prompt", "Enter prompt name:")
        if name:
            prompt = {
                "positive": self.positive_text.get(1.0, tk.END).strip(),
                "negative": self.negative_text.get(1.0, tk.END).strip()
            }
            if self.plugin.prompt_manager.save_prompt(name, **prompt):
                self._update_prompt_list()
                self.update_status(f"Saved prompt: {name}")

    def _delete_prompt(self):
        name = self.prompt_list.get()
        if name and messagebox.askyesno("Confirm", f"Delete prompt '{name}'?"):
            if self.plugin.prompt_manager.delete_prompt(name):
                self._update_prompt_list()
                self.update_status(f"Deleted prompt: {name}")

    def _start_processing(self):
        path = self.path_entry.get()
        if not path:
            self.show_error("No target path specified")
            return
        
        if not self.plugin.current_prompt:
            self.show_error("No prompt loaded")
            return
        
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        if Path(path).is_file():
            files = [path]
        else:
            files = [f for f in Path(path).rglob('*') if f.is_file()]
        
        Thread(target=self.plugin.start_processing, args=(files,), daemon=True).start()

    def _stop_processing(self):
        self.plugin.stop_processing()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')

    def _run_optimization(self):
        if not self.plugin.current_prompt:
            self.show_error("No active prompt to optimize")
            return
        Thread(target=self.plugin.evolution.optimize_prompt, daemon=True).start()

    def _safe_exit(self):
        if messagebox.askokcancel("Exit", "Stop processing and quit?"):
            self.plugin.stop()
            self.root.destroy()

    def update_status(self, message):
        self.status_var.set(message)
        logging.info(message)

    def show_error(self, message):
        self.status_var.set(f"ERROR: {message}")
        logging.error(message)
        messagebox.showerror("Error", message)

    def show_completion_message(self):
        messagebox.showinfo("Complete", "Processing completed successfully")
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')

    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update_idletasks()