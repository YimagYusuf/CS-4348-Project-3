import os


class BTreeNode:
    def __init__(self):
        self.id = 0
        self.keys = [0] * 19
        self.values = [0] * 19
        self.children = [0] * 20
        self.parentId = 0
        self.keyCount = 0

class BTree:
    BLOCK_SIZE = 512
    MAGIC = b'4337PRJ3'

    def __init__(self, filename=None):
        self.file = None
        self.rootId = 0 
        self.nextId = 1
        self.filename = filename

    

    def createFile(self, filename):
        self.filename = filename
        
        if os.path.exists(filename):
            
            overwrite = input(f"{filename}' exists do you want to overwrite it? (yes/no): ").strip().lower()
            
            if overwrite != 'yes':
                return
            
        with open(filename, 'wb') as userFile:
            userFile.write(self.MAGIC)
            
            userFile.write(self.intToByte(self.rootId))
            userFile.write(self.intToByte(self.nextId))
            
            userFile.write(b'\x00' * (self.BLOCK_SIZE - 24))
            
        self.openFile(filename)
        print(f"{filename} created and opened.")






    def openFile(self, filename):
        if not os.path.exists(filename):
            print(f"{filename} does not exist.")
            return
        
        self.filename = filename
        with open(filename, 'rb') as userFile:
            magic = userFile.read(8)
            if magic != self.MAGIC:
                print("Error invalid File")
                return
            
        self.file = open(filename, 'r+b')
        
        self.file.seek(8)
        
        self.rootId = self.byteToInt(self.file.read(8))
        self.nextId = self.byteToInt(self.file.read(8))
        
        
        print(f"{filename} opened")



    

    def readNode(self, blockId):
        
        self.file.seek(blockId * self.BLOCK_SIZE)
        
        node = BTreeNode()
        
        node.id = self.byteToInt(self.file.read(8))
        node.parentId = self.byteToInt(self.file.read(8))
        node.keyCount = self.byteToInt(self.file.read(8))
        
        node.keys = []
        for i in range(19):
            key = self.byteToInt(self.file.read(8))
            node.keys.append(key)
            
            
        node.values = []
        for i in range(19):
            value = self.byteToInt(self.file.read(8))
            node.values.append(value)
            
            
        node.children = []
        for i in range(20):
            child = self.byteToInt(self.file.read(8))
            node.children.append(child)
        return node




    def writeNode(self, node):
        
        self.file.seek(node.id * self.BLOCK_SIZE)
        
        self.file.write(self.intToByte(node.id))
        self.file.write(self.intToByte(node.parentId))
        self.file.write(self.intToByte(node.keyCount))
        
        for key in node.keys:
            self.file.write(self.intToByte(key))
            
        for value in node.values:
            self.file.write(self.intToByte(value))
            
        for child in node.children:
            self.file.write(self.intToByte(child))
            
        self.file.flush()





    def insert(self, key, value):
        if not self.file:
            print("Error no file is opened.")
            return
    
    
        if self.rootId != 0:  
            
            root = self.readNode(self.rootId)
            if root.keyCount == 19:  
                
                rootNode = BTreeNode()
                rootNode.id = self.nextId
                self.nextId += 1
                
                
                rootNode.children[0] = root.id
    
                
                middle = 9
                splitNode = BTreeNode()
                splitNode.id = self.nextId
                self.nextId += 1
                splitNode.parentId = rootNode.id
                splitNode.keyCount = middle
    
                
                
                for i in range(middle):
                    splitNode.keys[i] = root.keys[middle + i + 1]
                    splitNode.values[i] = root.values[middle + i + 1]
                
                
                if root.children[0] != 0:
                    for i in range(middle + 1):
                        splitNode.children[i] = root.children[middle + i + 1]

    
                
                root.keyCount = middle
    
                
                rootNode.keys[0] = root.keys[middle]
                rootNode.values[0] = root.values[middle]
                rootNode.children[1] = splitNode.id
                rootNode.keyCount = 1
    
                
                self.writeNode(root)
                self.writeNode(splitNode)
                self.writeNode(rootNode)
    
               
                self.rootId = rootNode.id
                self.file.seek(8)
                self.file.write(self.intToByte(self.rootId))
                self.file.write(self.intToByte(self.nextId))
                self.file.flush()
    
               
                if key > rootNode.keys[0]:
                    self.insertKey(splitNode, key, value)
                else:
                    self.insertKey(root, key, value)
            else:
                self.insertKey(root, key, value)
            print(f"Inserted: {key}, {value}")
            
        else:
            root = BTreeNode()
            root.id = self.nextId
            self.nextId += 1
            root.keys[0] = key
            root.values[0] = value
            root.keyCount = 1
            self.rootId = root.id
            self.writeNode(root)
            self.file.seek(8)
            self.file.write(self.intToByte(self.rootId))
            self.file.write(self.intToByte(self.nextId))
            self.file.flush()
            print(f"Inserted: {key}, {value}")
            



    

    def search(self, key):
        if not self.file:
            print("Error no file is opened")
            return
        current = self.readNode(self.rootId)
        while current:
            found = False
            for i in range(current.keyCount):
                if key == current.keys[i]:
                    print(f"Found {key} = {current.values[i]}")
                    return
                if key < current.keys[i]:
                    childIndex = current.children[i]
                    if childIndex != 0:
                        current = self.readNode(childIndex)
                    else:
                        current = None
                    found = True
                    break
            if not found:
                keyCount = current.keyCount
                if current.children[keyCount] != 0:
                    current = self.readNode(current.children[keyCount])
                else:
                    current = None
        print("Key not found.")



    

    def insertKey(self, node, key, value):
        i = node.keyCount - 1
    
        
        if node.children[0] == 0:
            if node.keyCount == 19:
                print(f"Full Node.")
                return
            
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1
                
            node.keys[i + 1] = key
            node.values[i + 1] = value
            node.keyCount += 1
            self.writeNode(node)
        else:
            
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            child = self.readNode(node.children[i])
            if child.keyCount == 19:
                
                splitNode = BTreeNode()
                splitNode.id = self.nextId
                self.nextId += 1
                splitNode.parentId = node.id
                middle = 9
    
                splitNode.keyCount = middle
                for j in range(middle):
                    splitNode.keys[j] = child.keys[middle + 1 + j]
                    splitNode.values[j] = child.values[middle + 1 + j]
                
                
                if child.children[0] != 0:
                    for j in range(middle + 1):
                        splitNode.children[j] = child.children[middle + 1 + j]

    
                
                child.keyCount = middle
    
                
                for j in range(node.keyCount, i, -1):
                    node.children[j + 1] = node.children[j]
                node.children[i + 1] = splitNode.id
    
                for j in range(node.keyCount - 1, i - 1, -1):
                    node.keys[j + 1] = node.keys[j]
                    node.values[j + 1] = node.values[j]
    
                node.keys[i] = child.keys[middle]
                node.values[i] = child.values[middle]
                node.keyCount += 1
    
                
                self.writeNode(child)
                self.writeNode(splitNode)
                self.writeNode(node)
    
                
                if key > node.keys[i]:
                    child = self.readNode(node.children[i + 1])
    
            
            self.insertKey(child, key, value)
    
    
    
    def printTree(self, blockId=None,):
        
        if blockId is None:
            blockId = self.rootId
            
        if blockId == 0:
            print("Nothing in the Tree")
            return
        
        node = self.readNode(blockId) 
        print(f"Node {blockId}:")
        
        for i in range(node.keyCount):
            print(f"Key = {node.keys[i]}, Val = {node.values[i]}")
    
        for i in range(node.keyCount + 1):
            
            if node.children[i] != 0:
                self.printTree(node.children[i])





    def intToByte(self, value, size=8):
        answer = value.to_bytes(size, 'big')
        return answer





    def byteToInt(self, value):
        answer = int.from_bytes(value, 'big')
        return answer
        
        
    
    
    
    def load(self, filename):
        if not self.file:
            print("Error no files are opened.")
            return
        if not os.path.exists(filename):
            print(f"Error {filename} does not exist.")
            return
        with open(filename, 'r') as loadFile:
            
            for line in loadFile:
                key, value = line.strip().split(",")
                self.insert(int(key), int(value))
                
        print(f"Loaded {filename}")







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
            filename = input("Enter filename to load from: ")
            tree.load(filename)
        elif command == 'quit':
            break
        else:
            print("Command not found, please try again:\n ")

if __name__ == "__main__":
    main()
