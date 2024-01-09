class PasswordManager:

    def add_password(self):
        ...

    def select_service(self):
        ...

    def generate_password(self):
        ...

    def main(self):
        action = input(
            "Выберите действие:" 
            "\n1.Add\n2.Copy\n3.Change\n4.Generate"
        )
        match action.lower():
            case 'add': self.add_password()
            case 'copy': self.select_service()
            case 'change': self.select_service()
            case 'generate': self.generate_password()


if __name__ == '__main__':
    manager = PasswordManager()
    manager.main()
