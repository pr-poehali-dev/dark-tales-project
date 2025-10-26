import json
import os
from typing import Dict, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: API для создания новых рассказов ужасов
    Args: event - dict с httpMethod, body (title, description, genre, authorId)
          context - object с request_id, function_name
    Returns: JSON созданного рассказа с id
    '''
    method: str = event.get('httpMethod', 'POST')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-User-Id',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    if method == 'POST':
        body_data = json.loads(event.get('body', '{}'))
        
        title = body_data.get('title')
        description = body_data.get('description')
        content = body_data.get('content', '')
        genre = body_data.get('genre', [])
        author_id = body_data.get('authorId')
        reading_time = body_data.get('readingTime', 10)
        
        if not title or not description or not author_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({
                    'error': 'Missing required fields',
                    'required': ['title', 'description', 'authorId']
                })
            }
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute('''
            INSERT INTO stories (title, description, content, author_id, reading_time)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, published_at::text as published_at
        ''', (title, description, content, int(author_id), reading_time))
        
        result = cur.fetchone()
        story_id = result['id']
        published_at = result['published_at']
        
        genre_list = genre if isinstance(genre, list) else [genre]
        for g in genre_list:
            if g:
                cur.execute('''
                    INSERT INTO story_genres (story_id, genre)
                    VALUES (%s, %s)
                ''', (story_id, g))
        
        cur.execute('''
            UPDATE authors
            SET stories_count = stories_count + 1
            WHERE id = %s
        ''', (int(author_id),))
        
        conn.commit()
        cur.close()
        conn.close()
        
        new_story = {
            'id': story_id,
            'title': title,
            'description': description,
            'content': content,
            'genre': genre_list,
            'authorId': author_id,
            'rating': 0,
            'views': 0,
            'likes': 0,
            'comments': 0,
            'readingTime': reading_time,
            'publishedAt': published_at,
            'status': 'published'
        }
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'isBase64Encoded': False,
            'body': json.dumps({
                'success': True,
                'story': new_story,
                'message': 'Story created successfully'
            })
        }
    
    return {
        'statusCode': 405,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'isBase64Encoded': False,
        'body': json.dumps({'error': 'Method not allowed'})
    }