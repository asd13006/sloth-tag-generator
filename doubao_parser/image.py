import json
import re

import httpx


async def doubao_image_parse(url: str, return_raw: bool = False):
    if "doubao.com/thread/" not in url:
        raise ValueError("連結格式不正確，請使用豆包對話連結（包含 /thread/）")

    headers = {
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0"
        ),
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            html_str = response.text
    except httpx.RequestError as e:
        raise ValueError(f"網路請求失敗，請檢查網路連線: {e}")

    match_json_str = re.search(
        r'data-script-src="modern-run-router-data-fn" data-fn-args="(.*?)" nonce="',
        html_str,
        re.DOTALL,
    )

    if not match_json_str:
        raise KeyError("無法解析頁面資料，請確認連結是否有效")

    try:
        json_str = match_json_str.group(1).replace("&quot;", '"')
        json_data = json.loads(json_str)

        if return_raw:
            return json_data

        image_list = []
        for data in json_data:
            if isinstance(data, dict) and data.get("data"):
                message_snapshot = data["data"]["message_snapshot"]["message_list"]
                for message in message_snapshot:
                    if not message.get("content_block"):
                        continue
                    for m2 in message["content_block"]:
                        json_data2 = json.loads(m2["content_v2"])
                        if "creation_block" in json_data2:
                            creations = json_data2["creation_block"]["creations"]
                            for image in creations:
                                image_raw = image["image"]["image_ori_raw"]
                                image_raw["url"] = image_raw["url"].replace("&amp;", "&")
                                image_list.append(image_raw)
    except KeyError:
        raise KeyError("頁面結構發生變化，無法解析圖片資料")
    except json.JSONDecodeError:
        raise ValueError("頁面資料格式錯誤，無法解析")

    return image_list
