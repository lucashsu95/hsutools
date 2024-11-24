# generate_folder_structure_readme.py

import os

def process_path(name:str,directory:str):
    return '/'.join(name.replace(directory,'').replace(' ', '%20').split('\\'))[1:]

def dfs(directory, output, folder_indexes,depth=1,maxDepth=True):
    try:
        ignore_list = ('.git', 'README.md', 'path.md', 'folder_path_readme_generator.py')
        items = list(filter(lambda x: x not in ignore_list, os.listdir(directory)))
        items = sorted(items,key=lambda x: (os.path.isdir(os.path.join(directory, x))),reverse=True)
        folder_index = 0

        for idx,item in enumerate(items,start=1):
            item_path = os.path.join(directory, item)
            space = ' ' * (depth - 1) * 4

            if os.path.isdir(item_path):
                folder_indexes[-1] = str(int(folder_indexes[-1]) + 1)
                print(f"{space}- {'#' * min(depth, 6)} 第{'-'.join(folder_indexes)}章 [{item}]({process_path(item_path,directory)})",file=output)
                if maxDepth == True or depth < maxDepth:
                    dfs(item_path, output,folder_indexes + [str(folder_index)], depth + 1,maxDepth)
            else:
                title = f"{'-'.join(folder_indexes[:-1])}_**{idx:02d}**"
                print(f"{space}- {title} [{item}]({process_path(item_path,directory)})",file=output)

    except OSError:
        print(f"Error reading files in directory: {directory}")

def main(path="."):
    folder_name = os.path.abspath(path)
    os.chdir(folder_name)
    output_file_path = os.path.join(folder_name, 'path.md')

    with open(output_file_path, "w", encoding="utf-8") as output_file:
        maxDepth = input('資料夾最大深度：')
        if(len(maxDepth) > 0):
            maxDepth = int(maxDepth)
        else:
            maxDepth = True

        dfs(folder_name, output_file,['0'],maxDepth=maxDepth)

if __name__ == "__main__":
    main()