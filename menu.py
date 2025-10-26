#!/usr/bin/env python3


class Menu:
    def __init__(self, title, options, actions):
        self.title = title
        self.options = options
        self.actions = actions

    def get_max_option_length(self):
        if not self.options:
            return 0
        return max(len(desc) for desc in self.options.values())

    def get_box_width(self):
        max_option = self.get_max_option_length()
        title_length = len(self.title)
        max_content = max(max_option, title_length)
        return 46

    def display_menu(self):
        width = self.get_box_width()
        desc_width = width - 6
        line = "+" + "-"*3 + "+" + "-"*desc_width + "+"
        print(line)
        title_content = f" \\ | {self.title}"
        spaces_needed = width - len(f" \\ | {self.title}") - 2
        spaces_needed = width - len(title_content) - 2
        print("|" + title_content + " "*spaces_needed + "|")
        print(line)
        for key, description in self.options.items():
            option_content = f" {key} | {description}"
            spaces_needed = width - len(option_content) - 2
            print("|" + option_content + " "*spaces_needed + "|")
        print(line)

    def get_user_choice(self):
        print("Select an Option")
        print("Enter the Selection Number: ", end="")
        choice = input().strip()
        return choice

    def validate_choice(self, choice):
        if choice in self.options:
            return True
        else:
            return False

    def execute_actions(self, choice):
        if choice in self.actions:
            action_function = self.actions[choice]
            result = action_function()
            return result
        else:
            print("⚠️ No action defined for this choice")
            return None

    def run(self):
        self.display_menu()
        choice = self.get_user_choice()
        if self.validate_choice(choice):
            result = self.execute_actions(choice)
            return result
        else:
            print("❌ Invalid option! Please try again.")
            return None
