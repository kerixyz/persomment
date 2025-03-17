from flask import Flask, render_template, request, jsonify
import os
import json
import pandas as pd
from utils.yt_scraper import download_comments
from utils.tc_scraper import download_twitch_chat
from utils.llm_processor import generate_personas, summarize_comments, extract_useful_content
from utils.clustering import cluster_comments

app = Flask(__name__)

app.config.from_pyfile('config.py')

@app.route('/')
def index():
    """Home page with options to download comments or view analysis."""
    return render_template('index.html')

@app.route('/download_yt', methods=['POST'])
def download_yt():
    """Download comments from YouTube videos."""
    youtube_ids = request.form.get('youtube_ids').split(',')
    results = {}
    
    for youtube_id in youtube_ids:
        youtube_id = youtube_id.strip()
        success, message = download_comments(youtube_id)
        results[youtube_id] = {'success': success, 'message': message}
    
    return jsonify(results)

@app.route('/download_tc', methods=['POST'])
def download_tc():
    """Download chat from Twitch Vods."""
    twitch_ids = request.form.get('twitch_ids').split(',')
    results = {}
    
    for twitch_id in twitch_ids:
        twitch_id = twitch_id.strip()
        success, message = download_twitch_chat(twitch_id)
        results[twitch_id] = {'success': success, 'message': message}
    
    return jsonify(results)


@app.route('/generate_personas', methods=['POST'])
def create_personas():
    youtube_id = request.form.get('youtube_id')
    num_personas = int(request.form.get('num_personas', 3))
    
    comments_path = os.path.join(app.config['DATA_DIR'], 'comments', f'{youtube_id}.csv')
    if not os.path.exists(comments_path):
        return jsonify({'success': False, 'message': 'Comments not found for this video'})
    
    comments_df = pd.read_csv(comments_path)
    
    try:
        personas = generate_personas(comments_df, num_personas)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Failed to generate personas: {e}'})

    personas_dir = os.path.join(app.config['DATA_DIR'], 'personas')
    os.makedirs(personas_dir, exist_ok=True)
    with open(os.path.join(personas_dir, f'{youtube_id}_personas.json'), 'w') as f:
        json.dump(personas, f)
    
    summaries = summarize_comments(comments_df, personas)
    
    summaries_dir = os.path.join(app.config['DATA_DIR'], 'summaries')
    os.makedirs(summaries_dir, exist_ok=True)
    with open(os.path.join(summaries_dir, f'{youtube_id}_summaries.json'), 'w') as f:
        json.dump(summaries, f)
    
    return jsonify({'success': True, 'personas': personas, 'summaries': summaries})

@app.route('/view_personas/<youtube_id>')
def view_personas(youtube_id):
    """View personas and summaries for a specific YouTube video."""
    personas_path = os.path.join(app.config['DATA_DIR'], 'personas', f'{youtube_id}_personas.json')
    summaries_path = os.path.join(app.config['DATA_DIR'], 'summaries', f'{youtube_id}_summaries.json')
    
    if not os.path.exists(personas_path) or not os.path.exists(summaries_path):
        return render_template('error.html', message='Personas or summaries not found for this video')
    
    with open(personas_path, 'r') as f:
        personas = json.load(f)
    
    with open(summaries_path, 'r') as f:
        summaries = json.load(f)
    
    return render_template('personas.html', youtube_id=youtube_id, personas=personas, summaries=summaries)

@app.route('/negative_comments/<youtube_id>')
def negative_comments(youtube_id):
    """View negative comments with extracted useful content."""
    comments_path = os.path.join(app.config['DATA_DIR'], 'comments', f'{youtube_id}.csv')
    
    if not os.path.exists(comments_path):
        return render_template('error.html', message='Comments not found for this video')
    
    comments_df = pd.read_csv(comments_path)
    
    negative_comments = comments_df.sample(min(10, len(comments_df)))
    
    comments_with_useful_content = []
    for _, comment in negative_comments.iterrows():
        useful_content = extract_useful_content(comment['text'])
        comments_with_useful_content.append({
            'original': comment['text'],
            'useful_content': useful_content
        })
    
    return render_template('negative_comments.html', 
                          youtube_id=youtube_id, 
                          comments=comments_with_useful_content)

@app.route('/videos')
def list_videos():
    """List all videos with downloaded comments."""
    comments_dir = os.path.join(app.config['DATA_DIR'], 'comments')
    if not os.path.exists(comments_dir):
        return jsonify([])
    
    videos = []
    for filename in os.listdir(comments_dir):
        if filename.endswith('.csv'):
            video_id = filename.replace('.csv', '')
            videos.append(video_id)
    
    return jsonify(videos)

if __name__ == '__main__':
    os.makedirs(os.path.join(app.config['DATA_DIR'], 'comments'), exist_ok=True)
    os.makedirs(os.path.join(app.config['DATA_DIR'], 'personas'), exist_ok=True)
    os.makedirs(os.path.join(app.config['DATA_DIR'], 'summaries'), exist_ok=True)
    
    app.run(debug=True)
