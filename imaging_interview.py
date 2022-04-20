import os
import time
import logging

import numpy as np
import cv2
import imutils
import shutil

def draw_color_mask(img, borders, color=(0, 0, 0)):
    h = img.shape[0]
    w = img.shape[1]

    x_min = int(borders[0] * w / 100)
    x_max = w - int(borders[2] * w / 100)
    y_min = int(borders[1] * h / 100)
    y_max = h - int(borders[3] * h / 100)

    # -1 will fill the whole area
    img = cv2.rectangle(img, (0, 0), (x_min, h), color, -1)
    img = cv2.rectangle(img, (0, 0), (w, y_min), color, -1)
    img = cv2.rectangle(img, (x_max, 0), (w, h), color, -1)
    img = cv2.rectangle(img, (0, y_max), (w, h), color, -1)

    return img


def preprocess_image_change_detection(img, gaussian_blur_radius_list=None, black_mask=(5, 10, 5, 0)):
    gray = img.copy()
    gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    if gaussian_blur_radius_list is not None:
        for radius in gaussian_blur_radius_list:
            gray = cv2.GaussianBlur(gray, (radius, radius), 0)

    gray = draw_color_mask(gray, black_mask)

    return gray


def compare_frames_change_detection(prev_frame, next_frame, min_contour_area:int):
    # Get the differences
    frame_delta = cv2.absdiff(prev_frame, next_frame)
    # Get the binary image
    # If pixel > 45, 255
    # Else 0
    thresh = cv2.threshold(frame_delta, 45, 255, cv2.THRESH_BINARY)[1]

    thresh = cv2.dilate(thresh, None, iterations=2)
    # CHAIN_APPROX_SIMPLE removes all redundant points and compresses the contour
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    score = 0
    res_cnts = []
    for c in cnts:
        # filter out small contour
        logging.debug(f"contour area: {cv2.contourArea(c)}")
        if cv2.contourArea(c) < min_contour_area:
            continue

        res_cnts.append(c)
        score += cv2.contourArea(c)
    # Visualize contours on the images
    # prev_frame_vis = cv2.drawContours(prev_frame.copy(), res_cnts, -1, (0,255,0), 3)
    # next_frame_vis = cv2.drawContours(next_frame.copy(), res_cnts, -1, (0,255,0), 3)
    # cv2.imwrite("prev_frame.png", prev_frame_vis)
    # cv2.imwrite("next_frame.png", next_frame_vis)
    return score, res_cnts, thresh

def compare(data_folder:str, img1:str, img2:str):
    # compare img1 and img2 in data_folder

    img1_path = os.path.join(data_folder, img1)
    img1_cv2 = cv2.imread(img1_path)
    img1_cv2 = cv2.resize(img1_cv2, (640,480), interpolation = cv2.INTER_AREA)
    gray1 = preprocess_image_change_detection(img1_cv2,gaussian_blur_radius_list=[5,7])

    img2_path = os.path.join(data_folder, img2)
    img2_cv2 = cv2.imread(img2_path)
    img2_cv2 = cv2.resize(img2_cv2, (640,480), interpolation = cv2.INTER_AREA)
    gray2 = preprocess_image_change_detection(img2_cv2,gaussian_blur_radius_list=[5,7])
    
    score, res_cnts, thresh = compare_frames_change_detection(gray1, gray2, min_contour_area=300)
   
    cv2.imwrite("thresh.png", thresh)
    return score

def copy_image(data_folder:str, result_folder:str, img:str):
    # copy image from data folder to result folder
    src = os.path.join(data_folder, img)
    dst = os.path.join(result_folder, img)
    shutil.copyfile(src, dst)

def clean_dataset():
    score_list = {}
    data_folder = "dataset"
    result_folder = "result"

    os.makedirs(result_folder, exist_ok=True)
    images = os.listdir(data_folder)
    
    logging.info(f"images number before cleanling {len(images)}")
    # sort the images based on name
    images.sort()
    l = len(images)
    last = None

    for i,img in enumerate(images):
        logging.info(f"[{i}/{l} {img}]")

        img_path = os.path.join(data_folder, img)
        img_cv2 = cv2.imread(img_path)

        # check if image is valid or if the image size is too small
        if img_cv2 is None or img_cv2.shape[0] < 100:
            logging.warn(f"{img} is not valid")
            continue

        # resize all the images to the same size
        img_cv2 = cv2.resize(img_cv2, (640,480), interpolation = cv2.INTER_AREA)
        gray = preprocess_image_change_detection(img_cv2,gaussian_blur_radius_list=[5,7])

        # For the first image
        if last is None:
            copy_image(data_folder, result_folder, img)
            last = gray.copy()

        score, _, _ = compare_frames_change_detection(gray, last, min_contour_area=300)
        logging.debug(f"score: {score}")

        score_list[img] = score

        if score > 300:
            copy_image(data_folder, result_folder, img)
        last = gray.copy()

    # Store the image name and score for checking
    with open('score.txt', 'w') as f:
        for key, item in score_list.items():
            f.write(f"{key} {item}\n")    

    logging.info(f"images number after cleaning {len(os.listdir(result_folder))}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    start_time = time.time()
    clean_dataset()
    # data_folder = "dataset"

    # img = "c20_2021_03_26__11_29_57.png"
    # r = "c20_2021_03_26__11_35_39.png"

    # # img = "c20_2021_03_25__16_18_36.png"
    # # r = "c20_2021_03_25__16_28_50.png"
    # score = compare(data_folder, img, r)
    # print(score)
    
    logging.info(f"Running time is {time.time()-start_time}")