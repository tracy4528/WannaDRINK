from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec
import pandas as pd

item_descriptions = [
    "帶有淡淡茉莉花香的綠茶，茶感清新淡雅的茶品。",
    "珍珠的咀嚼口感，配上鮮奶茶，大人小孩都喜歡。(此描述僅供參考)",
    "我們的紅茶不會澀，即使無糖都很好喝，未開封放冰箱一晚茶香更濃郁",
    "烏龍跟青茶完美比例的混合，清香好喝，放冰箱一晚香氣更棒",
    "【僅限冷飲】香濃奶茶加一顆布丁，小朋友會很喜歡，可惜不能做熱的，因為布丁會溶化，不喜歡冰的可以點常溫喔"
]

# tfidf_vectorizer = TfidfVectorizer()
# tfidf_matrix = tfidf_vectorizer.fit_transform(item_descriptions)
# dense_tfidf_matrix = tfidf_matrix.toarray()
# vocabulary = tfidf_vectorizer.get_feature_names_out()
# for idx, term in enumerate(vocabulary):
#     print(f"Index {idx}: {term}")

# # 打印第一個品項的TF-IDF向量
# print("TF-IDF向量 for 第一個品項:")
# print(dense_tfidf_matrix)

