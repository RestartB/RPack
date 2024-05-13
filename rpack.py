### rPack ###
# @RestartB #

# Imports
import click
from tqdm import tqdm
import csv
from colorama import Fore, Style
import glob
import json
import requests
import os
import platform
import sys
import string
import random
import shutil

# Directory Manager
def dirMan(install):
    try:
        # Check if we're installing or uninstalling
        if install == True:
            # Set Path Vars
            rpackPath = os.path.expanduser("~/.rpack")
            rpackTempPath = os.path.join(rpackPath, "tmp")
            rpackRepoPath = os.path.join(rpackPath, "repo")
            rpackRepoFilePath = os.path.join(rpackRepoPath, "repolist.csv")

            # Create paths / files where needed
            if os.path.exists(rpackPath) != True:
                os.makedirs(rpackPath)
            
            if os.path.exists(rpackTempPath) != True:
                os.makedirs(os.path.join(rpackPath, "tmp"))
            
            if os.path.exists(rpackRepoPath) != True:
                os.makedirs(os.path.join(rpackPath, "repo"))

            if os.path.exists(rpackRepoFilePath) != True:
                file = open(rpackRepoFilePath, "w")
                file.close()

            # Return our path
            return rpackPath
        else:
            # Remove all paths
            rpackPath = os.path.expanduser("~/.rpack")

            os.rmdir(rpackPath)

            return
    except OSError as error:
        print(f"{Fore.RED}ERROR: OSError has occurred while running dirMan.{Style.RESET_ALL} Aborting, error below:")
        print(error)
        sys.exit()
    except Exception as error:
        print(f"{Fore.RED}ERROR: An error has occurred.{Style.RESET_ALL} Aborting, error below:")
        print(error)
        sys.exit()

# Cleaner
def clean(path, type):
    try:
        print("\nCleaning up...")
        if os.path.exists(path):
            os.remove(path)
        else:
            pass
        return
    except Exception as error:
        print(f"{Fore.RED}ERROR: An error has occurred while cleaning.{Style.RESET_ALL} Aborting, error below:")
        print(error)
        sys.exit()

# Command Group
@click.group()
def commands():
    pass

# Add Repo Command
@commands.command()
@click.argument("target")
def addrepo(target):
    """Adds a repo to rPack."""
    
    fullFilePath = ""
    
    try:
        # Get paths
        print("Loading...")
        rpackPath = dirMan(True)

        # Are we provided with a valid JSON?
        if target.split("/")[-1].endswith(".json"):
            print("Finding repo...\n")

            # Generate Filename
            letters = string.ascii_lowercase
            filename = f"{''.join(random.choice(letters) for i in range(8))}.json"
            
            fullFilePath = f"{rpackPath}/tmp/{filename}"

            # Get repo
            response = requests.get(target, stream = True)
            sizeBytes = int(response.headers.get('content-length', 0))
            progress = tqdm(total = sizeBytes, unit = 'B', unit_scale = True)

            with open(fullFilePath, "wb") as file:
                for data in response.iter_content(chunk_size = 1024):
                    file.write(data)
                    progress.update(len(data))
                    
                file.close()
                progress.close()

            # Repo info
            with open(fullFilePath, "r") as repoFile:
                repoData = json.load(repoFile)
                print(f"{repoData['repo-name']} - {repoData['repo-author']}\n- Web Address: {target}\n- Packages: {len(repoData['packages'])}\n")
                repoFile.close()

            # Add repo to CSV and repo folder
            if input("Add repo? (y/n) ").lower() == "y":
                shutil.move(fullFilePath, f"{rpackPath}/repo/{filename}")
                
                repoListFile = open(f"{rpackPath}/repo/repolist.csv", "r")
                repoList = csv.reader(repoListFile, delimiter=",", quotechar='"')
                repoList = list(repoList)
                repoListFile.close()
                
                repoListFile = open(f"{rpackPath}/repo/repolist.csv", "w")
                repoListWriter = csv.writer(repoListFile, delimiter=",", quotechar='"')

                for row in repoList:
                    if row != []:
                        if row[0] != target:
                            repoListWriter.writerow(row)
                
                repoListWriter.writerow([f"{target}", f"{filename}"])
                repoListFile.close()
        
                print("\nAdded repo!")
                sys.exit()
            else:
                print("Cleaning up...")
                os.remove(fullFilePath)
                print("Aborting...")
                sys.exit()
        else:
            print(f"{Fore.RED}ERROR: not a JSON file! Aborting.{Style.RESET_ALL}")
    except Exception as error:
        print(f"{Fore.RED}ERROR: An error has occurred.{Style.RESET_ALL} Aborting, error below:")
        print(error)
        clean(fullFilePath, "repo")
        sys.exit()

# Remove Repo command
@commands.command()
@click.argument("target")
def removerepo(target):
    """Remove a repo from rPack."""
    
    try:
        print("Loading...\n")
        rpackPath = dirMan(True)

        repoListFile = open(f"{rpackPath}/repo/repolist.csv", "r")
        repoList = csv.reader(repoListFile, delimiter=",", quotechar='"')
        repoList = list(repoList)
        repoListFile.close()
        
        for repo in repoList:
            if repo != []:
                if repo[0] == target:
                    filename = f"{rpackPath}/repo/{repo[1]}"
                    
                    with open(filename, "r") as repoFile:
                        repoData = json.load(repoFile)

                        print("Found repo to delete:")
                        try:
                            print(f"{repoData['repo-name']} - {repoData['repo-author']}\n- Web Address: {repo[0]}\n- Local Filename: {repo[1]}\n- Packages: {len(repoData['packages'])}\n")
                        except KeyError:
                            print(f"{Fore.RED}Repo has corrupted or missing metadata!{Style.RESET_ALL}")

                        repoPath = f"{rpackPath}/repo/{repo[1]}"
                        repoFile.close()

                    if input(f"{Fore.RED}Are you sure?{Style.RESET_ALL} (y/n) ").lower() == "y":
                        print("\nDeleting...")
                        
                        repoListFile = open(f"{rpackPath}/repo/repolist.csv", "w")
                        repoListWriter = csv.writer(repoListFile, delimiter=",", quotechar='"')

                        for row in repoList:
                            if row != []:
                                if row[0] != target:
                                    repoListWriter.writerow(row)
                        
                        repoListFile.close()
                        
                        os.remove(repoPath)

                        print(f"{Fore.GREEN}Deleted!{Style.RESET_ALL}")
                        sys.exit()
                else:
                    pass
        
        print("Repo not found.")
    except Exception as error:
        print(f"{Fore.RED}ERROR: An error has occurred.{Style.RESET_ALL} Aborting, error below:")
        print(error)
        sys.exit()

# View Repos command
@commands.command()
@click.option('--pretty/--compact', default=False, help='display repo info in a prettier format')
def viewrepos(pretty):
    """View repos added to rPack."""
    
    try:
        print("Loading...\n")
        rpackPath = dirMan(True)
        
        repoListFile = open(f"{rpackPath}/repo/repolist.csv", "r")
        repoList = csv.reader(repoListFile, delimiter=",", quotechar='"')
        repoList = list(repoList)

        i = 0
        
        for repo in repoList:
            if repo != []:
                i += 1
                filename = f"{rpackPath}/repo/{repo[1]}"
                
                with open(filename, "r") as repoFile:
                    repoData = json.load(repoFile)

                    if pretty == False:
                        print(f"{i}: {repoData['repo-name']} (by {repoData['repo-author']}) ({len(repoData['packages'])} packages) - {repo[0]} ({repo[1]})")
                    else:
                        print(f"{i}: {repoData['repo-name']} - {repoData['repo-author']}\n- Web Address: {repo[0]}\n- Local Filename: {repo[1]}\n- Packages: {len(repoData['packages'])}\n")

                    repoFile.close()
    except Exception as error:
        print(f"{Fore.RED}ERROR: An error has occurred.{Style.RESET_ALL} Aborting, error below:")
        print(error)
        sys.exit()

# Sync Repos command
@commands.command()
def sync():
    """Sync the rPack repo cache."""
    
    fullFilePath = ""
    
    try:
        print("Loading...")
        rpackPath = dirMan(True)

        print("Finding repos...")
        
        global repoList
        global repo

        repoListFile = open(f"{rpackPath}/repo/repolist.csv", "r")
        repoList = csv.reader(repoListFile, delimiter=",", quotechar='"')
        repoList = list(repoList)
        
        print(f"{Fore.GREEN}Found {len(repoList)} repos.{Style.RESET_ALL}")
        print(f"\nDownloading package lists...")
        
        i = 0
        for repo in repoList:
            if repo != []:
                i += 1
                
                print(f"\nFetch {i}: {repo[0]}")
                for item in repoList:
                    if item != []:
                        if item[0] == repo[0]:
                            filename = item[1]
                            fullFilePath = f"{rpackPath}/repo/{filename}"
                            
                            response = requests.get(repo[0], stream = True)
                            sizeBytes = int(response.headers.get('content-length', 0))
                            progress = tqdm(total = sizeBytes, unit = 'B', unit_scale = True)
                            
                            with open(fullFilePath, "wb") as file:
                                for data in response.iter_content(chunk_size = 1024):
                                    file.write(data)
                                    progress.update(len(data))
                                    
                                file.close()
                                progress.close()
                        else:
                            pass
        
        print(f"\n{Fore.GREEN}Package lists synced.{Style.RESET_ALL}")
    except Exception as error:
        print(f"{Fore.RED}ERROR: An error has occurred.{Style.RESET_ALL} Aborting, error below:")
        print(error)
        clean(fullFilePath, "repo")
        sys.exit()

# Install Package command
@commands.command()
@click.argument("target")
def install(target):
    """Install a package."""

    fullFilePath = ""
    
    try:
        print("Loading...")
        rpackPath = dirMan(True)

        print(f"Searching for package: {target}...")

        repos = glob.glob(f"{rpackPath}/repo/*.json")

        for currentRepo in repos:
            try:
                repoFile = open(currentRepo, "r")
                repo = json.load(repoFile)
                for package in repo['packages']:
                    if package == target:
                        osStr = ""
                        archStr = ""
                        myOS = sys.platform
                        myArch = platform.machine()

                        # OS String Gen
                        for repoOS in repo['packages'][package]:
                            if repoOS != "info":
                                if osStr == "":
                                    osStr = repoOS
                                else:
                                    osStr += f", {repoOS}"
                        
                        # Arch String Gen
                        for arch in repo['packages'][package][myOS]:
                            if archStr == "":
                                archStr = arch
                            else:
                                archStr += f", {arch}"
                        
                        # OS Check
                        try:
                            repo['packages'][package][myOS]
                        except KeyError:
                            print(f"{Fore.RED}Target OS ({myOS}) not available in this package! ({osStr} available) Aborting...")
                            sys.exit()
                        
                        # Arch Check
                        try:
                            repo['packages'][package][myOS][myArch]
                        except KeyError:
                            print(f"{Fore.RED}Target architecture ({myArch}) not available in this package! ({archStr} available) Aborting...")
                            sys.exit()
                        
                        # Package Info
                        print(f"\n{Fore.GREEN}Package found!{Style.RESET_ALL}\n")
                        print(f"Name: {repo['packages'][package]["info"]['fullName']}")
                        print(f"Description: {repo['packages'][package]["info"]['description']}")
                        print(f"Author: {repo['packages'][package]["info"]['author']}")
                        print(f"Version: {repo['packages'][package]['info']['latest']}")
                        print(f"Repo: {repo['repo-name']}")
                        latest = repo['packages'][package]['info']['latest']
                        
                        # Allow package install if latest version is available for us
                        if repo['packages'][package]['info']['latest'] in repo['packages'][package][myOS][myArch]:
                            if input("\nInstall package? (y/n) ").lower() == "y":
                                print("\nStarting download.")

                                url = repo['packages'][package][myOS][myArch][latest]['sourceURL']
                                
                                response = requests.get(url, stream = True)
                                sizeBytes = int(response.headers.get('content-length', 0))
                                progress = tqdm(total = sizeBytes, unit = 'B', unit_scale = True)

                                filename = url.split("/")[-1]
                                fullFilePath = f"{rpackPath}/tmp/{filename}"

                                with open(fullFilePath, "wb") as file:
                                    for data in response.iter_content(chunk_size = 1024):
                                        file.write(data)
                                        progress.update(len(data))
                                
                                    file.close()
                                    progress.close()
                                
                                print(f"{Fore.GREEN}Package downloaded.{Style.RESET_ALL}")
                                print("\nStarting install.\n")

                                os.system(repo['packages'][package][myOS][myArch][latest]['installCommand'].replace("{FILE}", os.path.normpath(fullFilePath)))
                                print(f"{Fore.GREEN}Package installed!{Style.RESET_ALL}")
                                repoFile.close()
                                clean(fullFilePath, "package")
                                sys.exit()
                            else:
                                print("Aborting.")
                                repoFile.close()
                                sys.exit()
                        else:
                            print(f"\n{Fore.RED}ERROR: Latest version (v{repo['packages'][package]['info']['latest']}) is not in {currentRepo}! Please select an available version.{Style.RESET_ALL} Aborting.")
                            sys.exit()
                    else:
                        pass
                repoFile.close()
            except KeyError:
                print(f"{Fore.RED}ERROR: {currentRepo} has corrupt metadata!{Style.RESET_ALL} Aborting.")
                clean(fullFilePath, "package")
                sys.exit()
        print("Package not found.")
    except KeyboardInterrupt:
        clean(fullFilePath, "package")
        sys.exit()
    except Exception as error:
        print(f"{Fore.RED}ERROR: An error has occurred.{Style.RESET_ALL} Aborting, error below:")
        print(error)
        clean(fullFilePath, "package")
        sys.exit()

# Search for Package command
@commands.command()
def search(target):
    """(not implemented) Search for a package."""

    print("Sorry, not implemented yet!")

# View all Packages command
@commands.command()
def viewpacks():
    """(not implemented) View all available packages."""

    try:
        rpackPath = dirMan(True)
        
        repos = glob.glob(f"{rpackPath}/repo/*.json")

        for currentRepo in repos:
            repoFile = open(currentRepo, "r")
            repo = json.load(repoFile)

            for package in repo['packages']:
                id = package
                name = repo['packages'][package]['fullName']
                description = repo['packages'][package]['description']
                author = repo['packages'][package]['author']
                latest = repo['packages'][package]['latest']
    except Exception as error:
        print(f"{Fore.RED}ERROR: An error has occurred.{Style.RESET_ALL} Aborting, error below:")
        print(error)
        sys.exit()

# Path command
@commands.command()
def path():
    """View rPack data path."""
    
    print(dirMan(True))
    sys.exit()

commands()