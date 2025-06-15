# -*- coding: utf-8 -*-
## Dateiname: lmevolution.py (Selbstverbesserung)
# LMS Evolution Modul

import difflib
import json
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
        """Analyze and save processing results"""
        try:
            diff = self._calculate_diff(result['original'], result['processed'])
            score = self._score_changes(diff)
            self._save_analysis(
                file_path=result['file_path'],
                diff=diff,
                score=score,
                prompt=self.plugin.current_prompt
            )
            
            if score < 50:  # Optimization threshold
                self._optimize_prompt()
        except Exception as e:
            logging.error(f"Analysis failed: {str(e)}")
            self.plugin.gui.show_error(f"Analysis error: {str(e)}")

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
        """Save analysis data with safe filename"""
        try:
            timestamp = datetime.now().isoformat()
            safe_timestamp = self._get_safe_filename(timestamp)
            filename = f"analysis_{safe_timestamp}.json"
            
            data = {
                "file": str(file_path),
                "timestamp": timestamp,
                "score": score,
                "diff": diff,
                "prompt": prompt
            }
            
            with open(self.evolution_dir / filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logging.info(f"Saved analysis: {filename}")
        except Exception as e:
            logging.error(f"Failed to save analysis: {str(e)}")
            raise

    def _optimize_prompt(self):
        """Optimize prompt using AI"""
        try:
            optimized = self.plugin.api_handler.optimize_prompt(self.plugin.current_prompt)
            name = f"optimized_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.plugin.prompt_manager.save_prompt(
                name=name,
                positive=optimized['positive'],
                negative=optimized['negative']
            )
            logging.info(f"Prompt optimized and saved as {name}")
        except Exception as e:
            logging.error(f"Prompt optimization failed: {str(e)}")