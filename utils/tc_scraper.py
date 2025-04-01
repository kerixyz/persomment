import os
import pandas as pd
import time
from chat_downloader import ChatDownloader

def download_twitch_chat(vod_id, max_comments=1000):
    try:
        url = f"https://www.twitch.tv/videos/{vod_id}"
        chat = ChatDownloader().get_chat(url)

        all_comments_dict = {
            'cid': [],
            'text': [],
            'time': [],
            'author': [],
            'time_parsed': []
        }
        
        count = 0
        for message in chat:
            all_comments_dict['cid'].append(message.get("message_id", ""))
            all_comments_dict['text'].append(message.get("message", ""))
            all_comments_dict['time'].append(message.get("time_in_seconds", ""))
            all_comments_dict['author'].append(message.get("author", {}).get("name", ""))
            all_comments_dict['time_parsed'].append(time.strftime('%H:%M:%S', time.gmtime(message.get("time_in_seconds", 0))))
            
            count += 1
            if max_comments > 0 and count >= max_comments:
                break
        print(all_comments_dict)
        comments_df = pd.DataFrame(all_comments_dict)
        
        comments_dir = os.path.join(DATA_DIR, 'twitch_comments')
        os.makedirs(comments_dir, exist_ok=True)
        
        csv_path = os.path.join(comments_dir, f'{vod_id}.csv')
        comments_df.to_csv(csv_path, index=False)
        
        return True, f"Downloaded {len(comments_df)} comments for VOD: {vod_id}"
    
    except Exception as e:
        return False, f"Error: {str(e)}"
