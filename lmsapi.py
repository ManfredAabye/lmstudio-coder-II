# -*- coding: utf-8 -*-
## Dateiname: lmsapi.py (API Kommunikation)
#
import requests
import json
import queue
import threading
import logging
from urllib.parse import urljoin

class LMSAPIHandler:
    def __init__(self, plugin):
        self.plugin = plugin
        self.base_url = "http://localhost:1234/v1/"
        self.request_queue = queue.Queue()
        self.running = True
        self.worker = threading.Thread(target=self._process_requests)
        self.worker.start()
        logging.info("API handler initialized")

    def process_content(self, data):
        """Add processing request to queue"""
        self.request_queue.put({
            'action': 'process',
            'data': data
        })

    def optimize_prompt(self, prompt):
        """Optimize prompt via API"""
        try:
            response = requests.post(
                urljoin(self.base_url, "chat/completions"),
                json={
                    "messages": [
                        {
                            "role": "system", 
                            "content": "Optimize this coding prompt while maintaining strict constraints:"
                        },
                        {
                            "role": "user",
                            "content": json.dumps(prompt)
                        }
                    ],
                    "temperature": 0.5,
                    "max_tokens": 2000
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logging.error(f"Prompt optimization failed: {str(e)}")
            raise

    def _process_requests(self):
        """Process API requests from queue"""
        while self.running:
            task = self.request_queue.get()
            if task['action'] == 'process':
                self._call_api(task['data'])
            self.request_queue.task_done()

    def _call_api(self, data):
        """Call LMStudio API with comprehensive error handling"""
        try:
            # Validate input data structure
            if not all(key in data for key in ['file_path', 'content', 'prompt']):
                raise ValueError("Missing required fields in input data")
            if not isinstance(data['prompt'], dict) or not all(key in data['prompt'] for key in ['positive', 'negative']):
                raise ValueError("Invalid prompt format")

            # Prepare messages with strict validation
            messages = [
                {"role": "system", "content": str(data['prompt']['positive'])},
                {"role": "user", "content": str(data['content'])},
                {"role": "system", "content": f"Constraints: {str(data['prompt']['negative'])}"}
            ]

            # Prepare API request with timeout
            request_data = {
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 4000,
                "stream": False
            }

            # Make API call
            response = requests.post(
                urljoin(self.base_url, "chat/completions"),
                json=request_data,
                timeout=60,
                headers={"Content-Type": "application/json"}
            )

            # Check for HTTP errors
            response.raise_for_status()

            # Parse and validate response
            result = response.json()
            if 'choices' not in result or len(result['choices']) == 0:
                raise ValueError("Invalid API response format")

            # Prepare processed data with all required fields
            processed_data = {
                'file_path': str(data['file_path']),
                'original': str(data['content']),
                'processed': str(result['choices'][0]['message']['content'])
            }

            # Send to plugin for processing
            self.plugin.process_ai_response(processed_data)

        except requests.exceptions.RequestException as e:
            error_msg = f"API connection error: {str(e)}"
            self.plugin.gui.show_error(error_msg)
            logging.error(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"API response parsing failed: {str(e)}"
            self.plugin.gui.show_error(error_msg)
            logging.error(error_msg)
        except KeyError as e:
            error_msg = f"Missing expected data field: {str(e)}"
            self.plugin.gui.show_error(error_msg)
            logging.error(error_msg)
        except Exception as e:
            error_msg = f"Unexpected API error: {str(e)}"
            self.plugin.gui.show_error(error_msg)
            logging.error(error_msg)

    def stop(self):
        """Stop API handler"""
        self.running = False
        self.request_queue.put({'action': 'shutdown'})
        self.worker.join()
        logging.info("API handler stopped")