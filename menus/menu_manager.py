import traceback


class MenuManager:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    def __init__(self,
                 quick_menu,
                 query_menu,
                 other_menu,
                 load_from_file_menu
                 ):
        self.quick_menu = quick_menu
        self.query_menu = query_menu
        self.other_menu = other_menu
        self.load_from_file_menu = load_from_file_menu
        self.current_menu = "quick"
        self.menu_stack = []
        self.running = True

    def get_current_menu(self):
        if self.current_menu == "quick":
            return self.quick_menu
        elif self.current_menu == "query":
            return self.query_menu
        elif self.current_menu == "other":
            return self.other_menu
        elif self.current_menu == "load_from_file":
            return self.load_from_file_menu
        else:
            return None

    def switch_to(self, menu_name):
        self.menu_stack.append(self.current_menu)
        self.current_menu = menu_name
        print(f"📋 Switched to {self.CYAN}{menu_name}{self.RESET} menu")

    def go_back(self):
        if len(self.menu_stack) > 0:
            self.current_menu = self.menu_stack.pop()
            print("⬅️ Going back...")
        else:
            print("⬅️ No previous menu. Exiting...")
            self.running = False

    def run(self):
        print("🚀 Starting Menu Manager...")
        while self.running:
            try:
                menu = self.get_current_menu()
                if menu is None:
                    print("❌ Error: Invalid menu")
                    break
                result = menu.run()
                if result is None:
                    continue
                elif result == "back":
                    self.go_back()
                elif result == "exit":
                    print("👋 Exiting program...")
                    self.running = False
                elif result.startswith("switch:"):
                    menu_name = result.split(":", 1)[1]
                    self.switch_to(menu_name)
                else:
                    print(f"❗ Unknown result: {result}")
            except KeyboardInterrupt:
                print("\n🛑 Program interrupted by user")
                self.running = False
            except Exception as e:
                traceback.print_exc()
                print(f"❌ Error: {e}")
                self.running = False
        print("\n✅ Menu Manager stopped")
