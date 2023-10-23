import pytest
import sys
import os
import pandas as pd
from unittest.mock import Mock, patch
test_directory = os.path.dirname(os.path.abspath(__file__))
app_directory = os.path.join(test_directory, '..')  
sys.path.append(app_directory)
from server.controllers.dashboard_controller import all_store,hot_article,drink_google_result



def test_all_store():
    result = all_store()

    assert isinstance(result, tuple)

    assert len(result) == 3

    assert isinstance(result[0], int)  
    assert isinstance(result[1], int)  
    assert isinstance(result[2], int)  



def test_hot_article_database_connection():
    with patch('server.controllers.dashboard_controller.conn_pool.get_connection') as mock_get_connection:
        mock_conn = Mock()
        mock_get_connection.return_value = mock_conn

        mock_cursor = mock_conn.cursor.return_value

        mock_cursor.fetchall.return_value = [
            {'url': "url1", 'push': 10, 'title': 'Title 1', 'crawl_date': '20231023'},
            {'url': "url2", 'push': 20, 'title': 'Title 2', 'crawl_date': '20231023'},
        ]

        result = hot_article()

    assert isinstance(result, pd.DataFrame)

    expected_data = [
        {'Title': '<a href="url1">Title 1</a>', 'Push': 10, 'URL': 'url1'},
        {'Title': '<a href="url2">Title 2</a>', 'Push': 20, 'URL': 'url2'},
    ]
    assert result.to_dict(orient='records') == expected_data


def test_drink_google_result():
     with patch('server.controllers.dashboard_controller.conn_pool.get_connection') as mock_get_connection:
        mock_conn = Mock()
        mock_get_connection.return_value = mock_conn

        mock_cursor = mock_conn.cursor.return_value

        mock_cursor.fetchall.return_value = [
            {'store': 'Store 1', 'trend_index': 10.5},
            {'store': 'Store 2', 'trend_index': 8.2},
        ]

        result = drink_google_result()
        assert isinstance(result, dict)
        expected_result = {'Store 1': 10.5, 'Store 2': 8.2}
        assert result == expected_result
    