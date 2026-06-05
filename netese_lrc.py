import requests
import re
import os


def get_song_id(url):

    match = re.search(r"id=(\d+)", url)

    if match:
        return match.group(1)

    return None


def parse_lrc(lines):
    """
    解析 LRC
    返回：
    {
        "[00:10.00]": "歌词"
    }
    """

    result = {}

    for line in lines:

        matches = re.findall(r"\[\d+:\d+\.\d+\]", line)

        if not matches:
            continue

        text = re.sub(r"\[\d+:\d+\.\d+\]", "", line).strip()

        for tag in matches:

            result[tag] = text

    return result


def merge_lrc(original_dict, translated_dict):

    merged = []

    for tag in sorted(original_dict.keys()):

        original_text = original_dict[tag]

        merged.append(f"{tag}{original_text}")

        if tag in translated_dict:

            trans_text = translated_dict[tag]

            if trans_text != "":
                merged.append(f"{tag}{trans_text}")

    return "\n".join(merged)


def download_lyric(song_id):

    headers = {
        "Referer": "https://music.163.com",
        "User-Agent": "Mozilla/5.0"
    }

    lyric_api = (
    f"https://music.163.com/api/song/lyric/v1"
    f"?id={song_id}&cp=false&tv=0&lv=0&rv=0&kv=0&yv=0&ytv=0&yrv=0"
)

    response = requests.get(lyric_api, headers=headers)

    data = response.json()
   
    
    if "lrc" not in data:

        print("没有找到歌词")
        return

    # 原歌词
    original_text = data["lrc"].get("lyric", "")

    # 翻译歌词
    translated_text = ""

    if "tlyric" in data:

        translated_text = data["tlyric"].get("lyric", "")

    # 解析
    original_dict = parse_lrc(
        original_text.splitlines()
    )

    translated_dict = parse_lrc(
        translated_text.splitlines()
    )

    # 合并
    final_lrc = merge_lrc(
        original_dict,
        translated_dict
    )

    # 获取歌曲名
    song_api = (
        f"https://music.163.com/api/song/detail/"
        f"?id={song_id}&ids=[{song_id}]"
    )

    song_response = requests.get(song_api, headers=headers)

    song_data = song_response.json()

    song_name = song_data["songs"][0]["name"]

    # 清理非法字符
    song_name = re.sub(
        r'[\\/:*?"<>|]',
        '_',
        song_name
    )

    filename = f"{song_name}.lrc"

    with open(filename, "w", encoding="utf-8") as f:

        f.write(final_lrc)

    print("\n下载完成！")
    print(f"文件名：{filename}")
    print(f"保存位置：{os.path.abspath(filename)}")


# =========================

print("网易云双语歌词下载器")
print("--------------------")

url = input("\n请输入网易云歌曲链接：\n")

song_id = get_song_id(url)

if song_id:

    download_lyric(song_id)

else:

    print("链接格式错误")