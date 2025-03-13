import os
import pandas as pd
import time
import requests
import json
import csv
import sys

# Import app config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_DIR, MAX_COMMENTS_PER_VIDEO, TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET

def get_twitch_access_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()["access_token"]

def download_twitch_chat(vod_id, max_comments=MAX_COMMENTS_PER_VIDEO):
    try:
        access_token = get_twitch_access_token()
        url = f"https://api.twitch.tv/v5/videos/{vod_id}/comments"
        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        chat_data = response.json()

        all_comments_dict = {
            'cid': [],
            'text': [],
            'time': [],
            'author': [],
            'time_parsed': []
        }
        
        count = 0
        for comment in chat_data.get("comments", []):
            all_comments_dict['cid'].append(comment.get("_id", ""))
            all_comments_dict['text'].append(comment.get("message", {}).get("body", ""))
            all_comments_dict['time'].append(comment.get("content_offset_seconds", ""))
            all_comments_dict['author'].append(comment.get("commenter", {}).get("display_name", ""))
            all_comments_dict['time_parsed'].append(time.strftime('%H:%M:%S', time.gmtime(comment.get("content_offset_seconds", 0))))
            
            count += 1
            if max_comments > 0 and count >= max_comments:
                break
        
        comments_df = pd.DataFrame(all_comments_dict)
        
        comments_dir = os.path.join(DATA_DIR, 'twitch_comments')
        os.makedirs(comments_dir, exist_ok=True)
        
        csv_path = os.path.join(comments_dir, f'{vod_id}.csv')
        comments_df.to_csv(csv_path, index=False)
        
        return True, f"Downloaded {len(comments_df)} comments for VOD: {vod_id}"
    
    except Exception as e:
        return False, f"Error: {str(e)}"
