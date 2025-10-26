import json
import os
from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

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
        
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if story_id:
            cur.execute('''
                SELECT s.id, s.title, s.description, s.content, s.rating, s.views, 
                       s.likes, s.comments_count as comments, s.reading_time as "readingTime",
                       s.published_at::text as "publishedAt",
                       a.id as author_id, a.name as author_name, a.avatar as author_avatar,
                       a.rating as author_rating, a.stories_count as author_stories,
                       array_agg(sg.genre) as genre
                FROM stories s
                JOIN authors a ON s.author_id = a.id
                LEFT JOIN story_genres sg ON s.id = sg.story_id
                WHERE s.id = %s
                GROUP BY s.id, a.id
            ''', (int(story_id),))
            
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
                    'body': json.dumps({'error': 'Story not found'})
                }
            
            story = {
                'id': row['id'],
                'title': row['title'],
                'description': row['description'],
                'content': row['content'],
                'rating': float(row['rating']) if row['rating'] else 0,
                'views': row['views'],
                'likes': row['likes'],
                'comments': row['comments'],
                'readingTime': row['readingTime'],
                'publishedAt': row['publishedAt'],
                'genre': [g for g in row['genre'] if g],
                'author': {
                    'id': row['author_id'],
                    'name': row['author_name'],
                    'avatar': row['author_avatar'],
                    'rating': float(row['author_rating']) if row['author_rating'] else 0,
                    'stories': row['author_stories']
                }
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps(story)
            }
        
        order_clause = 's.published_at DESC'
        if sort_by == 'popular':
            order_clause = 's.views DESC'
        elif sort_by == 'rating':
            order_clause = 's.rating DESC'
        
        genre_filter = ''
        genre_params = []
        if genre:
            genre_filter = 'WHERE %s = ANY(array_agg(sg.genre))'
            genre_params = [genre]
        
        query = f'''
            SELECT s.id, s.title, s.description, s.rating, s.views, 
                   s.likes, s.comments_count as comments, s.reading_time as "readingTime",
                   s.published_at::text as "publishedAt",
                   a.id as author_id, a.name as author_name, a.avatar as author_avatar,
                   a.rating as author_rating, a.stories_count as author_stories,
                   array_agg(sg.genre) as genre
            FROM stories s
            JOIN authors a ON s.author_id = a.id
            LEFT JOIN story_genres sg ON s.id = sg.story_id
            GROUP BY s.id, a.id
            ORDER BY {order_clause}
        '''
        
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        stories = []
        for row in rows:
            genre_list = [g for g in row['genre'] if g]
            if genre and genre not in genre_list:
                continue
                
            stories.append({
                'id': row['id'],
                'title': row['title'],
                'description': row['description'],
                'rating': float(row['rating']) if row['rating'] else 0,
                'views': row['views'],
                'likes': row['likes'],
                'comments': row['comments'],
                'readingTime': row['readingTime'],
                'publishedAt': row['publishedAt'],
                'genre': genre_list,
                'author': {
                    'id': row['author_id'],
                    'name': row['author_name'],
                    'avatar': row['author_avatar'],
                    'rating': float(row['author_rating']) if row['author_rating'] else 0,
                    'stories': row['author_stories']
                }
            })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'isBase64Encoded': False,
            'body': json.dumps({'stories': stories, 'total': len(stories)})
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
