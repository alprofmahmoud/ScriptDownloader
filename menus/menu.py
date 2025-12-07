class Menu:
    def __init__(self, title, options, actions):
        self.title = title
        self.options = options
        self.actions = actions

    def get_max_key_length(self):
        """Calculate max length of option keys"""
        if not self.options:
            return 1
        return max(len(key) for key in self.options.keys())

    def get_max_option_length(self):
        """Calculate max length of option descriptions"""
        if not self.options:
            return 0
        return max(len(desc) for desc in self.options.values())

    def get_box_width(self):
        """Calculate dynamic box width"""
        max_key_len = self.get_max_key_length()
        max_option = self.get_max_option_length()
        title_length = len(self.title)
        key_col = max_key_len + 2
        desc_width = max(max_option, title_length)
        total = key_col + 3 + desc_width + 2
        return total

    def display_menu(self):
        """Display formatted menu with dynamic key column width"""
        max_key_len = self.get_max_key_length()
        width = self.get_box_width() + 8
        key_col_width = max_key_len + 2
        # Separator line
        line = f"+{'-'*key_col_width}+{'-'*(width - key_col_width - 3)}+"
        print(line)
        # Title row
        title_content = f" \\ {' '*(max_key_len-1)}| {self.title}"
        spaces_needed = width - len(title_content) - 2
        print("|" + title_content + " "*spaces_needed + "|")
        print(line)
        # Options rows
        for key, description in self.options.items():
            padded_key = key.rjust(max_key_len)
            option_content = f" {padded_key} | {description}"
            spaces_needed = width - len(option_content) - 2
            print("|" + option_content + " "*spaces_needed + "|")
        print(line)

    def get_user_choice(self):
        """Prompt user for choice"""
        print("Select an Option")
        print("Enter the Selection Number: ", end="")
        choice = input().strip()
        return choice

    def validate_choice(self, choice):
        """Validate user choice"""
        return choice in self.options

    def execute_actions(self, choice):
        """Execute action for choice"""
        if choice in self.actions:
            action_function = self.actions[choice]
            result = action_function()
            return result
        else:
            print("❗ No action defined for this choice")
            return None

    def run(self):
        """Run menu loop"""
        self.display_menu()
        choice = self.get_user_choice()
        if self.validate_choice(choice):
            result = self.execute_actions(choice)
            return result
        else:
            print("❌ Invalid option! Please try again.")
            return None
