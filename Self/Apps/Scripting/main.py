import shutil
import os
import sys
import re
import json

def filtiring(target_dir):
    filtered_dirs = []
    for root, dirs, files in os.walk(target_dir):
        for directory in dirs:
            if "game" in directory:
                filtered_dirs.append(os.path.join(root, directory))
    
    return filtered_dirs

def copy_or_overwrite(destination_dir, required_dirs):
    required = []
    for directory in required_dirs:
        remove_game = re.sub(r"([^a-zA-Z0-9]?game[^a-zA-Z0-9]?)", "", os.path.basename(directory))
        if os.path.exists(os.path.join(destination_dir, remove_game)):
            print(f"{remove_game} already exists. Overwriting")
            shutil.rmtree(os.path.join(destination_dir, remove_game))
    
        shutil.copytree(directory, os.path.join(destination_dir, remove_game))
        required.append(remove_game)
    
    return required
    
    
def create_destination_dir(destination):
    if not os.path.exists(destination):
        os.makedirs(destination)
    
    return destination    

def create_json_metadata(destination, required_paths):
    data = {
        "name": required_paths,
        "total": len(required_paths)
    }
    
    with open(destination, "w") as outfile:
        json.dump(data, outfile)

if __name__ == '__main__':
    print("type your source, target[including required dirs] and destination")
    args = sys.argv # without passing any args in the terminal it pass the cwdir as an arg
    if len(args) != 3:
        raise Exception("Invalid number of arguments")
    
    target, destination = args[1:]
    
    required_dirs = filtiring(target)
    
    destination_dir = create_destination_dir(destination)
    
    required = copy_or_overwrite(destination_dir, required_dirs)
    
    json_dest = os.path.join(destination_dir, "metadata.json")
    create_json_metadata(json_dest, required)
   
