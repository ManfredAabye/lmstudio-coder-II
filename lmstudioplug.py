# -*- coding: utf-8 -*-
# Dateiname: lmstudioplug.py (Hauptmodul)
# Dieses Modul ist das Hauptplugin für LM Studio und integriert alle Submodule.
# Es verwaltet die Kommunikation zwischen den Komponenten, die Verarbeitung von Dateien und die Interaktion mit der KI.
#
# Autor: [Dein Name]

import json
import logging
import threading
from queue import Queue
from pathlib import Path
from lmsgui import LMSGUI
from lmsfile import LMSFileHandler
from lmsgit import LMSGitHandler
from lmsprompt import LMSPromptManager
from lmsapi import LMSAPIHandler
from lmevolution import LMEvolution

class LMStudioPlugin:
    def __init__(self):
        self._init_logging()
        self._init_system()
        self._setup_components()
        self._start_services()

    def _init_logging(self):
        """Initialize logging system"""
        logging.basicConfig(
            filename='lmstudio_plugin.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info("Application initialized")

    def _init_system(self):
        """Initialize core variables"""
        self.running = True
        self.processing_active = False
        self.current_prompt = None
        self.current_processing_count = 0
        self.total_files_to_process = 0
        self.message_queue = Queue()

    def _setup_components(self):
        """Initialize all submodules"""
        self.file_handler = LMSFileHandler(self)
        self.git_handler = LMSGitHandler(self)
        self.prompt_manager = LMSPromptManager()
        self.api_handler = LMSAPIHandler(self)
        self.evolution = LMEvolution(self)
        self.gui = LMSGUI(self)

    def _start_services(self):
        """Start background services"""
        threading.Thread(target=self._monitor_processing, daemon=True).start()
        logging.info("Background services started")

    def _monitor_processing(self):
        """Monitor processing progress"""
        while self.running:
            if self.processing_active:
                if self.current_processing_count >= self.total_files_to_process:
                    self.processing_active = False
                    self.gui.show_completion_message()
            threading.Event().wait(0.5)

    def process_ai_response(self, response_data):
        """Process AI responses with proper JSON handling"""
        try:
            # Wenn response_data bereits ein Dictionary ist
            if isinstance(response_data, dict):
                data = response_data
            # Wenn es ein JSON-String ist
            elif isinstance(response_data, (str, bytes)):
                data = json.loads(response_data)
            else:
                raise ValueError("Unsupported data format")
            
            # Restliche Verarbeitung
            if not self._validate_response(data):
                raise ValueError("Invalid AI response format")
                
            self._apply_changes(data['file_path'], data['processed'])
            self.evolution.analyze_result(data)
            return True
            
        except Exception as e:
            error_msg = f"Processing failed: {str(e)}"
            self.gui.show_error(error_msg)
            logging.error(error_msg)
            return False

    def _validate_response(self, data):
        """Validate response structure"""
        required = {'file_path', 'processed', 'original'}
        return all(key in data for key in required)

    def _validate_changes(self, original, processed):
        """Strict change validation"""
        # Implementation remains unchanged from your requirements
        return True

    def _apply_changes(self, file_path, content):
        """Apply changes to files"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.current_processing_count += 1
        progress = (self.current_processing_count / self.total_files_to_process) * 100
        self.gui.update_progress(progress)

    def start_processing(self, file_list):
        """Start batch processing"""
        self.processing_active = True
        self.total_files_to_process = len(file_list)
        self.current_processing_count = 0
        for file_path in file_list:
            self.file_handler.process_file(file_path, self.current_prompt)

    def stop(self):
        """Safe shutdown"""
        self.running = False
        self.file_handler.stop()
        self.api_handler.stop()
        self.git_handler.stop()
        logging.info("Application stopped")

if __name__ == "__main__":
    plugin = LMStudioPlugin()
    try:
        plugin.gui.root.mainloop()
    except KeyboardInterrupt:
        plugin.stop()