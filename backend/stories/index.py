import json
from typing import Dict, Any, List, Optional
from datetime import datetime

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: API для управления рассказами ужасов - получение списка, поиск, фильтрация
    Args: event - dict с httpMethod, queryStringParameters, body
          context - object с request_id, function_name
    Returns: JSON список рассказов или детали рассказа
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-User-Id',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    if method == 'GET':
        params = event.get('queryStringParameters', {}) or {}
        story_id = params.get('id')
        genre = params.get('genre')
        sort_by = params.get('sort', 'latest')
        
        mock_stories = [
            {
                "id": 1,
                "title": "Тени в подвале",
                "author": {
                    "id": 1,
                    "name": "Александр Темный",
                    "avatar": "/img/4a8f619e-b09e-4045-86d6-b6e8f9490542.jpg",
                    "rating": 4.8,
                    "stories": 23
                },
                "description": "Когда старый дом начинает скрипеть по ночам, а тени на стенах становятся длиннее, становится ясно — здесь живет что-то древнее и злобное...",
                "genre": ["Мистика", "Психологический ужас"],
                "rating": 4.9,
                "views": 1250,
                "likes": 89,
                "comments": 23,
                "publishedAt": "2024-01-15",
                "readingTime": 8
            },
            {
                "id": 2,
                "title": "Последний поезд",
                "author": {
                    "id": 2,
                    "name": "Мария Кровавая",
                    "avatar": "/img/4a8f619e-b09e-4045-86d6-b6e8f9490542.jpg",
                    "rating": 4.6,
                    "stories": 15
                },
                "description": "Полночный поезд, который приходит только раз в год. Пассажиры говорят, что билет в один конец стоит всего лишь душу...",
                "genre": ["Сверхъестественное", "Готика"],
                "rating": 4.7,
                "views": 980,
                "likes": 67,
                "comments": 18,
                "publishedAt": "2024-01-12",
                "readingTime": 12
            },
            {
                "id": 3,
                "title": "Зеркальная комната",
                "author": {
                    "id": 3,
                    "name": "Николай Мрачный",
                    "avatar": "/img/4a8f619e-b09e-4045-86d6-b6e8f9490542.jpg",
                    "rating": 4.9,
                    "stories": 31
                },
                "description": "В каждом зеркале живет отражение, но что делать, если отражение начинает жить своей жизнью и планирует занять твое место?",
                "genre": ["Паранормальное", "Триллер"],
                "rating": 4.8,
                "views": 1560,
                "likes": 124,
                "comments": 35,
                "publishedAt": "2024-01-10",
                "readingTime": 15
            }
        ]
        
        if story_id:
            story = next((s for s in mock_stories if s['id'] == int(story_id)), None)
            if story:
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps(story)
                }
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({'error': 'Story not found'})
            }
        
        filtered_stories = mock_stories
        if genre:
            filtered_stories = [s for s in filtered_stories if genre in s['genre']]
        
        if sort_by == 'popular':
            filtered_stories = sorted(filtered_stories, key=lambda x: x['views'], reverse=True)
        elif sort_by == 'rating':
            filtered_stories = sorted(filtered_stories, key=lambda x: x['rating'], reverse=True)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'isBase64Encoded': False,
            'body': json.dumps({'stories': filtered_stories, 'total': len(filtered_stories)})
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
