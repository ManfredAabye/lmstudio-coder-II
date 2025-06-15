# -*- coding: utf-8 -*-
## Dateiname: lmsprompt.py (Prompt Management)
## LMS Prompt Manager
# 
import json
import logging
from pathlib import Path
from datetime import datetime

class LMSPromptManager:
    def __init__(self):
        self.storage_dir = Path("prompts")
        self.storage_dir.mkdir(exist_ok=True)
        logging.info("Prompt manager initialized")

    def save_prompt(self, name, positive, negative, language="Python"):
        """Save prompt with strict validation"""
        prompt = {
            "name": name,
            "language": language,
            "positive": positive,
            "negative": negative,
            "created": datetime.now().isoformat()
        }
        
        try:
            path = self.storage_dir / f"{name}.json"
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(prompt, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"Failed to save prompt: {str(e)}")
            return False

    def load_prompt(self, name):
        """Load prompt with validation"""
        try:
            path = self.storage_dir / f"{name}.json"
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate structure
            required_keys = {'name', 'positive', 'negative'}
            if not all(key in data for key in required_keys):
                raise ValueError("Invalid prompt format")
            
            return {
                'name': data['name'],
                'positive': data['positive'],
                'negative': data['negative'],
                'language': data.get('language', 'Python')
            }
        except Exception as e:
            logging.error(f"Failed to load prompt '{name}': {str(e)}")
            return None

    def delete_prompt(self, name):
        """Delete prompt with backup"""
        try:
            path = self.storage_dir / f"{name}.json"
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            logging.error(f"Failed to delete prompt: {str(e)}")
            return False

    def list_prompts(self):
        """List only valid prompts"""
        valid_prompts = []
        for f in self.storage_dir.glob("*.json"):
            try:
                with open(f, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    if all(key in data for key in ['name', 'positive', 'negative']):
                        valid_prompts.append(f.stem)
            except:
                continue
        return valid_prompts
