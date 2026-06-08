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
