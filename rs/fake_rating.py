import random
import time
import csv
import pandas as pd
from itertools import islice



def generate_random_data(num_reviewers, min_items_per_reviewer, max_items_per_reviewer):
    data = []
    current_time = int(time.time())
    
    item_ids = [f"B{random.randint(0, 9999999999):010}" for _ in range(100)]  # 假設有 100 種不同的 item_id
    
    for _ in range(num_reviewers):
        reviewer_id = f"A{random.randint(1000000000, 9999999999)}"
        num_items = random.randint(min_items_per_reviewer, max_items_per_reviewer)
        
        for _ in range(num_items):
            item_id = random.choice(item_ids) 
            rating = round(random.uniform(1.0, 5.0), 1)
            timestamp = random.randint(current_time - 365 * 24 * 3600, current_time)
            
            data.append([reviewer_id, item_id, rating, timestamp])
    
    return data









def save_data_to_csv(data, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['reviewerID', 'itemID', 'rating', 'time'])
        writer.writerows(data)

# 使用示例：生成 20 位 reviewer，每位有 5 到 10 個不等的 item 評分
# random_data = generate_random_data(30, 20, 30)
# save_data_to_csv(random_data, 'ratings.csv')


# df = pd.read_csv('/Users/tracy4528/Downloads/Clothing_Shoes_and_Jewelry_small.csv')
# df_sub=df.head(10000)
# df_sub.to_csv('/Users/tracy4528/Desktop/appwork/01personal/ratings_subset.csv', index=False)



csv_url = '/Users/tracy4528/Downloads/Clothing_Shoes_and_Jewelry_small.csv'
output_file = 'output.csv'  
num_rows_to_extract = 10000  

drink_id_mapping = {}


with open(csv_url, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
    reader = csv.reader(islice(infile, num_rows_to_extract))  
    header = next(reader)  


    writer = csv.writer(outfile)
    writer.writerow(header + ['drinkID'])  

    for row in reader:
        reviewer_id, item_id, rating, time = row


        if item_id not in drink_id_mapping:
            drink_id_mapping[item_id] = len(drink_id_mapping) + 1

        drink_id = drink_id_mapping[item_id]

        writer.writerow([reviewer_id, item_id, rating, time, drink_id])





