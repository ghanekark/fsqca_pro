# fsQCA Pro
# Copyright (C) 2026 ImmortalSoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import datetime
from typing import List, Dict, Any, Optional

class ResearchLogger:
    """
    A singleton logger for recording critical analytical decisions in fsQCA.
    Supports JSON-based internal tracking and Markdown export for replicability reports.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ResearchLogger, cls).__new__(cls)
            cls._instance.log_entries: List[Dict[str, Any]] = []
        return cls._instance

    def log_action(self, category: str, description: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Records an analytical action with timestamp and optional metadata.
        
        Args:
            category: Action type (e.g., 'CALIBRATION', 'MINIMIZATION').
            description: Human-readable explanation of the action.
            metadata: Structured data related to the action (e.g., thresholds, parameters).
        """
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "category": category,
            "description": description,
            "metadata": metadata or {}
        }
        self.log_entries.append(entry)

    def export_log(self, filepath: str) -> bool:
        """
        Exports the research log as a human-readable report (Markdown or TXT).
        
        Args:
            filepath: Destination path for the file.
        
        Returns:
            True if export was successful, False otherwise.
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("# Research Transparency & Replicability Log\n\n")
                f.write(f"**Generated on:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")

                if not self.log_entries:
                    f.write("*No actions recorded yet.*\n")
                    return True

                for entry in self.log_entries:
                    f.write(f"### [{entry['category']}] - {entry['timestamp']}\n")
                    f.write(f"**Description:** {entry['description']}\n\n")
                    if entry['metadata']:
                        f.write("**Metadata:**\n")
                        for k, v in entry['metadata'].items():
                            f.write(f"- **{k}:** {v}\n")
                        f.write("\n")
                    f.write("---\n\n")
            return True
        except Exception as e:
            # Note: Using print for internal debugging; in production we might use a proper logger.
            print(f"Failed to export research log: {e}")
            return False

    def clear_log(self) -> None:
        """Clears all entries from the current session log."""
        self.log_entries = []
