#!/usr/bin/env python
# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/2/29
@Software: PyCharm
@disc:
======================================="""
import random

import PySimpleGUI as sg
from PIL import Image
import cv2
import io
import imageio
import base64
from core import frame_diffusion


def loadVideo():
    filename = sg.popup_get_file('Filename to gif')
    return filename


def main():
    # ---===--- Get the filename --- #
    skipRate = 3
    gifFps = 10
    videoFile = loadVideo()
    # scale=0.5
    try:
        outFile = videoFile[:-3] + 'gif'
        cap = cv2.VideoCapture(videoFile)
        videoWidth = cap.get(3)
        videoHeight = cap.get(4)
        videoFps = cap.get(5)
        videoTotalFrames = cap.get(7)
        print("video info: [fps:{},total_frame:{}]".format(videoFps, videoTotalFrames))
    except:
        print("cannot play")
        return

    sg.theme('Black')

    # ---===--- define the window layout --- #
    layout = [
        [sg.Text('OpenCV Demo', size=(120, 1), font='Helvetica 20', key='-text-')],
        [
            sg.Image(filename='', key='-image-', size=(600, 400)),
            sg.Image(filename='', key='-new-frame-', size=(600, 400))

        ],
        [sg.Text('End Frame'), sg.Slider(range=(1, videoTotalFrames),
                                         size=(1000, 10), orientation='h', key='-current-frame-')],
        [sg.Text('Video Sample Rate'), sg.Slider(range=(skipRate, 300),
                                                 size=(60, 10), orientation='h', key='-slider-')],
        [sg.Text('Output Gif FPS'), sg.Slider(range=(1, 60),
                                              size=(60, 10), orientation='h', key='-slider2-')],
        [sg.Text('Video Resize Rate'), sg.Slider(range=(1, 10),
                                                 size=(60, 10), orientation='h', key='-slider3-')],
        [sg.Input(key='-prompt-', size=(1000, 10))],
        [
            sg.Button('Start', size=(7, 1), pad=((100, 0), 3), font='Helvetica 14'),
            sg.Button('Restart', size=(7, 1), pad=((100, 0), 3), font='Helvetica 14'),
            sg.Button('Exit', size=(7, 1), pad=((100, 0), 3), font='Helvetica 14'),
            sg.Button('Generate', size=(7, 1), pad=((100, 0), 3), font='Helvetica 14')
        ],
    ]

    # create the window and show it without the plot
    window = sg.Window('Demo Application - video2gif', layout, no_titlebar=False, location=(0, 0), size=(1200, 800),
                       resizable=True)

    # locate the elements we'll be updating. Does the search only 1 time
    image_elem = window['-image-']
    new_frameElem = window['-new-frame-']
    text_elem = window['-text-']
    slider_elem = window['-slider-']
    gifSliderElem = window['-slider2-']
    sizeSliderElem = window['-slider3-']
    currentFrameElem = window['-current-frame-']

    def gui_show_frame(frame):
        try:
            firstFrameDisplay = cv2.resize(frame, (0, 0), fx=1 / 2, fy=1 / 2)
            imgbytes = cv2.imencode('.png', firstFrameDisplay)[1].tobytes()  # ditto
            image_elem.update(data=imgbytes)
        except Exception as e:
            print(e)

    # ---===--- LOOP through video file by frame --- #
    cur_frame = 0
    startProcess = False
    totalFrames = videoTotalFrames
    Seed = random.Random().randint(0, 2 ** 32 - 1)

    while True:
        event, values = window.read(timeout=0)

        current_frame_index = int(values['-current-frame-'])
        skipRate = int(values['-slider-'])
        gifFps = int(values['-slider2-'])
        scale = int(values['-slider3-'])

        if event in ('Generate', None):
            print("要生成了")
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_index)
            ret, org_frame = cap.read()
            # 检查是否成功捕获到了一帧
            if ret:
                # 指定图片保存路径和文件名
                file_name = "saved_frame.jpg"
                # 保存图像
                cv2.imwrite(file_name, org_frame)
                generated_fp = frame_diffusion(file_name, Seed)
                new_frameElem.update(filename=generated_fp)

        if event in ('Start', None):
            startProcess = True
        if event in ('Exit', None):
            break
        if not startProcess:

            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_index)
            ret, org_frame = cap.read()
            gui_show_frame(org_frame)

            slider_elem.update(skipRate)
            gifSliderElem.update(gifFps)
            sizeSliderElem.update(scale)
            framerCounter = 0
            cap.set(cv2.CAP_PROP_POS_FRAMES, framerCounter)
            if current_frame_index != 1:
                totalFrames = current_frame_index
            gif_duration = round((totalFrames / skipRate) / gifFps, 2)
            gifTotalFrames = totalFrames // (skipRate + 1)
            text_elem.update(
                "EST Video[fps:{}, totalFrames:{}] ===> GIF[duration:{} s, totalFrames:{}], Seed:{}".format(videoFps,
                                                                                                            videoTotalFrames,
                                                                                                            gif_duration,
                                                                                                            gifTotalFrames,
                                                                                                            Seed))


        else:
            eta = "strating...."
            text_elem.update(eta)
            with imageio.get_writer(outFile, duration=1 / gifFps, mode='I') as writer:

                while True:
                    event, values = window.read(timeout=0)
                    if framerCounter + 1 > totalFrames and framerCounter + 1 == videoTotalFrames:
                        break
                    if event in ('Restart', None):
                        break
                    cap.set(cv2.CAP_PROP_POS_FRAMES, framerCounter)
                    ret, org_frame = cap.read()
                    if not ret:  # if out of data stop looping
                        break

                    framerCounter += skipRate
                    frame = cv2.resize(org_frame, (0, 0), fx=1 / scale, fy=1 / scale)

                    if False:
                        # 转换OpenCV的图像帧为Pillow Image对象
                        frame_pillow = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                        # 使用Pillow进行无损压缩和保存操作
                        # 注意：GIF格式实际上只支持256色，因此Pillow将采用一种称为dithering的方法来近似颜色
                        # 如果想要减小GIF文件大小，应该考虑降低色彩深度或调整尺寸，而不是压缩品质
                        frame = frame_pillow.convert('P', palette=Image.ADAPTIVE)
                    else:
                        # 压缩图像，75是指定的图像质量
                        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 100]
                        result, img_encode = cv2.imencode('.jpg', frame, encode_param)
                        frame = cv2.imdecode(img_encode, 1)
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    writer.append_data(frame)

                    # 更新界面
                    gui_show_frame(org_frame)
                    eta = "ETA-" + str(round((framerCounter / totalFrames) * 100, 2)) + "%"
                    text_elem.update(eta)
                    slider_elem.update(skipRate)
                    gifSliderElem.update(gifFps)
                    if cv2.waitKey(1) == ord('q'):
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        startProcess = False
                        break
            #
            startProcess = False
    cap.release()


if __name__ == '__main__':
    main()
    # cap = cv2.VideoCapture("/Users/shadikesadamu/Documents/壁纸/视频/已发/2521442.jpeg.mp4")
    # videoWidth = cap.get(3)
    # videoHeight = cap.get(4)
    # videoFps = cap.get(5)
    # videoTotalFrames = cap.get(7)
    # print("video info: [fps:{},total_frame:{}]".format(videoFps, videoTotalFrames))
    # # 随机种子 = 1666545269
    # seed = random.Random().randint(0, 2 ** 32 - 1)
    # print("seed: {}".format(seed))
    # for i in range(videoTotalFrames):
    #     print("frame{}".format(i + 1))
    #     init_images = [
    #         encode_file_to_base64(r"/Users/shadikesadamu/Pictures/vlcsnap-2024-02-29-05h24m21s922.png"),
    #         # encode_file_to_base64(r"B:\path\to\img_2.png"),
    #         # "https://image.can/also/be/a/http/url.png",
    #     ]
    #     batch_size = 1
    #     payload = {
    #         "prompt": "1girl, blue hair",
    #         "seed": 1,
    #         "steps": 20,
    #         "width": 512,
    #         "height": 512,
    #         "denoising_strength": 0.5,
    #         "n_iter": 1,
    #         "init_images": init_images,
    #         "batch_size": batch_size if len(init_images) == 1 else len(init_images),
    #         # "mask": encode_file_to_base64(r"/Users/shadikesadamu/Pictures/img.png")
    #     }
    #     # if len(init_images) > 1 then batch_size should be == len(init_images)
    #     # else if len(init_images) == 1 then batch_size can be any value int >= 1
    #     call_img2img_api(**payload)
