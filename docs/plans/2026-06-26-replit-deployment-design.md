# Design Document: Flask App Replit Deployment

This document outlines the design changes required to configure the Flask version of the Nusantara Palm-Estate Operations Planner & Sentinel (`main.py`) for automated and seamless deployment on Replit.

---

## 1. Goal
Ensure that the Flask app automatically detects the port assigned by Replit's environment, binds to `0.0.0.0` for public accessibility, and runs immediately when the "Run" button is clicked in Replit.

---

## 2. Proposed Changes

### A. Dynamic Port Binding
Replit dynamically assigns a port to web containers through the `PORT` environment variable. We will update the server startup block in [main.py](file:///c:/Users/oneda/Projects/nusantara-palm-sentinel-mvp/main.py) to read this variable, falling back to `5000` for local development.

### B. Replit Configuration File
We will create a new `.replit` file in the root of the project to tell Replit's workspace environment to execute `python main.py` as the default application launcher command.

---

## 3. Scope of Impact

### [NEW] [.replit](file:///c:/Users/oneda/Projects/nusantara-palm-sentinel-mvp/.replit)
- Setup Nix/Python environment configuration.
- Add entry point launch command `run = "python main.py"`.

### [MODIFY] [main.py](file:///c:/Users/oneda/Projects/nusantara-palm-sentinel-mvp/main.py)
- Import `os`.
- Retrieve port via `os.environ.get("PORT", 5000)`.
- Bind Flask to host `0.0.0.0` on that port.
