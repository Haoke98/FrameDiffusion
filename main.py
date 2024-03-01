#!/usr/bin/env python
# _*_ codign:utf8 _*_
"""====================================
@Author:Sadam·Sadik
@Email：1903249375@qq.com
@Date：2024/2/29
@Software: PyCharm
@disc:
======================================="""
import os

import cv2
import gradio as gr
import numpy as np
from moviepy.editor import VideoClip
from PIL import Image
from core.hash import get_combined_hash

# global variable definition:
webui_server_url = 'http://218.31.113.195:57860'
out_dir = 'api_out'
out_dir_i2i = os.path.join(out_dir, 'img2img')
videoWidth = 1920
videoHeight = 1080
videoFPS = 30


def get_fp(frame_img_fp, params):
    hash_value = get_combined_hash(frame_img_fp, params)
    save_fp = os.path.join(out_dir_i2i, f'{hash_value}.png')
    return save_fp


def frame_to_video_clip(frame_path):
    # 读取图片
    frame = np.asarray(Image.open(frame_path))
    # 将图片转换为 VideoClip 对象
    clip = VideoClip(frame, duration=1 / 25)
    return clip


def frames_to_video(frame_paths, output_path, fps):
    # 创建一个 VideoClip 对象，将所有 frame 连接起来
    clip = VideoClip([frame_to_video_clip(frame_path) for frame_path in frame_paths], concat=True)
    # 设置视频的帧率
    clip = clip.set_fps(fps)
    # 保存视频为 MP4 文件
    clip.write_videofile(output_path)


def generate_video(frames: list[slice]):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    """
    参数2 VideoWriter_fourcc为视频编解码器
    fourcc意为四字符代码（Four-Character Codes），顾名思义，该编码由四个字符组成,下面是VideoWriter_fourcc对象一些常用的参数,注意：字符顺序不能弄混
    cv2.VideoWriter_fourcc('I', '4', '2', '0'),该参数是YUV编码类型，文件名后缀为.avi 
    cv2.VideoWriter_fourcc('P', 'I', 'M', 'I'),该参数是MPEG-1编码类型，文件名后缀为.avi 
    cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'),该参数是MPEG-4编码类型，文件名后缀为.avi 
    cv2.VideoWriter_fourcc('T', 'H', 'E', 'O'),该参数是Ogg Vorbis,文件名后缀为.ogv 
    cv2.VideoWriter_fourcc('F', 'L', 'V', '1'),该参数是Flash视频，文件名后缀为.flv
    cv2.VideoWriter_fourcc('m', 'p', '4', 'v')    文件名后缀为.mp4
    """
    generated_video_fp = "generated_video.mp4"
    print(f"Generate params:[fps:{videoFPS}, width:{videoWidth}, height:{videoHeight}, fourcc:{fourcc}]", )
    video = cv2.VideoWriter(generated_video_fp, fourcc, int(videoFPS),
                            (int(videoWidth), int(videoHeight)))  # 创建视频流对象-格式一

    # frame_paths = []
    for i, frame in enumerate(frames):
        frame_fp, flag = frame
        # print(i, frame_fp, flag)
        image = cv2.imread(frame_fp)
        video.write(image)
        print(i, flag)
    # frames_to_video(frame_paths, generated_video_fp, videoFPS)
    return generated_video_fp


def on_frame_selected(evt: gr.SelectData, frames: list[slice], seed: int, prompt: str):
    print(f"OnFrameSelected:[{evt.index} from {evt.target}, Seed:{seed}]")
    print(evt.value)
    """
    {
        'image': {
            'path': '/private/var/folders/by/gmwsqd_x01q02gssqxb8ry140000gn/T/gradio/b5b7c1932bd4383da5e747ad11f5c39399222c33/image.png', 
            'url': 'http://127.0.0.1:7860/file=/private/var/folders/by/gmwsqd_x01q02gssqxb8ry140000gn/T/gradio/b5b7c1932bd4383da5e747ad11f5c39399222c33/image.png', 
            'size': None, 
            'orig_name': None,
            'mime_type': None,
            'is_stream': False
        },
        'caption': 'frame33'
    }
    """
    res = []
    for i, frame in enumerate(frames):
        frame_fp, flag = frame
        # print(i, frame_fp, flag)
        if i == evt.index:
            res.append(["api_out/img2img/2ffc5feecb71e7ada52357c330d0b1a7d6b677fbdf2fe6fe71789dadb6366d7c.png", flag])
        else:
            res.append([frame_fp, flag])
    #
    file_name = "saved_frame.jpg"
    # 保存图像
    # cv2.imwrite(file_name, org_frame)
    params = {
        "prompt": prompt,
        "seed": seed,
        "steps": 20,
        "width": videoWidth,
        "height": videoHeight,
        "denoising_strength": 0.5,
        "n_iter": 1,
    }
    # save_fp = get_fp(file_name, params)
    # if os.path.exists(save_fp):
    #   # 更新GUI上的画面
    #   new_frameElem.update(filename=save_fp, size=(1200, 400))
    # else:
    #     q.put([file_name, params])
    # generated_fp = frame_diffusion(file_name, params)
    # print("已经处理好了:", file_name, params, generated_fp)
    return res


def on_input_video_change(input_video_fp):
    global videoWidth, videoHeight, videoFPS
    # /private/var/folders/by/gmwsqd_x01q02gssqxb8ry140000gn/T/gradio/51b4179c3e0c8063abb954c87fe139a3a1bec014/2521442.jpeg.mp4
    print("on_input_video_change:", input_video_fp)
    cap = cv2.VideoCapture(input_video_fp)
    videoWidth = cap.get(3)
    videoHeight = cap.get(4)
    videoFPS = cap.get(5)
    videoTotalFrames = int(cap.get(7))
    print("video info: [fps:{},total_frame:{}]".format(videoFPS, videoTotalFrames))
    print("frameSlider.maximum:", seedSlider.maximum)
    frames = []
    for frame_index in range(videoTotalFrames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, org_frame = cap.read()
        print("On Input Video processing: frame{}, {:.2f}%".format(frame_index, frame_index / videoTotalFrames * 100))
        if ret:
            # 转换为 RGB 颜色格式
            rgb_frame = cv2.cvtColor(org_frame, cv2.COLOR_BGR2RGB)
            # 将 OpenCV 帧转换为 numpy.ndarray
            frame_ndarray = np.asarray(rgb_frame)
            frames.append([frame_ndarray, "frame{}".format(frame_index)])
    # 释放Video
    cap.release()
    info = f'''
    ## Video Info
    * Frame: {videoWidth}x{videoHeight}
    * Fps: {videoFPS} Frame Count:{videoTotalFrames} Duration: {videoTotalFrames / videoFPS}s
    '''
    return frames, info
    # print("video frames num:", input_v.get_num_frames())


with gr.Blocks(js="extensions/js-extension.js") as demo:
    gr.State()
    # with gr.Row():
    #     with gr.Column(scale=1):
    #
    #     with gr.Column(scale=3):
    gr.Markdown(
        '''
        # Frame Diffusion
        Start typing below and then click **Run** to see the output.
        '''
    )
    with gr.Row():
        with gr.Column(scale=1):
            inputVideoView = gr.Video(label="InputVideo", height=480)
            videoInfoView = gr.Markdown(
                '''
                ## Video Info
                '''
            )
            promptElem = gr.Text(label="prompt", interactive=True, lines=3, value="1girl, blue hair")
            seedSlider = gr.Slider(label="Seed", elem_id="frameSlider", randomize=True, minimum=1, maximum=3290305185)
            progress = gr.Progress()
            btn = gr.Button("Start Generation", interactive=True)
        with gr.Column(scale=3):
            with gr.Tab("Generated Frames"):
                with gr.Row():
                    originalFrameGallery = gr.Gallery(label="Original Frames", columns=6, height=400, interactive=False)
                with gr.Row():
                    generatedFrameGallery = gr.Gallery(label="Generated Frames", columns=6, height=400,
                                                       interactive=False)
            with gr.Tab("Generated Video"):
                out = gr.Video(label="Out", show_download_button=True, height=760)

    # with gr.Row():
    #     with gr.Column(scale=1):
    #         frameCountView = gr.Number(label="Frame Count", interactive=False, elem_id="frameCount")
    #         gr.Markdown("Video Info:\nwidth:200px\nheight:300px")
    #     gr.Image(value="api_out/img2img/img2img-20240229-172125-0.png", interactive=True)
    #     # with gr.Column(scale=2):
    # with gr.Row():
    #     gr.Gallery(
    #         value=["api_out/img2img/img2img-20240229-172054-0.png", "api_out/img2img/img2img-20240229-171824-0.png"])

    # 开始绑定事件
    inputVideoView.change(on_input_video_change, inputs=[inputVideoView], outputs=[originalFrameGallery, videoInfoView])
    originalFrameGallery.select(on_frame_selected, inputs=[originalFrameGallery, seedSlider, promptElem],
                                outputs=[generatedFrameGallery])
    btn.click(fn=generate_video, inputs=[generatedFrameGallery], outputs=out)

if __name__ == '__main__':
    demo.launch()
