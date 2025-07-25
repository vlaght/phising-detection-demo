# Phishing Detection Streamlit App

A demo-page for phishing detection model trained within the study project for INFO80813 Artificial Intelligence


## Installation

### 1. Install uv package manager

#### On macOS and Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### On Windows:
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Alternative installation methods:
- **With pip**: `pip install uv`
- **With pipx**: `pipx install uv`
- **With Homebrew**: `brew install uv`

### 2. Install Project Dependencies

Navigate to the project directory and install dependencies:

```bash
cd phishing_detector
uv sync
```

This will automatically create a virtual environment and install all required packages.

## Running the app

To start:

```bash
uv run streamlit run app.py
```

The app will automatically open in your default web browser at `http://localhost:8501`.

If it doesn't open automatically, you can manually navigate to the URL shown in the terminal.

## Using the app

Instructions will be displayed on the app page; in case if the browser window wasn't opened, refer to the url in the terminal output.
