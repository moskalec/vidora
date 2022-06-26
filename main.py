import os
import re
from time import time

import aiofiles
import m3u8
import requests
import asyncio
import aiohttp
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from seleniumwire import webdriver
from selenium.webdriver.common.by import By

# def get_m3u8_list():
#     url = "http://baskino.me/films/boeviki/33055-vymogatelstvo.html"
#
#     driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"))
#     driver.get(url)
#     driver.find_element(By.CLASS_NAME, "basplayer").click()
#     playlist = driver.wait_for_request(".m3u8")
#
#     first_piece_of_url = re.search("(.*)==/", playlist.url).group(1)
#
#     playlist = m3u8.load(playlist.url)
#
#     cleared_file = []
#     for link in playlist.segments.uri[:3]:
#         cleared_file.append(first_piece_of_url + "==/" + link)
#
#     driver.quit()
#
#     film_name = re.search("-(.*).html", url).group(1)
#     tmp_objects = []
#     for idx, link in enumerate(cleared_file):
#         file_name = f"tmp/tmp{idx}.mp4"
#
#         response = requests.get(link, allow_redirects=True, stream=True)
#         with open(file_name, "wb") as file:
#             file.write(response.content)
#         tmp_objects.append(VideoFileClip(file_name))
#
    # final_clip = concatenate_videoclips(tmp_objects)
    # final_clip.write_videofile("films/" + f"{film_name}.mp4")
    #
    # tmp_folder = 'tmp'
    # for f in os.listdir(tmp_folder):
    #     os.remove(os.path.join(tmp_folder, f))

###########################


tasks = []
tmp_frames = []
tasks_write = []


def clear_tmp_folder():
    tmp_folder = 'tmp'
    for f in os.listdir(tmp_folder):
        os.remove(os.path.join(tmp_folder, f))


def concatenate_frames(frames_list, film_name):
    final_clip = concatenate_videoclips(frames_list)
    final_clip.write_videofile("films/" + f"{film_name}.mp4")

    clear_tmp_folder()


def get_frames_links(url):
    driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"))
    driver.get(url)
    driver.find_element(By.CLASS_NAME, "basplayer").click()
    playlist = driver.wait_for_request(".m3u8")

    first_piece_of_url = re.search("(.*)==/", playlist.url).group(1)

    playlist = m3u8.load(playlist.url)

    frames_links = []
    for link in playlist.segments.uri[:3]:
        frames_links.append(first_piece_of_url + "==/./" + link)

    driver.quit()

    return frames_links


def write_frame(data, name):
    with open('tmp/' + str(name) + '.mp4', 'wb') as file:
        print('...writing...')
        file.write(data)
        tmp_frames.append(VideoFileClip('tmp/'+str(name) + '.mp4'))


async def fetch_content(url, session, filename):
    async with session.get(url, allow_redirects=True) as response:
        print('downloading...')
        data = await response.read()
        print('saving...')
        write_frame(data, filename)  # TODO: remove blocking here


async def main(url):
    links = get_frames_links(url)

    async with aiohttp.ClientSession(trust_env=True) as session:
        for idx, frame_url in enumerate(links):
            task = asyncio.create_task(fetch_content(url=frame_url, session=session, filename=idx))
            tasks.append(task)
            print('task created')

        await asyncio.gather(*tasks)
        print('...gather tasks downloading...')


if __name__ == "__main__":
    url = "http://baskino.me/films/boeviki/33055-vymogatelstvo.html"

    t0 = time()
    asyncio.run(main(url))
    print(time() - t0)

    film_name = re.search("-(.*).html", url).group(1)
    final_clip = concatenate_videoclips(tmp_frames)
    final_clip.write_videofile("films/" + f"{film_name}.mp4")

    tmp_folder = 'tmp'
    for f in os.listdir(tmp_folder):
        os.remove(os.path.join(tmp_folder, f))