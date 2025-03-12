import os
import pandas as pd
import time
from youtube_comment_downloader import YoutubeCommentDownloader
import csv
import sys

# Import app config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_DIR, MAX_COMMENTS_PER_VIDEO

def download_comments(video_id_or_url, max_comments=MAX_COMMENTS_PER_VIDEO):
    try:
        downloader = YoutubeCommentDownloader()
        
        if "youtube.com" not in video_id_or_url and "youtu.be" not in video_id_or_url:
            video_url = f"https://www.youtube.com/watch?v={video_id_or_url}"
        else:
            video_url = video_id_or_url
            
        if "youtube.com" in video_url:
            video_id = video_url.split("v=")[1].split("&")[0]
        elif "youtu.be" in video_url:
            video_id = video_url.split("/")[-1].split("?")[0]
        else:
            video_id = video_id_or_url
        
        comments = downloader.get_comments_from_url(video_url)
        
        all_comments_dict = {
            'cid': [],
            'text': [],
            'time': [],
            'author': [],
            'channel': [],
            'votes': [],
            # 'replies': [],
            # 'photo': [],
            # 'heart': [],
            # 'reply': [],
            'time_parsed': []
        }
        
        count = 0
        for comment in comments:
            for key in all_comments_dict.keys():
                all_comments_dict[key].append(comment.get(key, ""))
            
            count += 1
            if max_comments > 0 and count >= max_comments:
                break
        
        comments_df = pd.DataFrame(all_comments_dict)
        
        comments_dir = os.path.join(DATA_DIR, 'comments')
        os.makedirs(comments_dir, exist_ok=True)
        
        csv_path = os.path.join(comments_dir, f'{video_id}.csv')
        comments_df.to_csv(csv_path, index=False)
        
        return True, f"Downloaded {len(comments_df)} comments for video: {video_id}"
    
    except Exception as e:
        return False, f"Error: {str(e)}"