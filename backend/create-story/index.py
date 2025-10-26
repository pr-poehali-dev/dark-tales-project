import json
from typing import Dict, Any
from datetime import datetime

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
        
        new_story = {
            'id': 999,
            'title': title,
            'description': description,
            'genre': genre if isinstance(genre, list) else [genre],
            'authorId': author_id,
            'rating': 0,
            'views': 0,
            'likes': 0,
            'comments': 0,
            'readingTime': reading_time,
            'publishedAt': datetime.now().isoformat(),
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
