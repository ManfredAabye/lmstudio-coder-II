# -*- coding: utf-8 -*-
## Dateiname: lmevolution.py (Selbstverbesserung)
# LMS Evolution Modul

import json
import difflib
import logging
from pathlib import Path
from datetime import datetime
import re

class LMEvolution:
    def __init__(self, plugin):
        self.plugin = plugin
        self.evolution_dir = Path("evolution_data")
        self.evolution_dir.mkdir(exist_ok=True)
        logging.info("Evolution module initialized")

    def _get_safe_filename(self, timestamp):
        """Convert timestamp to safe filename"""
        return re.sub(r'[^\w\-.]', '_', timestamp)

    def analyze_result(self, result):
        """Analyze processing results with complete argument handling"""
        try:
            if not all(key in result for key in ['file_path', 'original', 'processed']):
                raise ValueError("Invalid result format")
            
            diff = self._calculate_diff(result['original'], result['processed'])
            score = self._score_changes(diff)
            
            # Pass all required arguments including the current prompt
            self._save_analysis(
                file_path=result['file_path'],
                diff=diff,
                score=score,
                prompt=self.plugin.current_prompt  # Added this argument
            )
            
            if score < 50 and getattr(self.plugin.gui, 'auto_optimize', False):
                self._optimize_prompt()
                
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            logging.error(error_msg)
            self.plugin.gui.show_error(error_msg)

    def _calculate_diff(self, original, processed):
        """Generate unified diff"""
        return list(difflib.unified_diff(
            original.splitlines(),
            processed.splitlines(),
            fromfile='original',
            tofile='processed'
        ))

    def _score_changes(self, diff):
        """Score changes based on rules"""
        added = sum(1 for line in diff if line.startswith('+') and '#' in line)
        modified = sum(1 for line in diff if line.startswith('-') and not line.startswith('-#'))
        return added - (modified * 10)

    def _save_analysis(self, file_path, diff, score, prompt):
        """Save analysis data with all required parameters"""
        try:
            timestamp = datetime.now().isoformat()
            safe_timestamp = re.sub(r'[^\w\-.]', '_', timestamp)
            filename = f"analysis_{safe_timestamp}.json"
            
            data = {
                "file": str(file_path),
                "timestamp": timestamp,
                "score": score,
                "diff": diff,
                "prompt": prompt  # Now properly included
            }
            
            with open(self.evolution_dir / filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logging.info(f"Saved analysis: {filename}")
        except Exception as e:
            logging.error(f"Failed to save analysis: {str(e)}")
            raise

    def _optimize_prompt(self):
        """Optimize prompt using AI with proper response handling"""
        try:
            if not self.plugin.current_prompt:
                raise ValueError("No active prompt to optimize")
            
            # Get current prompt data safely
            current_prompt = {
                'positive': self.plugin.current_prompt.get('positive', ''),
                'negative': self.plugin.current_prompt.get('negative', '')
            }
            
            # Call API for optimization
            optimized = self.plugin.api_handler.optimize_prompt(current_prompt)
            
            # Validate and parse API response
            if not isinstance(optimized, dict):
                raise ValueError("Invalid API response format")
            
            required_keys = {'positive', 'negative'}
            if not all(key in optimized for key in required_keys):
                raise ValueError("Optimized prompt missing required fields")
            
            # Save new prompt
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"optimized_{timestamp}"
            
            self.plugin.prompt_manager.save_prompt(
                name=name,
                positive=optimized['positive'],
                negative=optimized['negative']
            )
            
            logging.info(f"Prompt optimized and saved as {name}")
            self.plugin.gui.update_status(f"New prompt saved: {name}")
            
        except ValueError as e:
            error_msg = f"Prompt validation error: {str(e)}"
            logging.error(error_msg)
            self.plugin.gui.show_error(error_msg)
        except Exception as e:
            error_msg = f"Optimization failed: {str(e)}"
            logging.error(error_msg)
            self.plugin.gui.show_error(error_msg)