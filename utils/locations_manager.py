import os
from config import LOCATIONS_FILE


class LocationsManager:
    MAX_LOCATIONS = 12  # Maximum saved locations (excluding default)

    def __init__(self, file_path=LOCATIONS_FILE):
        self.file_path = file_path
        self.locations = self._load_locations()

    def _load_locations(self):
        """Load locations from file"""
        if not os.path.exists(self.file_path):
            self._create_default_file()
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            locations = [line.strip() for line in lines if line.strip()]
            return locations if locations else []
        except Exception as e:
            print(f"❗Error reading locations: {e}")
            return []

    def _create_default_file(self):
        """Create empty locations file"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as _:
                pass  # Empty file
            print(f"✅ Created locations file: {self.file_path}")
        except Exception as e:
            print(f"❗Error creating file: {e}")

    def _get_default_location(self):
        """Return fixed default location"""
        return "Downloads"

    def add_new_location(self, new_location):
        """Add new location - reset if max reached"""
        """
        # Expand path
        expanded = os.path.expanduser(new_location)
        # Validate path exists
        if not os.path.isdir(expanded):
            print(f"Path doesn't exist: {expanded}")
            return False
        """
        # Check duplicate
        if new_location in self.locations:
            print("ocation already exists")
            return False
        # Check max limit
        if len(self.locations) >= self.MAX_LOCATIONS:
            print(
                    f"❗Max locations reached ({self.MAX_LOCATIONS}). "
                    f"Resetting...")
            self._reset_file()
        try:
            # Append to file
            with open(self.file_path, 'a', encoding='utf-8') as file:
                file.write(new_location + '\n')
            # Add to memory
            self.locations.append(new_location)
            print(f"✅ Location added: {new_location}")
            return True
        except Exception as e:
            print(f"❗Error adding location: {e}")
            return False

    def _reset_file(self):
        """Clear file and reset locations"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as _:
                pass  # Empty file
            self.locations = []
            print("🔄 Locations reset")
        except Exception as e:
            print(f"❗Error resetting file: {e}")

    def select_location(self):
        """Display menu and return selected folder"""
        while True:
            # Build options
            options = {}
            actions = {}
            # Add default (always first)
            default = self._get_default_location()
            options["1"] = default
            actions["1"] = lambda: default
            # Add saved locations
            for i, loc in enumerate(self.locations, 2):
                options[str(i)] = loc
                actions[str(i)] = lambda folder=loc: folder
            # Add "Add New" option
            add_key = str(len(self.locations) + 2)
            options[add_key] = "Add New Location"
            actions[add_key] = self._prompt_new_location
            # Display menu
            from menus.menu import Menu
            location_menu = Menu(
                title="Select Download Location",
                options=options,
                actions=actions
            )
            result = location_menu.run()
            # Validate result
            if result:
                return result
            # Loop if invalid choice

    def _prompt_new_location(self):
        """Prompt user for new location"""
        print("="*46)
        print("             Add New Location")
        print("="*46)
        new_location = input("Enter folder path: ").strip()
        if not new_location:
            print("❌ No location entered")
            return None
        # Add location
        if self.add_new_location(new_location):
            return new_location  # Return new location
        return None  # Failed - loop again
