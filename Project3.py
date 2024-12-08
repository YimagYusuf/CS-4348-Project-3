class BTreeNode:
    def __init__(self):
        self.id = 0
        self.keys = [0] * 19
        self.values = [0] * 19
        self.children = [0] * 20
        self.parent_id = 0
        self.key_count = 0

class BTree:
    BLOCK_SIZE = 512
    MAGIC = b'4337PRJ3'
    MIN_DEG = 10

    def __init__(self, filename=None):
        self.file = None
        self.header = {'magic': self.MAGIC, 'rootId': 0, 'nextId': 1}
        self.filename = filename
        
        #Need to implement functions, just labeled for now


def main():
    tree = BTree()
    while True:
        command = input("Create, open, insert, search, print, load, extract, quit\nEnter command: ").lower()
        if command == 'create':
            filename = input("Enter filename: ")
            tree.createFile(filename) 
        elif command == 'open':
            filename = input("Enter filename: ")
            tree.openFile(filename)
        elif command == 'insert':
            key = int(input("Enter key: "))
            value = int(input("Enter value: "))
            tree.insert(key, value)
        elif command == 'search':
            key = int(input("Enter key to search: "))
            tree.search(key)
        elif command == 'print':
            tree.printTree()
        elif command == 'load':
            filename = input("Enter filename to load: ")
            tree.load(filename)
        elif command == 'extract':
            filename = input("Enter filename to extract to: ")
            tree.extract(filename)
        elif command == 'quit':
            break
        else:
            print("Command not found, please try again:\n ")

if __name__ == "__main__":
    main()
