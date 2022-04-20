## What did you learn after looking on our dataset?

There are 1080 images in total. There are 4 cameras, 10, 20, 21, 23. Each camera has a fixed position.
All images end with .png.

One of the timestamp format is cxx_yyyy_mm_dd__hh_mm_ss for example  c20_yyyy_mm_dd__hh_mm_ss.png.

Another format I am not sure what the unit is.

### Images have different sizes, some images are broken, some images have very small sizes.

Because contour area is related to image resolution. And the algorithm can only compare the images with same size.

There are 2 Ways to do it: I choose the first one.

1. First resize all the images to the same size. Reduce resolution -> reduce time

2. Choose the threshold based on image size.

For images that are broken or have very small size. skip them.

## How does you program work?

All the images should be placed in `dataset` folder. The cleaned images would be stored in `result` folder. 

Get all the image names in the `dataset` folder

Sort the image names

For every image, check if the image is valid and the image size, if not valid, skip it.

Resize image to the same size

Compare current image with the last image

Check if the score is larger than score threshold:

If yes, copy the image into result folder

If no, continue

Set the current image as last image

## What values did you decide to use for input parameters and how did you find these values?

I wrote a function compare() to compare an image pair and visulize the contours on image pairs to check the performance with different values.

* gaussian_blur_radius_list

Blurring images can reduce noise. After some experiments, gaussian_blur_radius_list is set to be [5,7].
But blurring can also lead to a problem that if someone with dark clothings appears in the shadow, the algorithm might not be able to tell the differences.

* min_coutourarea

I resized all the images to be 640*480 before comparing.
min_contourarea is set to be 300. For example, there are 2 people on the image c20_2021_03_26__11_35_39.png, but not on image c20_2021_03_26__11_29_57. The smaller contour area of an human is 333. So I set the min_contourarea to be 300 in order to be able to detect the human.

* score

Score is set to be 300.
I also output the image name and its score compared to last image into a file for checking.


## What you would suggest to implement to improve data collection of unique cases in future?

The largest problem for now is how to identify the changes of light and shadow and the changes of verhicles and people. I suggest that we should collect images with a short time interval so that the light and shadow won't change a lot (under the threshold). But clean the data frequently to reduce the data storage. 

Or to check the shape of contour to identify if it is an object or just light and shadow. 

## Any other comments about your solution?

Because my score threshold is set quite low, only around half of the images have been removed.
Original folder: 1080 iamges, after filtering: 532 images.
Run time: 72s for 1080 images.
