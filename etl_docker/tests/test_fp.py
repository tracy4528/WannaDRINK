import pytest
import sys
import os
test_directory = os.path.dirname(os.path.abspath(__file__))
app_directory = os.path.join(test_directory, '..')  
sys.path.append(app_directory)
from crawl_foodpanda.main import request_get, get_nearby_restaurants



@pytest.mark.parametrize("longitude, latitude, way, sort, cuisine, food_characteristic, budgets, has_discount, limit, offset, expected_output", [
    (121.56716, 25.04106, "外送", "rating_desc", "181", "", "", True, 10, 0, [{"name": "8more白木耳專門店 (台北八德店)"}, {"name": "BlackCoffee 布樂客咖啡"}]),
])
def test_get_nearby_restaurants(longitude, latitude, way, sort, cuisine, food_characteristic, budgets, has_discount, limit, offset, expected_output):
    restaurants = get_nearby_restaurants(longitude, latitude, way, sort, cuisine, food_characteristic, budgets, has_discount, limit, offset)
    assert restaurants == expected_output
