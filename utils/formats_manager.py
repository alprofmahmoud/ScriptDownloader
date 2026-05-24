import os
from config import FORMATS_FILE


class FormatsManager:
    MAX_FORMATS = 5  # Maximum saved formats (excluding default)

    def __init__(self, file_path=FORMATS_FILE):
        self.file_path = file_path
        self.formats = self._load_formats()

    def _load_formats(self):
        """Load formats from file"""
        if not os.path.exists(self.file_path):
            self._create_default_file()
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            formats = [line.strip() for line in lines if line.strip()]
            return formats if formats else []
        except Exception as e:
            print(f"❗Error reading formats: {e}")
            return []

    def _create_default_file(self):
        """Create empty format file"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as _:
                pass  # Empty file
            print(f"✅ Created formats file: {self.file_path}")
        except Exception as e:
            print(f"❗Error creating file: {e}")

    def _get_best_format(self):
        """Return best format"""
        return "best"

    def _get_hd_format(self):
        """Return hd format"""
        return "hd"

    def add_new_format(self, new_format):
        """Add new format - reset if max reached"""
        # Check duplicate
        if new_format in self.formats:
            print("format already exists")
            return False
        # Check max limit
        if len(self.formats) >= self.MAX_FORMATS:
            print(
                    f"❗Max formats reached ({self.MAX_FORMATS}). "
                    f"Resetting...")
            self._reset_file()
        try:
            # Append to file
            with open(self.file_path, 'a', encoding='utf-8') as file:
                file.write(new_format + '\n')
            # Add to memory
            self.formats.append(new_format)
            print(f"✅ Format added: {new_format}")
            return True
        except Exception as e:
            print(f"❗Error adding format: {e}")
            return False

    def _reset_file(self):
        """Clear file and reset formats"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as _:
                pass  # Empty file
            self.formats = []
            print("🔄 Formats reset")
        except Exception as e:
            print(f"❗Error resetting file: {e}")

    def select_format(self):
        """Display menu and return selected format"""
        while True:
            # Build options
            options = {}
            actions = {}
            # Add best (always first)
            best_format = self._get_best_format()
            options["1"] = best_format
            actions["1"] = lambda: best_format
            # Add HD (always second)
            hd_format = self._get_hd_format()
            options["2"] = hd_format
            actions["2"] = lambda: hd_format
            # Add saved format
            for i, format_id in enumerate(self.formats, 3):
                options[str(i)] = format_id
                actions[str(i)] = lambda format_=format_id: format_
            # Add "Add New" option
            add_key = str(len(self.formats) + 3)
            options[add_key] = "Add New Format ID"
            actions[add_key] = self._prompt_new_format
            # Display menu
            from menus.menu import Menu
            format_menu = Menu(
                title="Select Format ID",
                options=options,
                actions=actions
            )
            result = format_menu.run()
            # Validate result
            if result:
                return result
            # Loop if invalid choice

    def _prompt_new_format(self):
        """Prompt user for new format"""
        print("="*38)
        print(f"{' '*10}Add New Format ID")
        print("="*38)
        new_format = input("Enter format ID: ").strip()
        if not new_format:
            print("❌ No format entered")
            return None
        # Add format ID
        if self.add_new_format(new_format):
            return new_format  # Return new format
        return None  # Failed - loop again
