# fsqca_pro

A specialized desktop application for **Fuzzy-Set Qualitative Comparative Analysis (fsQCA)**. `fsqca_pro` provides researchers and social scientists with a robust, modern interface for studying complex causal relationships through set-theoretic methods, prioritizing both analytical precision and scientific transparency.

## 🚀 Overview

`fsqca_pro` modernizes the qualitative comparative analysis workflow by bridging the gap between raw data and configurational models. It enables researchers to perform "theory-informed" calibration, build comprehensive truth tables, and execute advanced Boolean minimization algorithms. Built with a commitment to open-science principles, the application provides detailed audit trails for every analytical decision.

## ✨ Key Features

### 🏗️ Engineering Excellence
- **Strict MVC/MVVM Architecture:** Ensures a clean separation between set-theoretic algorithms (`models`), high-density user interfaces (`views`), and coordination logic (`controllers`).
- **Non-blocking Asynchronous UI:** All heavy computational tasks—including Quine-McCluskey minimization and batch calibration—are offloaded to background `QThread` workers, maintaining a fluid 60FPS user experience even with large datasets.
- **Dynamic Theme Engine:** Native support for Dark and Light modes, with user preferences persisted across sessions.

### 🧪 Advanced fsQCA Capabilities
- **Direct Method Calibration Interface:** A professional workspace for converting raw variables into fuzzy sets using qualitative anchors. Features real-time `matplotlib` distribution histograms with interactive anchor overlays.
- **Complexity-Parsimony Continuum Visualizer:** A unique auditing tool that aligns Complex, Intermediate, and Parsimonious solutions side-by-side, highlighting "Core" vs. "Complementary" conditions to make simplifying assumptions transparent.
- **Scientific Necessity Auditor:** Enhanced necessity analysis including "Relevance of Necessity" (RoN) and Triviality proxies, allowing researchers to distinguish between substantive findings and empirical artifacts.
- **One-Click Batch Calibration:** Rapidly operationalize entire datasets using industry-standard percentile benchmarks (95th/50th/5th).

### 📝 Methodological Transparency
- **Automated Metadata Audit Log:** Captures and persists the theoretical justifications for every calibrated variable in companion `.meta.json` files.
- **Ingestion Sanitization Reporting:** Automatically generates a "Transparency Report" during data load, documenting all automated renaming, type conversions, and case-dropping actions.
- **Visual Audit Tooltips:** Hover over any variable in the main data grid to instantly view its calibration anchors and theoretical rationale.

## 🛠️ Installation

### Prerequisites
- Python 3.10 or higher
- Windows 10/11 (Optimized for high-DPI scaling)

### Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/ghanekark/fsqca_pro.git
   cd fsqca_pro
   ```

2. **Create and activate a virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

## 📁 Directory Structure

- **`main.py`**: Application entry point and controller initialization.
- **`controllers/`**: Logic binding models and views, including theme and analysis orchestration.
- **`models/`**: Data processing, QCA algorithms, and metadata persistence.
- **`views/`**: PyQt6 windows and dialogs for analysis and visualization.
- **`styles/`**: QSS templates for dynamic theming.
- **`utils/`**: Asynchronous workers, result formatters, and helper functions.
