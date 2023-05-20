import logging
import subprocess
import os
import requests
from easyOCR import cudaVersionGet
from public import update_global

update_global()
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 '
                  'Safari/537.36 '
}

if os.path.exists("torch"):
    pass
else:
    if cudaVersionGet():  # 如果存在CUDA，则自动安装pytorch
        url = "https://download.pytorch.org/whl/cu" + cudaVersionGet()
        response = requests.get(url, headers=header)
        error_count = 0
        while response.status_code != 200:
            url = "https://download.pytorch.org/whl/cu" + str(int(cudaVersionGet()) + 1)
            response = requests.get(url)
            error_count += 1
            if error_count > 20:
                logging.error(f"Error occurred: {response.status_code}")
                break
        else:
            url = "https://download.pytorch.org/whl/cu" + cudaVersionGet()
            subprocess.Popen(['cmd', '/k', 'pip3 install torch torchvision --index-url %s' % url],
                             creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        subprocess.Popen(['cmd', '/k', 'pip3 install torch torchvision'], creationflags=subprocess.CREATE_NEW_CONSOLE)

import UI


def start():
    try:
        root = UI.MainGUI()
        root.wm_attributes('-alpha', 0.9)
        root.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    start()

# pip freeze > requirements.txt  将所有三方库列出
# pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ 下载所有三方库
