import cv2
img = cv2.imread("E:/hnumedical/Compare_4Cdata/test_4C_pic/0.jpg")
#各参数依次是：照片/添加的文字/左上角坐标/字体/字体大小/颜色/字体粗细
print(img)
cv2.putText(img, 'lena', (50,150), cv2.FONT_HERSHEY_COMPLEX, 5, (0, 255, 0), 12)
cv2.imshow("lena", img)
cv2.waitKey()