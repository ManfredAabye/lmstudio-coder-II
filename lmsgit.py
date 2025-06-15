# -*- coding: utf-8 -*-
## Dateiname: lmsgit.py (GitHub Integration)
# LMS Git Handler
#

from github import Github
import subprocess
import tempfile
import shutil
import logging
import queue
import threading
from pathlib import Path

class LMSGitHandler:
    def __init__(self, plugin):
        self.plugin = plugin
        self.github = None
        self.task_queue = queue.Queue()
        self.running = True
        self.worker = threading.Thread(target=self._process_tasks)
        self.worker.start()
        logging.info("Git handler initialized")

    def authenticate(self, token):
        """Authenticate with GitHub"""
        try:
            self.github = Github(token)
            self.plugin.gui.update_status("GitHub authentication successful")
            logging.info("GitHub authentication successful")
            return True
        except Exception as e:
            self.plugin.gui.show_error(f"GitHub auth failed: {str(e)}")
            logging.error(f"GitHub auth error: {str(e)}")
            return False

    def clone_repository(self, repo_url, local_path):
        """Add clone task to queue"""
        self.task_queue.put({
            'action': 'clone',
            'url': repo_url,
            'path': local_path
        })
        self.plugin.gui.update_status(f"Queued repository clone: {repo_url}")

    def _process_tasks(self):
        """Process GitHub tasks from queue"""
        while self.running:
            task = self.task_queue.get()
            if task['action'] == 'clone':
                self._clone_repository(task['url'], task['path'])
            self.task_queue.task_done()

    def _clone_repository(self, repo_url, local_path):
        """Clone repository using git CLI"""
        temp_dir = tempfile.mkdtemp()
        try:
            self.plugin.gui.update_status(f"Cloning {repo_url}...")
            result = subprocess.run(
                ["git", "clone", repo_url, temp_dir],
                check=True,
                capture_output=True,
                text=True
            )
            
            target = Path(local_path)
            if target.exists():
                shutil.rmtree(target)
            shutil.move(temp_dir, target)
            
            self.plugin.gui.update_status(f"Repository cloned to {local_path}")
            logging.info(f"Repository cloned: {repo_url} -> {local_path}")
        except subprocess.CalledProcessError as e:
            error = f"Clone failed: {e.stderr.strip()}"
            self.plugin.gui.show_error(error)
            logging.error(error)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def stop(self):
        """Stop git handler"""
        self.running = False
        self.task_queue.put({'action': 'shutdown'})
        self.worker.join()
        logging.info("Git handler stopped")