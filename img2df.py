import gzip
import base64

import json

from PIL import Image

from inspect import getsourcefile
import os

import pyperclip


path = os.path.dirname(os.path.abspath(__file__))



def Initialize():

    # Empty result.txt file
    with open("result.txt", "w") as f:
        f.write("")

    Convert()

def toHex(r, g, b):
    hex_str = format((r << 16) | (g << 8) | b, '06x')
    if (hex_str =="000000"): return "§0"
    if (hex_str =="0000aa"): return "§1"
    if (hex_str =="00aa00"): return "§2"
    if (hex_str =="00aaaa"): return "§3"
    if (hex_str =="aa0000"): return "§4"
    if (hex_str =="aa00aa"): return "§5"
    if (hex_str =="ffaa00"): return "§6"
    if (hex_str =="aaaaaa"): return "§7"
    if (hex_str =="555555"): return "§8"
    if (hex_str =="5555ff"): return "§9"
    if (hex_str =="55ff55"): return "§a"
    if (hex_str =="55ffff"): return "§b"
    if (hex_str =="ff5555"): return "§c"
    if (hex_str =="ff55ff"): return "§d"
    if (hex_str =="ffff55"): return "§e"
    if (hex_str =="ffffff"): return "§f"
    return "§x§" + "§".join(hex_str[i:i+1] for i in range(0, len(hex_str)))

#     return "§"+("x"+hex).split('').join('§');

def getPixelColor(x, y, img):
    pixel = 0
    try:
        pixel = img.getpixel((x, y))
    except:
        pixel = (0, 0, 0, 0)
    
    if (isinstance(pixel, int)):
        print(pixel)
        pixel = (0, 0, 0, 255)
    
    r, g, b, a = pixel

    if a == 0:
        return "§l  "
    return toHex(r, g, b) + "■ "
    
def toJson(l, name):
    json_str = '{"blocks":[{"id":"block","block":"func","data":"'+name+'","args":{"items":[{"item":{"id":"bl_tag","data":{"option":"False","tag":"Is Hidden","action":"dynamic","block":"func"}},"slot":26}]}},{"id":"block","block":"set_var","args":{"items":[{"item":{"id":"var","data":{"name":"textures","scope":"local"}},"slot":0}]},"action":"CreateList"}]}'
    j = json.loads(json_str)

    items = []
    for _,i in enumerate(l):
        items.append(json.loads('{"item": {"id": "txt","data": {"name": \"'+str(i)+'\"}},"slot": '+str(_+1)+'}'))
    
    for i in items:
        j["blocks"][1]["args"]["items"].append(i)
    
    return j

def compress(str):
    compressed = gzip.compress(str.encode('utf-8'))
    result = base64.b64encode(b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\xff' + compressed[10:])
    return(result)

def optimize(result):
    r = result
    for _,i in enumerate(result):
        t = ""
        ind = 0
        spacer = 0
        
        #print(i)
        while ind < len(i):
            code = i[ind+1:ind+2]

            if (code == "n"):
                t += "\\n"
                ind += 2
                continue

            if (code == "l"):
                if (spacer == code):
                    t += "  "
                else:
                    t += "§l  "
                spacer = code
                ind += 4
            
            if ('a' <= code <= 'f' or '0' <= code <= '9'):
                if (spacer == i[ind:ind+2]):
                    t += "■ "
                else:
                    t += f"{i[ind:ind+2]}■ "
                spacer = i[ind:ind+2]
                ind += 4

            if (code == "x"):
                if (spacer == i[ind:ind+14]):
                    t += "■ "
                else:
                    t += f"{i[ind:ind+14]}■ "
                spacer = i[ind:ind+14]
                ind += 16

            #print(f"{ind}: {code} ({spacer})")
        #print(t)


        # optimize
        r[_] = t
    return r

def Convert():
    for filename in os.listdir(path):
        if (filename.endswith(".png")):
            print(f"Converting {filename}")
            file_path = os.path.join(path, filename)
            img = Image.open(file_path)
            img = img.convert("RGBA")

            result = ["", "", "", ""]
            
            width, height = img.size
            for y in range(0, height, 2):
                for x in range(0, width, 2):
                    result[0] += getPixelColor(x, y, img)
                    result[1] += getPixelColor(x+1, y, img)
                    result[2] += getPixelColor(x, y+1, img)
                    result[3] += getPixelColor(x+1, y+1, img)
                result = [f"{s}\\n" for s in result]
            
            result = optimize(result)

            result_json = toJson(result, filename)
            #print(json.dumps(result_json, ensure_ascii=False))
            compressed = compress(json.dumps(result_json, ensure_ascii=False))
            compressed = str(compressed)[2:-1]
            item = """minecraft:ender_chest{PublicBukkitValues:{"hypercube:codetemplatedata":'{"author":"DFL","name":"§b§lFunction §3» §b#NAME","version":1,"code":"#CODE"}'},display:{Name:'{"extra":[{"bold":true,"italic":false,"underlined":false,"strikethrough":false,"obfuscated":false,"color":"aqua","text":"Function "},{"bold":false,"italic":false,"color":"dark_aqua","text":"» "},{"italic":false,"color":"aqua","text":"Unnamed"}],"text":""}'}}"""
            
            final_result = item.replace("#NAME", filename).replace("#CODE", compressed)

            print(" - Done")
            with open(f"result.txt", "a") as f:
                f.write(f"{filename}:\n{final_result}\n\n")

            result = [f'"{s}"' for s in result]
            # Result for DFL ^
            

#toJson(["TEST1", "TEST2"], "namething")
Initialize()