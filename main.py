import os
import re

import m3u8
import requests
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from seleniumwire import webdriver
from selenium.webdriver.common.by import By


def get_m3u8_list():
    url = "http://baskino.me/films/boeviki/33055-vymogatelstvo.html"

    driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"))
    driver.get(url)
    driver.find_element(By.CLASS_NAME, "basplayer").click()
    playlist = driver.wait_for_request(".m3u8")

    first_piece_of_url = re.search("(.*)==/", playlist.url).group(1)

    playlist = m3u8.load(playlist.url)

    cleared_file = []
    for link in playlist.segments.uri[:3]:
        cleared_file.append(first_piece_of_url + "==/" + link)

    driver.quit()

    film_name = re.search("-(.*).html", url).group(1)
    tmp_objects = []
    for idx, link in enumerate(cleared_file):
        file_name = f"tmp/tmp{idx}.mp4"

        response = requests.get(link, allow_redirects=True, stream=True)
        with open(file_name, "wb") as file:
            file.write(response.content)
        tmp_objects.append(VideoFileClip(file_name))

    final_clip = concatenate_videoclips(tmp_objects)
    final_clip.write_videofile("films/" + f"{film_name}.mp4")

    tmp_folder = 'tmp'
    for f in os.listdir(tmp_folder):
        os.remove(os.path.join(tmp_folder, f))


if __name__ == "__main__":
    get_m3u8_list()
