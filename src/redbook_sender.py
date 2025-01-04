from PIL import Image, ImageDraw, ImageFont
import platform
from dotenv import load_dotenv
load_dotenv()
import json
import traceback
from datetime import datetime,timedelta
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def string_to_vertical_image(
    text: str, 
    font_path: str = f"{CURRENT_DIR}/../json/song.TTF",  # Default font path
    font_size: int = 30, 
    image_width: int = 800, 
    background_color: str = "white", 
    text_color: str = "black", 
    output_path: str = "vertical_text.png"
):
    # Load the font
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        raise IOError(f"Unable to load font from {font_path}. Please ensure the font file exists and is valid.")

    # Split the text into lines to fit the image width
    def wrap_text(text, font, max_width):
        lines = []
        current_line = ""
        for char in text:
            if char == "\n":  # Preserve manual newlines
                lines.append(current_line)
                current_line = ""
                continue
            test_line = current_line + char
            if font.getbbox(test_line)[2] > max_width:  # Check if line exceeds max width
                lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        if current_line:  # Add remaining text
            lines.append(current_line)
        return lines

    lines = wrap_text(text, font, image_width - 40)  # Add margin

    # Calculate image height
    line_height = font.getbbox("A")[3] + 10  # Height of one line with spacing
    image_height = line_height * len(lines) + 40  # Add padding

    # Create the image
    image = Image.new("RGB", (image_width, image_height), background_color)
    draw = ImageDraw.Draw(image)

    # Draw the text
    y = 20
    for line in lines:
        line_width = font.getbbox(line)[2]
        x = (image_width - line_width) // 2  # Center align
        draw.text((x, y), line, fill=text_color, font=font)
        y += line_height

    # Save the image
    image.save(output_path)
    return output_path


XIAOHONGSHU_COOKING = f'{CURRENT_DIR}/../config/rb_config.json'

def get_driver():
    options = Options()
    # options.add_argument("--headless")  # 无头模式，不打开浏览器界面
    options.add_argument("--no-sandbox")  # 避免沙盒错误
    options.add_argument("--disable-dev-shm-usage")  # 禁用开发共享内存
    options.add_argument("--remote-debugging-port=9222")  # 启用远程调试端口
    options.add_argument("--disable-gpu")  # 禁用GPU加速

    # 自动下载并配置 ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def xiaohongshu_login(driver):
    if (os.path.exists(XIAOHONGSHU_COOKING)):
        print("cookies存在")
        with open(XIAOHONGSHU_COOKING) as f:
            cookies = json.loads(f.read())
            driver.get("https://creator.xiaohongshu.com/publish/publish")
            driver.implicitly_wait(10)
            driver.delete_all_cookies()
            time.sleep(4)
            # 遍历cook
            print("加载cookie")
            for cookie in cookies:
                if 'expiry' in cookie:
                    del cookie["expiry"]
                # 添加cook
                driver.add_cookie(cookie)
            # 刷新
            print("开始刷新")
            driver.refresh()
            driver.get("https://creator.xiaohongshu.com/publish/publish")
            time.sleep(5)
    else:
        print("cookies不存在")
        driver.get('https://creator.xiaohongshu.com/creator/post')
        # driver.find_element(
        #     "xpath", '//*[@placeholder="请输入手机号"]').send_keys("")
        # # driver.find_element(
        # #     "xpath", '//*[@placeholder="请输入密码"]').send_keys("")
        # driver.find_element("xpath", '//button[text()="登录"]').click()
        print("等待登录")
        time.sleep(30)
        print("登录完毕")
        cookies = driver.get_cookies()
        with open(XIAOHONGSHU_COOKING, 'w') as f:
            f.write(json.dumps(cookies))
        print(cookies)
        time.sleep(1)

def get_publish_date():
    tomorrow = now = datetime.today()
    if(now.hour > 20):
        tomorrow = now + timedelta(days = 1)
        tomorrow = tomorrow.replace(hour=20)
    else:
        tomorrow = tomorrow.replace(hour=20,minute=0)
    return tomorrow.strftime("%Y-%m-%d %H:%M")

def publish_xiaohongshu_image(driver, image_path,title,describe,keywords):
    time.sleep(3)

    html = driver.page_source
    driver.find_element(By.XPATH, '//span[@class="title" and text()="上传图文"]').click()
    push_file = driver.find_element(By.CSS_SELECTOR, 'input.upload-input[type="file"][multiple][accept=".jpg,.jpeg,.png,.webp"]')
    file_names = os.listdir(image_path)
    # 打印所有文件名
    for file_name in file_names:
        canonical_path = os.path.abspath(f"{image_path}/{file_name}")
        push_file.send_keys(canonical_path)

    # 填写标题
    driver.find_element(
        By.XPATH, '//input[@placeholder="填写标题会有更多赞哦～"]').send_keys(title)

    time.sleep(1)
    # 填写描述
    content_clink = driver.find_element(
        By.XPATH, '//div[@class="ql-editor ql-blank" and @contenteditable="true" and @aria-owns="quill-mention-list" and @data-placeholder="输入正文描述，真诚有价值的分享予人温暖"]')
    content_clink.send_keys(describe)

    time.sleep(3)

    for label in keywords:
        content_clink.send_keys(label)
        time.sleep(1)
        # 直接找到id是quill-mention-item-0的元素然后点击
        try:
            mention_item = driver.find_element(By.ID, 'quill-mention-item-0')
            mention_item.click()
            print("点击标签", label)
        except Exception:
            traceback.print_exc()
        time.sleep(1)

    # 发布
    driver.find_element(By.XPATH, '//*[text()="发布"]').click()
    print("图文发布完成！")
    time.sleep(10)


def rb_main():
    while True:
        current_time = time.localtime()
        if current_time.tm_hour == 15 and current_time.tm_min == 35:
            current_time = time.localtime()
            today_date = time.strftime("%m-%d", current_time)
            print(f"Today's date is: {today_date}")
            try:
                title = f"ChatGPT勇闯美股 {today_date}"
                keywords = ['#python','#美股','#股票','#投资', 'ChatGPT', 'AI','Quant']
                describe = '个人工具分享，不构成投资建议'
                driver = get_driver()
                xiaohongshu_login(driver=driver)
                publish_xiaohongshu_image(driver, image_path = f"{CURRENT_DIR}/../json/redbook_pic", title=title,keywords=keywords,describe=describe)
                print('finished')
            finally:
                if driver:
                    driver.quit()

            print('Redbook Sender is done')

            time.sleep(60)

if __name__=='__main__':
    rb_main()