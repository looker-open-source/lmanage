class LookerFolder(object):
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.children = []
        self.parent = None

    def __repr__(self):
        return f"I am folder {self.id}"

    def add_parent(self, ref):
        self.parent = ref

    def add_child(self, ref):
        self.children.append(ref)


class LookerFolderManager(object):
    def __init__(self):
        self.folders = []

    def __repr__(self) -> str:
        return f"{self.folders}"

    def add_folder(self, ref):
        self.folders.append(ref)

    def create_link(self, folder1, folder2):
        folder1.add_parent(folder2)
        folder2.add_child(folder1)


Tree = LookerFolderManager()
Folder1 = LookerFolder('foo', 1)
Folder2 = LookerFolder('bar', 2)
Tree.add_folder(Folder1)
Tree.add_folder(Folder2)
Tree.create_link(Folder1, Folder2)

print(Tree)

# def recursive_create(root):
#     for folder in root.children:
#         folder.use_api_to_create_self()
#         if folder.children is not None:
#             for child in folder:
#                 return recursive_create(child)
