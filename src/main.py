from textnode import *
from htmlnode import *
from markdown_to_node import *

import sys
import os
import shutil

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}.")

    markdown = ""
    with open(from_path, 'r', encoding="utf-8") as f:
        markdown = f.read()

    template = ""
    with open(template_path, 'r', encoding="utf-8") as f:
        template = f.read()

    html_string = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)

    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", html_string)

    with open(dest_path, 'w', encoding="utf-8") as f:
        f.write(template)

def copy_to(source, destination):
    if not os.path.exists(source):
        raise Exception(f"{source} directory does not exist")
    if os.path.exists(destination):
        shutil.rmtree(destination)

    copy_recursion(source, destination)

def copy_recursion(source, destination):
    if os.path.isdir(source):
        print(f"made dir at {destination}")
        os.mkdir(destination)

        for file in os.listdir(source):
            copy_recursion(source + "/" + file, destination + "/" + file)
    else:
        print(f"made file at {destination}")
        shutil.copy(source, destination)

def generate_pages_recursive(dir_path, template_path, dest_path):
    if os.path.isdir(dir_path):

        if not os.path.exists(dest_path):
            print(f"made dir at {dest_path}")
            os.mkdir(dest_path)

        for file in os.listdir(dir_path):
            if os.path.isdir(dir_path + "/" + file):
                generate_pages_recursive(dir_path + "/" + file, template_path, dest_path + "/" + file)
            elif os.path.isfile(dir_path + "/" + file):
                if file[-3:] == ".md":
                    generate_page(dir_path + "/" + file, template_path, dest_path + "/" + file[:-3] + ".html")

def main():
    copy_to("./static", "./public")
    generate_pages_recursive("./content", "./template.html", "./public")

main()