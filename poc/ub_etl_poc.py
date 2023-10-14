import json

# 讀取JSON檔案
with open("web_page.json", "r") as json_file:
    data = json.load(json_file)

html_content = data.get("html_content", "")

# 使用正則表達式提取數字
import re

pattern = r'<div class="spacer _4"></div><div class="spacer _4"></div>(.*?)</div>'
# match = re.search(pattern, html_content)
matches = re.finditer(pattern, html_content)

pattern2 = r'<div class=\"g9 ga hx bb\"><span data-testid=\"rich-text\" class=\"hy ei hz ch d2 cj d3 b1\">(.*?)</span>'
drink_matches = re.finditer(pattern2, html_content)

for match in matches:
    number = match.group(1)
    print( number)

for m in drink_matches:
    drink = m.group(1)
    print( drink)




