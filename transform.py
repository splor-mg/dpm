import os


def remove_path_redundancies_res(resource):
    path1 = os.path.normpath(resource.basepath).replace('\\', '/')
    path2 = os.path.normpath(resource.path).replace('\\', '/')
    path1_folders = path1.split('/')
    path2_folders = path2.split('/')
    common_folders = [folder for folder in path1_folders if folder in path2_folders]

    for folder in common_folders:
        path2_folders.remove(folder)

    new_path = os.path.normpath(os.path.join(path1, *path2_folders))

    return new_path


def merge_remove_path_redundancies(path1, path2):
    path1 = os.path.normpath(path1).replace('\\', '/')
    path2 = os.path.normpath(path2).replace('\\', '/')
    path1_folders = path1.split('/')
    path2_folders = path2.split('/')
    common_folders = [folder for folder in path1_folders if folder in path2_folders]

    for folder in common_folders:
        path2_folders.remove(folder)

    new_path = os.path.normpath(os.path.join(path1, *path2_folders))

    return new_path