import json
from typing import Dict, Any
from datetime import datetime

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: API для лайков, комментариев и взаимодействия с рассказами
    Args: event - dict с httpMethod, body (storyId, action, userId, comment)
          context - object с request_id, function_name
    Returns: JSON результата операции
    '''
    method: str = event.get('httpMethod', 'POST')
    
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
    
    if method == 'POST':
        body_data = json.loads(event.get('body', '{}'))
        
        story_id = body_data.get('storyId')
        action = body_data.get('action')
        user_id = body_data.get('userId')
        
        if not story_id or not action or not user_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({
                    'error': 'Missing required fields',
                    'required': ['storyId', 'action', 'userId']
                })
            }
        
        if action == 'like':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({
                    'success': True,
                    'storyId': story_id,
                    'likes': 90,
                    'liked': True,
                    'message': 'Story liked successfully'
                })
            }
        
        if action == 'comment':
            comment_text = body_data.get('comment')
            if not comment_text:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'Comment text is required'})
                }
            
            new_comment = {
                'id': 123,
                'storyId': story_id,
                'userId': user_id,
                'text': comment_text,
                'createdAt': datetime.now().isoformat(),
                'likes': 0
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
                    'comment': new_comment,
                    'message': 'Comment added successfully'
                })
            }
        
        if action == 'view':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({
                    'success': True,
                    'storyId': story_id,
                    'views': 1251,
                    'message': 'View recorded'
                })
            }
        
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'isBase64Encoded': False,
            'body': json.dumps({
                'error': 'Invalid action',
                'validActions': ['like', 'comment', 'view']
            })
        }
    
    if method == 'GET':
        params = event.get('queryStringParameters', {}) or {}
        story_id = params.get('storyId')
        
        if not story_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({'error': 'storyId parameter required'})
            }
        
        mock_comments = [
            {
                'id': 1,
                'userId': 5,
                'userName': 'Иван Читатель',
                'text': 'Потрясающая история! Мурашки по коже.',
                'createdAt': '2024-01-16T10:30:00',
                'likes': 12
            },
            {
                'id': 2,
                'userId': 8,
                'userName': 'Анна Страшная',
                'text': 'Концовка превзошла все ожидания!',
                'createdAt': '2024-01-16T14:20:00',
                'likes': 8
            }
        ]
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'isBase64Encoded': False,
            'body': json.dumps({
                'storyId': story_id,
                'comments': mock_comments,
                'total': len(mock_comments)
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
