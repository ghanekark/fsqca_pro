# fsqca_pro: Project Instructions

This document defines the foundational mandates, architecture, and engineering standards for the `fsqca_pro` project. All development must adhere to these guidelines.

## 1. Core Mandates
- **Language:** Python 3.10+
- **Framework:** PyQt6
- **Dependency Management:** `requirements.txt`
- **Style Guide:** Strict adherence to [PEP 8](https://peps.python.org/pep-0008/).

## 2. Engineering Standards

### Type Safety
- **Strict Type Hinting:** All functions and methods must include comprehensive type hints for parameters and return values.
- **No `Any`:** Avoid using `Any` where a more specific type can be defined.

### Architectural Patterns
- **Separation of Concerns:** Maintain a strict separation between UI code (`views/`), business logic (`models/`), and coordination logic (`controllers/`).
- **MVC/MVVM:** Use Model-View-Controller or Model-View-ViewModel patterns to ensure the UI remains thin and logic remains testable.
- **Signal/Slot Communication:** Prefer PyQt signals and slots for communication between components rather than direct method calls across layers.

### UI & Performance
- **Non-blocking UI:** Any operation that takes longer than 100ms (e.g., file I/O, complex minimization, large data transformations) **MUST** be offloaded to a `QThread` or `QRunnable`.
- **Responsive Design:** Use layouts (`QVBoxLayout`, `QHBoxLayout`, `QGridLayout`) exclusively. Avoid fixed geometries (`setGeometry`).
- **Resource Management:** Ensure proper cleanup of resources and parent-child relationships in Qt objects to prevent memory leaks.

## 3. Directory Structure
- `main.py`: Application entry point and controller initialization.
- `models/`: Data processing, QCA algorithms, and business logic.
- `views/`: PyQt6 windows, dialogs, and custom widgets.
- `controllers/`: Logic binding models and views.
- `utils/`: Helpers, worker threads, and formatters.

## 4. Quality and Documentation
- Docstrings: Specify a standard. For example: "Use Google Style docstrings for all classes and functions to document parameters and return types."
- Error Handling & Logging: Guide the CLI on how to handle failures. For example: "Do not use print() statements. Use Python's native logging module. For user-facing critical errors, surface them using QMessageBox.critical."
- Testing: Tell the model how to write tests for your specific stack. For example: "Write unit tests using pytest and pytest-qt. Ensure all controller logic is tested independently of the views."

## 5. Execution & Modification Boundaries
When modifying code, adding features, or debugging, you MUST adhere to the following strict boundaries:
- **Zero Collateral Damage:** Do not change, refactor, or "clean up" anything outside the exact scope of the immediate prompt or the current PRD step.
- **Precision Preservation:** Retain all surrounding code, logic, and formatting precisely as is. 
- **Containment:** Ensure your updates do not introduce side effects to other components, particularly existing PyQt6 UI threads, models, and signal/slot connections.
- **No Unsolicited Rewrites:** Provide only the code requested. Never rewrite or alter surrounding functions unless explicitly commanded to do so.