
# Data Engineering Labs 2025

This repository contains the **public lab code** that accompanies the book.
All examples assume a **single standard runtime** so that you can focus
on the ideas, not on environment setup.

---

## Standard Runtime: GitHub Codespaces

All labs are designed to run in **GitHub Codespaces** using the devcontainer
configuration included in this repository.

### Prerequisites

- A GitHub account with access to GitHub Codespaces

### Setup (Recommended: Codespaces)

1. Open this repository on GitHub:  
   https://github.com/mikieto/data-eng-labs-2025


2. Click **“Code” → “Create codespace on main”**
   (or open an existing Codespace for this repo).

3. When the Codespace is ready, open a terminal inside the Codespace and run:

```bash
python labs/ch02/run.py
```

If you see output for the CH02 lab, your environment is ready.
All labs in this repository assume this runtime.

---

## Advanced: Local Dev Container (Optional)

If you prefer to run the devcontainer **locally**:

1. Install Docker and Visual Studio Code on your machine.

2. Clone this repository:

```bash
git clone https://github.com/mikieto/data-eng-labs-2025.git
cd data-eng-labs-2025
```

3. Open the folder in VS Code and use
   **“Dev Containers: Reopen in Container”**.

4. Then run:

```bash
python labs/ch02/run.py
```

The book and the per-chapter READMEs, however, treat **GitHub Codespaces**
as the default runtime.

---

## Repository Structure (high level)

* `labs/ch02/` — Lab for CH02 (Boundary, Change Unit, Evidence, RB-30)
* `labs/ch05/` — Lab for CH05 (Single Change Highway)
* `labs/ch07/` — Lab for CH07 (AI-assisted change packs)
* (more labs may be added over time)

Each lab folder has its own `README.md` that explains:

* Learning objectives
* Files used in that lab
* The steps you perform **after** your environment is ready

Please always follow the **Standard Runtime (GitHub Codespaces)** section
above before starting any lab. Once your Codespace is running, each chapter README
will guide you step by step.