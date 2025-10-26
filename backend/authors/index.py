import json
from typing import Dict, Any, List

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: API для получения информации об авторах и топ авторов
    Args: event - dict с httpMethod, queryStringParameters
          context - object с request_id, function_name
    Returns: JSON список авторов или данные конкретного автора
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-User-Id',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    if method == 'GET':
        params = event.get('queryStringParameters', {}) or {}
        author_id = params.get('id')
        top = params.get('top')
        
        mock_authors = [
            {
                "id": 1,
                "name": "Александр Темный",
                "avatar": "/img/4a8f619e-b09e-4045-86d6-b6e8f9490542.jpg",
                "rating": 4.8,
                "stories": 23,
                "followers": 340,
                "bio": "Мастер психологических триллеров"
            },
            {
                "id": 2,
                "name": "Мария Кровавая",
                "avatar": "/img/4a8f619e-b09e-4045-86d6-b6e8f9490542.jpg",
                "rating": 4.6,
                "stories": 15,
                "followers": 289,
                "bio": "Специалист по готической прозе"
            },
            {
                "id": 3,
                "name": "Николай Мрачный",
                "avatar": "/img/4a8f619e-b09e-4045-86d6-b6e8f9490542.jpg",
                "rating": 4.9,
                "stories": 31,
                "followers": 456,
                "bio": "Король паранормальных историй"
            },
            {
                "id": 4,
                "name": "Елена Призрачная",
                "avatar": "/img/4a8f619e-b09e-4045-86d6-b6e8f9490542.jpg",
                "rating": 4.7,
                "stories": 19,
                "followers": 312,
                "bio": "Создатель мистических сюжетов"
            }
        ]
        
        if author_id:
            author = next((a for a in mock_authors if a['id'] == int(author_id)), None)
            if author:
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps(author)
                }
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({'error': 'Author not found'})
            }
        
        if top:
            sorted_authors = sorted(mock_authors, key=lambda x: x['followers'], reverse=True)
            limit = int(top) if top.isdigit() else 4
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({'authors': sorted_authors[:limit]})
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'isBase64Encoded': False,
            'body': json.dumps({'authors': mock_authors})
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
