#!/usr/bin/env python3

import os
import sys
import json
from urllib.parse import urlparse
from password_generator import PasswordGenerator
import subprocess
import toml
import json
import pathlib
from slugify import slugify
import argparse
import secrets
from passwordgenerator import pwgenerator
from jinja2 import Environment, FileSystemLoader
import base64



parser = argparse.ArgumentParser()
parser.add_argument("--skip-db",action="store_true")
parser.add_argument("--shopify",action="store_true")
parser.add_argument("--skip-system",action="store_true")
args = parser.parse_args()

baseDir = pathlib.Path(__file__).resolve().parent.parent
appDir = os.path.join(baseDir,"esc")
configDir = os.path.join(baseDir,"configs")

#what

env = Environment(loader=FileSystemLoader(configDir))
allowEmpty = ["DJANGO_APPS","DJANGO_CONTEXT_PROCESSORS","DJANGO_MIDDLEWARE"]

tmpdir = pathlib.Path(os.path.join(baseDir,"tmp"))
if not tmpdir.exists():
    tmpdir.mkdir()
    
def writeToFile(contents,fileName):
    with open(fileName,"w") as f:
        f.write(contents)

def generate_password(length):
    """Generate a secure, random password of a given length."""
    characters = string.ascii_letters + string.digits + string.punctuation
    secure_password = ''.join(secrets.choice(characters) for i in range(length))
    return secure_password
    
def getValue(key=None,default=None,label=None,mustBe=[]):
    value = None
    while value is None:
        il = f"{label if label is not None else key} "
        if default is not None and default!="":
            il = f"{il} ({default})"
        inputValue = input(f"{il}: ").replace("\n","").strip()
        if inputValue == "":
            if default is not None and default!="":
                value = default
            elif key in allowEmpty:
                value = inputValue
                break
        elif len(mustBe)>0 and inputValue in mustBe:
            value = inputValue
        else:
            value = inputValue
    return value

def buildShopifyProfile(profile={}):
    info = {
        "SHOPIFY_API_KEY":"API Key",
        "SHOPIFY_API_SECRET":"API Secret",
        "SHOPIFY_TOKEN":"Access token",
        "SHOPIFY_DOMAIN":"Domain",
        "SHOPIFY_API_VERSION":"API Version"
    }
    for key,value in info.items():
        profile[key] = getValue(key,default=profile.get(key),label=value)
    return profile

config = {}    
print("Default Profile")
if args.shopify:
    config = buildShopifyProfile(config)



readFilename = ".env"
if not pathlib.Path(readFilename).exists():
    readFilename = "configs/env-default"
    
for line in open(readFilename).readlines():
    if "=" not in line:
        continue
    line = line.replace("\n","").strip()
    key = line[0:line.index("=")]
    
    value = line[line.index("=")+1:len(line)].strip()
    if key in ["DB_PASSWORD","DJANGO_SECRET"]:
        if value is not None and value!="":
            config[key] = value
        else:
            config[key] = pwgenerator.generate()
    elif key=="FIELD_ENCRYPTION_KEY":
        config[key] = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    else:
        
        config[key] = getValue(key,default=value)
    
    
print("Writing .env")
output = open(".env","w")
for key in config.keys():
    os.environ[key] = config[key]
    print(f"{key}={config[key]}",file=output)
output.close()

if not args.skip_system:

    sysConfigs = {
        "project_root":appDir,
        "wsgi_port":getValue(label="WSGI Port",default="9000"),
        "project_domain":config.get("APP_HOST"),
        "project_slug":  slugify(config.get("APP_NAME")),
        "project_name": config.get("APP_NAME"),
        "project_user":getValue(label="Project User",default="esc"),
        "project_group":getValue(label="Project User group",default="esc"),
        "project_base_class":getValue(label="Project Base Class",default="esc")   
    }
    
    print(sysConfigs)
    
    
    writeToFile(
        env.get_template('nginx.conf').render(sysConfigs),
        f"{tmpdir}/nginx.conf"
    )
    writeToFile(
        env.get_template('systemd.service').render(sysConfigs),
        f"{tmpdir}/{sysConfigs.get('project_slug')}.service"
    )
    writeToFile(
        env.get_template('uwsgi.ini').render(sysConfigs),
        f"{tmpdir}/uwsgi.ini"
    )


if args.skip_db:
    sys.exit()

sqlTmpFile = "/tmp/create-esc-etl.sql"
open(
    sqlTmpFile,
    "w"
).write(
    f""" 
    DROP DATABASE IF EXISTS `{config.get('DB_NAME')}`;
    CREATE DATABASE `{config.get('DB_NAME')}`  DEFAULT CHARSET = utf8mb4 DEFAULT COLLATE = utf8mb4_unicode_ci;; 
    DROP USER IF EXISTS `{config.get('DB_USER')}`@`localhost`;
    create user `{config.get('DB_USER')}`@`localhost` IDENTIFIED BY '{config.get('DB_PASSWORD')}';
    GRANT ALL PRIVILEGES on {config.get('DB_NAME')}.* to `{config.get('DB_USER')}`@`localhost`;
    flush privileges;
""")
os.system(f"sudo mysql < {sqlTmpFile}")
pathlib.Path(sqlTmpFile).unlink()



   
   
    
