import os
import re
import sys
import time
import json
import shutil
import random
import string
import argparse
import requests
import inquirer
import signal
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

headers = {
    'User-Agent': 'TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; en_US) Cronet'
}

headersWm = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

downloaded_video_url = None

def parse_args() -> None:
    signal.signal(signal.SIGINT, lambda signal_number, frame: destroy())
    program = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=100))
    program.add_argument('-v', '--video_url', help='download source video', dest='video_url')

    args = program.parse_args()

    print(args)

    return args



def get_choice():
    questions = [
        inquirer.List('choice',
                      message="Choose a option",
                      choices=["Mass Download (Username)", "Mass Download with (txt)", "Single Download (URL)"],
                      ),
        inquirer.List('type',
                      message="Choose a option",
                      choices=["With Watermark", "Without Watermark"],
                      ),
    ]
    answers = inquirer.prompt(questions)
    print(answers)
    return answers

def get_input(message):
    questions = [
        inquirer.Text('input',
                      message=message,
                      ),
    ]
    answers = inquirer.prompt(questions)
    return answers

def generate_url_profile(username):
    baseUrl = "https://www.tiktok.com/"
    if "@" in username:
        baseUrl = f"{baseUrl}{username}"
    else:
        baseUrl = f"{baseUrl}@{username}"
    return baseUrl

def download_media_from_list(list):
    folder = "./"
    for item in list:
        fileName = f"{item['id']}.mp4"
        downloadFile = requests.get(item['url'], headers=headers)
        with open(folder + fileName, 'wb') as file:
            file.write(downloadFile.content)
            return folder + fileName

def get_video_wm(url):
    idVideo = get_id_video(url)
    API_URL = f"https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={idVideo}"
    request = requests.get(API_URL, headers=headers)
    res = json.loads(request.text)
    urlMedia = res['aweme_list'][0]['video']['download_addr']['url_list'][0]
    data = {
        'url': urlMedia,
        'id': idVideo
    }
    return data

def get_video_no_wm(url):
    idVideo = get_id_video(url)
    API_URL = f"https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={idVideo}"
    request = requests.get(API_URL, headers=headers)
    res = json.loads(request.text)
    urlMedia = res['aweme_list'][0]['video']['play_addr']['url_list'][0]
    data = {
        'url': urlMedia,
        'id': idVideo
    }
    return data

def get_list_video_by_username(username):
    baseUrl = generate_url_profile(username)
    browser = webdriver.Chrome()
    browser.get(baseUrl)
    listVideo = []
    print(f"[*] Getting list video from: {username}")
    loop = True
    while loop:
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        listVideo = [a['href'] for a in soup.select('.tiktok-1s72ajp-DivWrapper > a')]
        print(f"[*] {len(listVideo)} video found")
        previousHeight = browser.execute_script('return document.body.scrollHeight;')
        browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(1)
        newHeight = browser.execute_script('return document.body.scrollHeight;')
        if newHeight == previousHeight:
            print("[X] No more video found")
            print(f"[*] Total video found: {len(listVideo)}")
            loop = False
    browser.quit()
    return listVideo

def get_redirect_url(url):
    if "vm.tiktok.com" in url or "vt.tiktok.com" in url:
        url = requests.get(url, headers=headers, allow_redirects=True).url
        print(f"[*] Redirecting to: {url}")
    return url

def get_id_video(url):
    matching = "/video/" in url
    if not matching:
        print("[X] Error: URL not found")
        sys.exit()
    idVideo = url[url.index("/video/") + 7:]
    return idVideo.split("?")[0] if len(idVideo) > 19 else idVideo

def main():
    args = parse_args()
    print("TikTok Downloader", args.video_url)
    header = "\r\n /$$$$$$$  /$$$$$$$  /$$   /$$  /$$$$$$$  /$$$$$$  /$$   /$$       /$$$$$$$   /$$$$$$  /$$      /$$ /$$   /$$ /$$        /$$$$$$   /$$$$$$  /$$$$$$$  /$$$$$$$$ /$$$$$$$ \r\n|__  $$__/|_  $$_/| $$  /$$/|__  $$__//$$__  $$| $$  /$$/      | $$__  $$ /$$__  $$| $$  /$$ | $$| $$$ | $$| $$       /$$__  $$ /$$__  $$| $$__  $$| $$_____/| $$__  $$\r\n   | $$     | $$  | $$ /$$/    | $$  | $$  \\ $$| $$ /$$/       | $$  \\ $$| $$  \\ $$| $$ /$$$| $$| $$$$| $$| $$      | $$  \\ $$| $$  \\ $$| $$  \\ $$| $$      | $$  \\ $$\r\n   | $$     | $$  | $$$$$/     | $$  | $$  | $$| $$$$$/        | $$  | $$| $$  | $$| $$/$$ $$ $$| $$ $$ $$| $$      | $$  | $$| $$$$$$$/| $$  | $$| $$$$$   | $$$$$$$/\r\n   | $$     | $$  | $$  $$     | $$  | $$  | $$| $$  $$        | $$  | $$| $$  | $$| $$$$_  $$$$| $$  $$$$| $$      | $$  | $$| $$__  $$| $$  | $$| $$__/   | $$__  $$\r\n   | $$     | $$  | $$\\  $$    | $$  | $$  | $$| $$\\  $$       | $$  | $$| $$  | $$| $$$/ \\  $$$| $$\\  $$$| $$      | $$  | $$| $$  \\ $$| $$  | $$| $$      | $$  \\ $$\r\n   | $$    /$$$$$$| $$ \\  $$   | $$  |  $$$$$$/| $$ \\  $$      | $$$$$$$/|  $$$$$$/| $$/   \\  $$| $$ \\  $$| $$$$$$$$|  $$$$$$/| $$  | $$| $$$$$$$/| $$$$$$$/| $$  | $$\r\n|__\/   |______/|__\/  \\__\/   |__\/   \\______/ |__\/  \\__\/      |_______\/  \\______/ |__\/     \\__\/|__\/  \\__\/|________\/ \\______/ |__\/  |__\/|_______\/ |________\/|__\/  |__\/\r\n\n by n0l3r (https://github.com/n0l3r)\n"
    print(header)
    # choice = get_choice()
    choice = {'choice': 'Single Download (URL)', 'type': 'Without Watermark'}
    listVideo = []
    listMedia = []
    if choice['choice'] == "Mass Download (Username)":
        usernameInput = get_input("Enter the username with @ (e.g. @username) : ")
        username = usernameInput['input']
        listVideo = get_list_video_by_username(username)
        if len(listVideo) == 0:
            print(chalk.yellow("[!] Error: No video found"))
            sys.exit()
    elif choice['choice'] == "Mass Download with (txt)":
        urls = []
        # Get URL from file
        fileInput = get_input("Enter the file path : ")
        file = fileInput['input']
        if not os.path.exists(file):
            print("[X] Error: File not found")
            sys.exit()
        # read file line by line
        with open(file, 'r') as f:
            urls = f.readlines()
        urls = [url.strip() for url in urls]
        for url in urls:
            print(f"[*] Found URL: {url}")
            url = get_redirect_url(url)
            listVideo.append(url)
    else:
        # urlInput = get_input("Enter the URL : ")
        # print(urlInput)
        urlInput = {'input': args.video_url}
        url = get_redirect_url(urlInput['input'])
        listVideo.append(url)
    print(f"[!] Found {len(listVideo)} video")
    for i, url in enumerate(listVideo):
        print(f"[*] Downloading video {i+1} of {len(listVideo)}")
        print(f"[*] URL: {url}")
        data = get_video_wm(url) if choice['type'] == "With Watermark" else get_video_no_wm(url)
        listMedia.append(data)
    downloaded_video_url = download_media_from_list(listMedia)
    print("[+] Downloaded successfully", downloaded_video_url)
    return downloaded_video_url

if __name__ == "__main__":
    main()
