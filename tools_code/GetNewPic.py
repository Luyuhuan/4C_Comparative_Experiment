import os
import shutil
def get_img_file(file_name):
    imagelist = []
    for parent, dirnames, filenames in os.walk(file_name):
        for filename in filenames:
            if filename.lower().endswith(
                    ('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff')):
                imagelist.append(os.path.join(parent, filename))
        return imagelist
def copy_image(srcpath,respath,count,orgpic):
    num = 0
    for parent, dirnames, filenames in os.walk(srcpath):
        for filename in filenames:
            if filename.lower().endswith(
                    ('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff')) and filename not in orgpic:
                shutil.copy(srcpath + filename, respath + filename)
                num = num + 1
            if num == count:
                return 0

trainpicpath = 'E:/hnumedical/4C_ABP/train/'
testpicpath = 'E:/hnumedical/4C_ABP/test/'
Orgpic = get_img_file(trainpicpath)+get_img_file(testpicpath)
Srcpath = 'E:/hnumedical/Data/Pic_Data/HuangGet_4C/'
Respath = 'E:/hnumedical/4C_ABP/new/'
copy_image(Srcpath+'心底四腔心切面_std/',Respath+'心底四腔心切面_std/',300,Orgpic)
copy_image(Srcpath+'心底四腔心切面_nstd/',Respath+'心底四腔心切面_nstd/',100,Orgpic)
copy_image(Srcpath+'心尖四腔心切面_std/',Respath+'心尖四腔心切面_std/',300,Orgpic)
copy_image(Srcpath+'心尖四腔心切面_nstd/',Respath+'心尖四腔心切面_nstd/',100,Orgpic)
copy_image(Srcpath+'胸骨旁四腔心切面_std/',Respath+'胸骨旁四腔心切面_std/',300,Orgpic)
copy_image(Srcpath+'胸骨旁四腔心切面_nstd/',Respath+'胸骨旁四腔心切面_nstd/',100,Orgpic)