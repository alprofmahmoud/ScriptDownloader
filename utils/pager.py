import os
import shutil
import subprocess


def page_text(text):
    """
    Display text using the system 'less' command, exactly like piping
    output into `less`. Falls back to plain print() if 'less' isn't
    available on the system (e.g. some minimal Windows setups).

    -R : show raw ANSI color codes correctly instead of garbling them
    -X : don't clear the screen on exit, so the table stays visible
    -F : if the content fits on one screen, print it and exit
         immediately instead of waiting for a keypress
    """
    if not text:
        print("No data to display.")
        return

    less_path = shutil.which("less")
    if not less_path:
        # No 'less' available on this system, just print normally
        print(text)
        return

    env = os.environ.copy()
    # Sensible default so 'less' behaves the same way across systems
    env.setdefault("LESS", "-R")

    try:
        subprocess.run(
            [less_path, "-R", "-X", "-F"],
            input=text.encode("utf-8"),
            env=env,
        )
    except Exception as e:
        # If anything goes wrong invoking 'less', don't lose the data
        print(f"⚠️ Couldn't open pager ({e}), printing instead:\n")
        print(text)
