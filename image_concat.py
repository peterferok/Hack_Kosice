import cv2

img1 = cv2.imread('Images/1.png')
img2 = cv2.imread('Images/2.png')
img3 = cv2.imread('Images/3.png')
img4 = cv2.imread('Images/4.png')
img5 = cv2.imread('Images/5.png')
#img6 = cv2.imread('Images/6.png')
im_h1 = cv2.hconcat([img1, img2])
im_h2 = cv2.hconcat([img3, img4])
im_h3 = cv2.hconcat([img5, img5])
im_v = cv2.vconcat([im_h1, im_h2,im_h3])
cv2.imwrite('Concat_images.jpg', im_v)