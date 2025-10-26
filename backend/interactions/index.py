import json
import os
from typing import Dict, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

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
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if action == 'like':
            cur.execute('''
                INSERT INTO likes (story_id, user_id)
                VALUES (%s, %s)
                ON CONFLICT (story_id, user_id) DO NOTHING
                RETURNING id
            ''', (int(story_id), int(user_id)))
            
            inserted = cur.fetchone()
            
            if inserted:
                cur.execute('''
                    UPDATE stories
                    SET likes = likes + 1
                    WHERE id = %s
                    RETURNING likes
                ''', (int(story_id),))
                result = cur.fetchone()
                conn.commit()
                cur.close()
                conn.close()
                
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
                        'likes': result['likes'],
                        'liked': True,
                        'message': 'Story liked successfully'
                    })
                }
            else:
                cur.close()
                conn.close()
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({
                        'success': False,
                        'message': 'Already liked'
                    })
                }
        
        if action == 'comment':
            comment_text = body_data.get('comment')
            user_name = body_data.get('userName', f'User{user_id}')
            
            if not comment_text:
                cur.close()
                conn.close()
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'Comment text is required'})
                }
            
            cur.execute('''
                INSERT INTO comments (story_id, user_id, user_name, text)
                VALUES (%s, %s, %s, %s)
                RETURNING id, created_at::text as created_at, likes
            ''', (int(story_id), int(user_id), user_name, comment_text))
            
            result = cur.fetchone()
            
            cur.execute('''
                UPDATE stories
                SET comments_count = comments_count + 1
                WHERE id = %s
            ''', (int(story_id),))
            
            conn.commit()
            cur.close()
            conn.close()
            
            new_comment = {
                'id': result['id'],
                'storyId': story_id,
                'userId': user_id,
                'userName': user_name,
                'text': comment_text,
                'createdAt': result['created_at'],
                'likes': result['likes']
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
            cur.execute('''
                UPDATE stories
                SET views = views + 1
                WHERE id = %s
                RETURNING views
            ''', (int(story_id),))
            
            result = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            
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
                    'views': result['views'] if result else 0,
                    'message': 'View recorded'
                })
            }
        
        cur.close()
        conn.close()
        
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
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute('''
            SELECT id, user_id as "userId", user_name as "userName", text, 
                   likes, created_at::text as "createdAt"
            FROM comments
            WHERE story_id = %s
            ORDER BY created_at DESC
        ''', (int(story_id),))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        comments = []
        for row in rows:
            comments.append({
                'id': row['id'],
                'userId': row['userId'],
                'userName': row['userName'],
                'text': row['text'],
                'likes': row['likes'],
                'createdAt': row['createdAt']
            })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'isBase64Encoded': False,
            'body': json.dumps({
                'storyId': story_id,
                'comments': comments,
                'total': len(comments)
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