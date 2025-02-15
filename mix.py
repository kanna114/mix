from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment, Message
from nonebot.params import CommandArg
from datetime import datetime
import json
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

MIX_DIR = Path(__file__).parent / "emojiMix"

mix = on_command("mix")

def read_json(file_path: Path):
    """读取JSON文件并返回数据"""
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)




def getMixEmoji(emoji1, emoji2, fn):

    emoji_code_1 = "-".join(f"{hex(ord(c))[2:]}" for c in emoji1)
    emoji_code_2 = "-".join(f"{hex(ord(c))[2:]}" for c in emoji2)

    info = read_json(MIX_DIR / "metadata4.json")


    if(emoji_code_1 not in info or emoji_code_2 not in info ):
        return -1
    
    link = "NULL"
    for i in info[emoji_code_1]:
        if((emoji_code_1 == i["leftEmoji"] and emoji_code_2 == i["rightEmoji"]) or (emoji_code_2 == i["leftEmoji"] and emoji_code_1 == i["rightEmoji"])):
            link = i["fn"]
            break
    #print(le,re,de)
    if(link == "NULL"):
        return -1
    q = requests.get("https://www.gstatic.com/android/keyboard/emojikitchen/%s"%(link))
    dat = q.content
    f = open(fn, "wb")
    f.write(dat)
    f.close()
    return 0


@mix.handle()
async def handle_first_receive(matcher: Matcher, event: Event, msg: Message = CommandArg()):
    args = str(msg).split(" ")
    if(len(args) == 2):
        mix_out = MIX_DIR / "mix.png"
        e = getMixEmoji(args[0], args[1], str(mix_out))
        if(e == 0):
            await mix.finish(MessageSegment.image(mix_out.resolve().as_uri()))
        else:
            await mix.finish("可能为不存在的表情组合")
    if(len(args) >= 4):
        power_factor = 1
        if(len(args) > 4):
            power_factor = float(args[4])
        stats = getMixEmoji(args[0], args[1], str(MIX_DIR / "img1.png"))
        if(stats < 0):
            await mix.finish("指令中可能有不存在的表情组合")
        stats = getMixEmoji(args[2], args[3], str(MIX_DIR / "img2.png"))
        if(stats < 0):
            await mix.finish("指令中可能有不存在的表情组合")

        temp_image = Image.new('RGB', (180, 180), (0, 0, 0))
        gif_frames = []
        pic1 = Image.open(str(MIX_DIR / "img1.png")).convert("RGBA")
        pic2 = Image.open(str(MIX_DIR / "img2.png")).convert("RGBA")
        image_size = (110, 110)
        move_1 = [0, 0, 3, 4, 7, 10, 7, 5, 2, 0]
        move_2 = [0, 4, 7, 12, 19, 15, 12, 7, 3, 2, 0]
        for i in range(0, 10):
            bg = temp_image.copy()
            bg.paste(pic1.resize(image_size), (20 - int(move_1[i] * power_factor), 70), pic1.resize(image_size))
            bg.paste(pic2.resize(image_size).rotate(-20), (70 - int(move_2[i] * power_factor), 50), pic2.resize(image_size).rotate(-20))
            bg = bg.resize((75, 75))
            gif_frames.append(bg)
            
        gif_out = MIX_DIR / "out.gif"
        gif_frames[0].save(str(gif_out),
                save_all=True, append_images=gif_frames[1:], optimize=False, duration=15, loop=0, transparency=0)
        
        await mix.finish(MessageSegment.image(gif_out.resolve().as_uri()))