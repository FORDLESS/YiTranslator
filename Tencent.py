from PIL import Image

image = Image.open(r'G:\PythonProject\gamerOCR\res\text_bg.png')

# 将图像转换为RGBA模式，添加透明通道
image_with_alpha = image.convert('RGBA')

# 调整透明度
alpha = 128  # 设置透明度值，范围为0-255
image_with_alpha = image_with_alpha.copy()
image_with_alpha.putalpha(alpha)

# 保存图像
image_with_alpha.save('transparent_image.png')
