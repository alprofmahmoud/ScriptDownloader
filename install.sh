#!/usr/bin/env bash
# install.sh - Setup script for ScriptDownloader.
# Creates (or reuses) a Python virtual environment at ./.venv and installs
# all required dependencies inside it, so the system/global Python
# environment (e.g. Termux's) is never touched.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/.venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

echo "ScriptDownloader install script"
echo "Project directory: $SCRIPT_DIR"

# --- Step 1: find a python3 interpreter ---
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "Error: no python3/python interpreter found on this system."
    exit 1
fi
echo "Using interpreter: $("$PYTHON_BIN" --version)"

# --- Step 2: detect whether we're already inside a virtual environment ---
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Already running inside a virtual environment: $VIRTUAL_ENV"
    ACTIVE_VENV="$VIRTUAL_ENV"
else
    # --- Step 3: create the venv if it doesn't exist yet, then activate it ---
    if [ ! -d "$VENV_DIR" ]; then
        echo "No virtual environment found. Creating one at: $VENV_DIR"
        "$PYTHON_BIN" -m venv "$VENV_DIR"
    else
        echo "Found existing virtual environment at: $VENV_DIR"
    fi
    ACTIVE_VENV="$VENV_DIR"
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    echo "Activated virtual environment: $VENV_DIR"
fi

# --- Step 4: keep pip itself reasonably current ---
python -m pip install --upgrade pip --quiet

# --- Step 5: install only whatever dependency is actually missing ---
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "Error: requirements.txt not found at $REQUIREMENTS_FILE"
    exit 1
fi

echo "Checking dependencies from requirements.txt..."
MISSING=0
while IFS= read -r pkg; do
    [ -z "$pkg" ] && continue
    pkg_name="${pkg%%[<>=!~]*}"
    if python -m pip show "$pkg_name" >/dev/null 2>&1; then
        echo "  [ok]      $pkg_name"
    else
        echo "  [missing] $pkg_name -> will install"
        MISSING=1
    fi
done < "$REQUIREMENTS_FILE"

if [ "$MISSING" -eq 1 ]; then
    echo "Installing missing dependencies from requirements.txt..."
    python -m pip install -r "$REQUIREMENTS_FILE"
else
    echo "All dependencies from requirements.txt are already installed."
fi

echo ""
echo "Setup complete."
echo "Virtual environment: $ACTIVE_VENV"

# --- Step 7: mark installation as verified, so main_sd.py can skip its
# own dependency check on every startup (it only re-checks when this file
# is missing, e.g. install.sh was never run or the data folder was wiped) ---
DATA_DIR="$SCRIPT_DIR/data"
mkdir -p "$DATA_DIR"
python -c "import json; json.dump({'verified': True}, open('$DATA_DIR/.install_state.json', 'w'))"
echo "Wrote install marker: $DATA_DIR/.install_state.json"

echo "To activate it manually in a new shell, run:"
echo "  source \"$VENV_DIR/bin/activate\""
echo "Then run the tool with: python main_sd.py"
