import os
import struct
import sys

class BTreeNode:
    def __init__(self):
        self.id = 0
        self.keys = [0] * 19
        self.values = [0] * 19
        self.children = [0] * 20
        self.parentId = 0
        self.keyCount = 0

class BTree:
    blockSize = 512
    magicNumber = b'4337PRJ3'

    def __init__(self, filename=None):
        self.file = None
        self.header = {'magic': self.magicNumber, 'rootId': 0, 'nextId': 1}
        self.filename = filename





    def createFile(self, filename):
        self.filename = filename
        
        if os.path.exists(filename):
            
            overwrite = input(f"{filename}' exists do you want to overwrite? (yes/no): ").strip().lower()
            
            if overwrite != 'yes':
                print("Ended")
                return
            
        with open(filename, 'wb') as f:
            f.write(self.header['magic'])
            
            f.write(self.intToByte(self.header['rootId']))
            f.write(self.intToByte(self.header['nextId']))
            
            f.write(b'\x00' * (self.blockSize - 24))
            
        self.openFile(filename)
        print(f"{filename} created and opened.")






    def openFile(self, filename):
        if not os.path.exists(filename):
            print(f"{filename} does not exist.")
            return
        
        self.filename = filename
        with open(filename, 'rb') as f:
            magic = f.read(8)
            if magic != self.magicNumber:
                print("Error invalid File")
                return
            
        self.file = open(filename, 'r+b')
        
        self.file.seek(8)
        
        self.header['rootId'] = self.byteToInt(self.file.read(8))
        self.header['nextId'] = self.byteToInt(self.file.read(8))
        
        print(f"{filename} opened")

    



    def readNode(self, blockId):
        
        self.file.seek(blockId * self.blockSize)
        
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
        
        self.file.seek(node.id * self.blockSize)
        
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
            print("Error there is no file opened")
            return
        
        if self.header['rootId'] == 0: 
            root = BTreeNode()
            
            root.id = self.header['nextId']
            self.header['nextId'] += 1
            
            root.keys[0] = key
            root.values[0] = value
            
            root.keyCount = 1
            self.header['rootId'] = root.id
            
            self.writeNode(root)
            
            self.file.seek(8)
            
            self.file.write(self.intToByte(self.header['rootId']))
            self.file.write(self.intToByte(self.header['nextId']))
            
            self.file.flush()
            
            print(f"Inserted:{key}, {value}")
        else:
            root = self.readNode(self.header['rootId'])
            self.insertToNode(root, key, value)




    def search(self, key):
        if not self.file:
            print("Error no file opened")
            return
        current = self.readNode(self.header['rootId'])
        while current:
            found = False
            for i in range(current.keyCount):
                if key == current.keys[i]:
                    print(f"{key}, {current.values[i]}")
                    return
            current = None
    
        print("Key not found.")




    def insertToNode(self, node, key, value):
        i = node.keyCount - 1
        while i >= 0 and key < node.keys[i]:
            node.keys[i + 1] = node.keys[i]
            node.values[i + 1] = node.values[i]
            i -= 1
        node.keys[i + 1] = key
        node.values[i + 1] = value
        node.keyCount += 1
        self.writeNode(node)
       




    def intToByte(self, value, size=8):
        answer = value.to_bytes(size, 'big')
        return answer




    def byteToInt(self, value):
        answer = int.from_bytes(value, 'big')
        return answer
        
  

    def printTree(self, blockId=None, level=0):
        if blockId is None:
            blockId = self.header['rootId']
        if blockId == 0:
            print("Tree is empty.")
            return
        node = self.readNode(blockId)
        print(f"{blockId}: Keys={node.keys[:node.keyCount]}")



def main():
    tree = BTree()
    while True:
        command = input("Create, open, insert, search, print, quit\nEnter command: ").lower()
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
        elif command == 'quit':
            break
        else:
            print("Command not found, please try again:\n ")

if __name__ == "__main__":
    main()
