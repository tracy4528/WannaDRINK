import pytest
import sys
import os
import json
from bs4 import BeautifulSoup
test_directory = os.path.dirname(os.path.abspath(__file__))
app_directory = os.path.join(test_directory, '..')  
sys.path.append(app_directory)
from crawl_ptt.main import get_post_comment

def test_get_post_comment():

    html = """
    <div class="article-metaline">
        <span class="article-meta-value">Author Name</span>
    </div>
    <div class="article-metaline">
        <span class="article-meta-value">Post Title</span>
    </div>
    <div class="article-metaline">
        <span class="article-meta-value">2023-10-19</span>
    </div>
    <div id="main-content">
        Main Content
        --
        ※ 發信站: 批踢踢實業坊(ptt.cc), 來自: Somewhere
    </div>
    <div class="push">
        <span class="push-tag">→</span>
        <span class="push-userid">User1</span>
        <span class="push-content">Comment 1</span>
        <span class="push-ipdatetime">10/19 10:00</span>
    </div>
    <div class="push">
        <span class="push-tag">→</span>
        <span class="push-userid">User2</span>
        <span class="push-content">Comment 2</span>
        <span class="push-ipdatetime">10/19 10:30</span>
    </div>
    """

    soup = BeautifulSoup(html, 'html.parser')

    json_data = get_post_comment(soup)

    # 解析 JSON 数据
    data = json.loads(json_data)

    assert data['meta_data']['author'] == 'Author Name'
    assert data['meta_data']['title'] == 'Post Title'
    assert data['meta_data']['date'] == '2023-10-19'
    assert data['content'] == 'Main Content'
    assert len(data['comments']) == 2
    assert data['comments'][0]['tag'] == '→'
    assert data['comments'][0]['userid'] == 'User1'
    assert data['comments'][0]['content'] == 'Comment 1'
    assert data['comments'][0]['time'] == '10/19 10:00'