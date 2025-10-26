import json
import os
from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

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
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if author_id:
            cur.execute('''
                SELECT id, name, avatar, bio, rating, stories_count as stories, followers
                FROM authors
                WHERE id = %s
            ''', (int(author_id),))
            
            row = cur.fetchone()
            cur.close()
            conn.close()
            
            if not row:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'Author not found'})
                }
            
            author = {
                'id': row['id'],
                'name': row['name'],
                'avatar': row['avatar'],
                'bio': row['bio'],
                'rating': float(row['rating']) if row['rating'] else 0,
                'stories': row['stories'],
                'followers': row['followers']
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps(author)
            }
        
        limit_clause = ''
        if top and top.isdigit():
            limit_clause = f'LIMIT {int(top)}'
        
        cur.execute(f'''
            SELECT id, name, avatar, bio, rating, stories_count as stories, followers
            FROM authors
            ORDER BY followers DESC
            {limit_clause}
        ''')
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        authors = []
        for row in rows:
            authors.append({
                'id': row['id'],
                'name': row['name'],
                'avatar': row['avatar'],
                'bio': row['bio'],
                'rating': float(row['rating']) if row['rating'] else 0,
                'stories': row['stories'],
                'followers': row['followers']
            })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'isBase64Encoded': False,
            'body': json.dumps({'authors': authors})
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