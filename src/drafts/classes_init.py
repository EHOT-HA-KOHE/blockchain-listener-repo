class MainFatherClass:
    def __init__(self, test: str):
        print(f'lol - {test}')


class NotMain(MainFatherClass):
    def __init__(self):
        super().__init__('NotMain')


if __name__ == '__main__':
    ex = NotMain()
