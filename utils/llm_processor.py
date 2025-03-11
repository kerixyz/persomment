import os
from openai import OpenAI
import pandas as pd
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, OPENAI_MODEL
api_key = OPENAI_API_KEY
client = OpenAI(api_key=api_key)

def generate_personas(client,comments_df, num_personas=3):
   
    sample_size = min(100, len(comments_df))
    sample_comments = comments_df.sample(sample_size)['text'].tolist()
    
    prompt = f"""
    Based on the following {sample_size} YouTube comments, identify {num_personas} distinct personas or viewpoint clusters.
    For each persona, provide:
    1. A short name/title
    2. A brief description of their viewpoint
    3. Key characteristics of their language and perspective
    
    Here are the comments:
    {sample_comments}
    
    Return the response as a JSON array of persona objects with 'name', 'description', and 'characteristics' fields.
    """
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert in analyzing social media comments and identifying distinct user personas."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1500
    )
    
    try:
        content = response.choices[0].message.content
        start_idx = content.find('[')
        end_idx = content.rfind(']') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            personas_json = content[start_idx:end_idx]
            personas = json.loads(personas_json)
        else:
            personas = []
            for i in range(num_personas):
                personas.append({
                    "name": f"Persona {i+1}",
                    "description": f"Description for persona {i+1}",
                    "characteristics": ["characteristic 1", "characteristic 2"]
                })
    except Exception as e:
        print(f"Error parsing personas: {e}")
        personas = []
        for i in range(num_personas):
            personas.append({
                "name": f"Persona {i+1}",
                "description": f"Description for persona {i+1}",
                "characteristics": ["characteristic 1", "characteristic 2"]
            })
    
    return personas

def summarize_comments(client, comments_df, personas):
    
    summaries = {}
    
    # Sample comments to summarize (to avoid token limits)
    sample_size = min(200, len(comments_df))
    sample_comments = comments_df.sample(sample_size)['text'].tolist()
    
    for persona in personas:
        prompt = f"""
        Summarize the following YouTube comments from the perspective of this persona:
        
        Persona: {persona['name']}
        Description: {persona['description']}
        Characteristics: {', '.join(persona['characteristics'])}
        
        Comments:
        {sample_comments}
        
        Provide a summary that captures what this persona would find most important or relevant in these comments.
        """
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert in summarizing social media content from different perspectives."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        summary = response.choices[0].message.content.strip()
        summaries[persona['name']] = summary
    
    return summaries

def extract_useful_content(client, negative_comment):
    
    prompt = f"""
    The following is a negative comment from YouTube. Extract any useful feedback or constructive criticism from it,
    ignoring toxic or unhelpful parts. If there is no useful content, indicate that.
    
    Comment: "{negative_comment}"
    
    Useful content:
    """
    
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert in extracting constructive feedback from negative comments."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=300
    )
    
    useful_content = response.choices[0].message.content.strip()
    return useful_content
