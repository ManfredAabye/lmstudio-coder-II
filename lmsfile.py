# -*- coding: utf-8 -*-
## Dateiname: lmsfile.py (Dateiverarbeitung)
#
import os
import queue
import threading
import logging
from pathlib import Path

class LMSFileHandler:
    SUPPORTED_EXTENSIONS = {
        '.py', '.js', '.java', '.cpp', '.c', '.h', 
        '.cs', '.php', '.rb', '.go', '.rs', '.ts'
    }

    def __init__(self, plugin):
        self.plugin = plugin
        self.file_queue = queue.Queue()
        self.running = True
        self.worker = threading.Thread(target=self._process_queue)
        self.worker.start()
        logging.info("File handler initialized")

    def process_file(self, file_path, prompt):
        """Add file to processing queue"""
        if not self._validate_file(file_path):
            return
        self.file_queue.put({
            'action': 'process',
            'path': str(file_path),
            'prompt': prompt
        })

    def _process_queue(self):
        """Process files from queue"""
        while self.running:
            task = self.file_queue.get()
            if task['action'] == 'process':
                self._handle_file(task['path'], task['prompt'])
            self.file_queue.task_done()

    def _handle_file(self, file_path, prompt):
        """Process single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.plugin.api_handler.process_content({
                'file_path': file_path,
                'content': content,
                'prompt': prompt
            })
        except Exception as e:
            self.plugin.gui.show_error(f"File error: {str(e)}")
            logging.error(f"File processing failed: {file_path} - {str(e)}")

    def _validate_file(self, file_path):
        """Check if file should be processed"""
        path = Path(file_path)
        return (
            path.exists() and 
            path.is_file() and 
            path.suffix.lower() in self.SUPPORTED_EXTENSIONS
        )

    def stop(self):
        """Stop file handler"""
        self.running = False
        self.file_queue.put({'action': 'shutdown'})
        self.worker.join()
        logging.info("File handler stopped")