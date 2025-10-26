import json
import os
import hashlib
import secrets
from typing import Dict, Any
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_session_token() -> str:
    return secrets.token_urlsafe(32)

def get_user_from_session(cur, session_token: str) -> Dict[str, Any]:
    cur.execute('''
        SELECT u.id, u.email, u.username, u.full_name, u.avatar, u.role, u.bio
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.session_token = %s AND s.expires_at > NOW() AND u.is_active = true
    ''', (session_token,))
    return cur.fetchone()

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    Business: API для регистрации, авторизации, управления сессиями, профилем и админ-панели
    Args: event - dict с httpMethod, body, queryStringParameters, headers
          context - object с request_id, function_name
    Returns: JSON с токеном/профилем/статистикой/админ-данными
    '''
    method: str = event.get('httpMethod', 'POST')
    params = event.get('queryStringParameters', {}) or {}
    resource = params.get('resource', 'auth')
    
    headers_dict = event.get('headers', {})
    session_token_header = headers_dict.get('X-Session-Token') or headers_dict.get('x-session-token')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-Session-Token',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    if method == 'POST':
        body_data = json.loads(event.get('body', '{}'))
        action = body_data.get('action', 'login')
        
        if action == 'register':
            email = body_data.get('email')
            password = body_data.get('password')
            username = body_data.get('username')
            full_name = body_data.get('fullName', username)
            
            if not email or not password or not username:
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
                        'error': 'Missing required fields',
                        'required': ['email', 'password', 'username']
                    })
                }
            
            password_hash = hash_password(password)
            
            cur.execute('''
                SELECT id FROM users WHERE email = %s OR username = %s
            ''', (email, username))
            
            if cur.fetchone():
                cur.close()
                conn.close()
                return {
                    'statusCode': 409,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'User already exists'})
                }
            
            cur.execute('''
                INSERT INTO users (email, password_hash, username, full_name, role)
                VALUES (%s, %s, %s, %s, 'user')
                RETURNING id, email, username, full_name, avatar, role, created_at::text
            ''', (email, password_hash, username, full_name))
            
            user = cur.fetchone()
            
            session_token = generate_session_token()
            expires_at = datetime.now() + timedelta(days=30)
            
            cur.execute('''
                INSERT INTO sessions (user_id, session_token, expires_at)
                VALUES (%s, %s, %s)
            ''', (user['id'], session_token, expires_at))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {
                'statusCode': 201,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({
                    'success': True,
                    'token': session_token,
                    'user': {
                        'id': user['id'],
                        'email': user['email'],
                        'username': user['username'],
                        'fullName': user['full_name'],
                        'avatar': user['avatar'],
                        'role': user['role']
                    }
                })
            }
        
        if action == 'login':
            email = body_data.get('email')
            password = body_data.get('password')
            
            if not email or not password:
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
                        'error': 'Missing email or password'
                    })
                }
            
            password_hash = hash_password(password)
            
            cur.execute('''
                SELECT id, email, username, full_name, avatar, role, is_active
                FROM users
                WHERE email = %s AND password_hash = %s
            ''', (email, password_hash))
            
            user = cur.fetchone()
            
            if not user:
                cur.close()
                conn.close()
                return {
                    'statusCode': 401,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'Invalid credentials'})
                }
            
            if not user['is_active']:
                cur.close()
                conn.close()
                return {
                    'statusCode': 403,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'Account is disabled'})
                }
            
            session_token = generate_session_token()
            expires_at = datetime.now() + timedelta(days=30)
            
            cur.execute('''
                INSERT INTO sessions (user_id, session_token, expires_at)
                VALUES (%s, %s, %s)
            ''', (user['id'], session_token, expires_at))
            
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
                    'token': session_token,
                    'user': {
                        'id': user['id'],
                        'email': user['email'],
                        'username': user['username'],
                        'fullName': user['full_name'],
                        'avatar': user['avatar'],
                        'role': user['role']
                    }
                })
            }
    
    if method == 'GET':
        headers = event.get('headers', {})
        session_token = headers.get('X-Session-Token') or headers.get('x-session-token')
        
        if not session_token:
            cur.close()
            conn.close()
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({'error': 'No session token provided'})
            }
        
        user = get_user_from_session(cur, session_token)
        
        if not user:
            cur.close()
            conn.close()
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({'error': 'Invalid or expired session'})
            }
        
        if resource == 'profile':
            username = params.get('username')
            
            if username:
                cur.execute('''
                    SELECT id, username, full_name, avatar, bio, role, created_at::text
                    FROM users
                    WHERE username = %s AND is_active = true
                ''', (username,))
                profile_user = cur.fetchone()
                
                if not profile_user:
                    cur.close()
                    conn.close()
                    return {
                        'statusCode': 404,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'isBase64Encoded': False,
                        'body': json.dumps({'error': 'User not found'})
                    }
                
                user_id = profile_user['id']
            else:
                profile_user = user
                user_id = user['id']
            
            cur.execute('SELECT COUNT(*) as count FROM stories WHERE created_by = %s', (user_id,))
            stories_count = cur.fetchone()['count']
            
            cur.execute('''
                SELECT s.id, s.title, s.rating, s.views, s.likes, s.published_at::text as published_at
                FROM stories s
                WHERE s.created_by = %s
                ORDER BY s.published_at DESC
                LIMIT 10
            ''', (user_id,))
            recent_stories = cur.fetchall()
            
            cur.execute('SELECT COUNT(*) as count FROM comments WHERE created_by = %s', (user_id,))
            comments_count = cur.fetchone()['count']
            
            cur.close()
            conn.close()
            
            stories_list = []
            for story in recent_stories:
                stories_list.append({
                    'id': story['id'],
                    'title': story['title'],
                    'rating': float(story['rating']) if story['rating'] else 0,
                    'views': story['views'],
                    'likes': story['likes'],
                    'publishedAt': story['published_at']
                })
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({
                    'user': {
                        'id': profile_user['id'],
                        'username': profile_user['username'],
                        'fullName': profile_user['full_name'],
                        'avatar': profile_user['avatar'],
                        'bio': profile_user['bio'],
                        'role': profile_user['role'],
                        'createdAt': profile_user.get('created_at')
                    },
                    'stats': {
                        'storiesCount': stories_count,
                        'commentsCount': comments_count
                    },
                    'recentStories': stories_list
                })
            }
        
        if resource == 'admin':
            if user['role'] != 'admin':
                cur.close()
                conn.close()
                return {
                    'statusCode': 403,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'Admin access required'})
                }
            
            admin_resource = params.get('admin_resource', 'stats')
            
            if admin_resource == 'stats':
                cur.execute('SELECT COUNT(*) as count FROM users')
                users_count = cur.fetchone()['count']
                
                cur.execute('SELECT COUNT(*) as count FROM stories')
                stories_count = cur.fetchone()['count']
                
                cur.execute('SELECT COUNT(*) as count FROM comments')
                comments_count = cur.fetchone()['count']
                
                cur.execute("SELECT COUNT(*) as count FROM users WHERE created_at > NOW() - INTERVAL '7 days'")
                new_users = cur.fetchone()['count']
                
                cur.execute("SELECT COUNT(*) as count FROM stories WHERE published_at > NOW() - INTERVAL '7 days'")
                new_stories = cur.fetchone()['count']
                
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
                        'stats': {
                            'totalUsers': users_count,
                            'totalStories': stories_count,
                            'totalComments': comments_count,
                            'newUsersWeek': new_users,
                            'newStoriesWeek': new_stories
                        }
                    })
                }
            
            if admin_resource == 'users':
                limit = int(params.get('limit', 50))
                offset = int(params.get('offset', 0))
                
                cur.execute('''
                    SELECT id, username, email, full_name, role, is_active, 
                           created_at::text, updated_at::text
                    FROM users
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                ''', (limit, offset))
                
                users_list = cur.fetchall()
                
                cur.execute('SELECT COUNT(*) as count FROM users')
                total = cur.fetchone()['count']
                
                cur.close()
                conn.close()
                
                result_users = []
                for u in users_list:
                    result_users.append({
                        'id': u['id'],
                        'username': u['username'],
                        'email': u['email'],
                        'fullName': u['full_name'],
                        'role': u['role'],
                        'isActive': u['is_active'],
                        'createdAt': u['created_at'],
                        'updatedAt': u['updated_at']
                    })
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({
                        'users': result_users,
                        'total': total,
                        'limit': limit,
                        'offset': offset
                    })
                }
            
            if admin_resource == 'stories':
                limit = int(params.get('limit', 50))
                offset = int(params.get('offset', 0))
                
                cur.execute('''
                    SELECT s.id, s.title, s.views, s.likes, s.comments_count, 
                           s.published_at::text, u.username as author
                    FROM stories s
                    LEFT JOIN users u ON s.created_by = u.id
                    ORDER BY s.published_at DESC
                    LIMIT %s OFFSET %s
                ''', (limit, offset))
                
                stories_list = cur.fetchall()
                
                cur.execute('SELECT COUNT(*) as count FROM stories')
                total = cur.fetchone()['count']
                
                cur.close()
                conn.close()
                
                result_stories = []
                for s in stories_list:
                    result_stories.append({
                        'id': s['id'],
                        'title': s['title'],
                        'author': s['author'],
                        'views': s['views'],
                        'likes': s['likes'],
                        'comments': s['comments_count'],
                        'publishedAt': s['published_at']
                    })
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({
                        'stories': result_stories,
                        'total': total,
                        'limit': limit,
                        'offset': offset
                    })
                }
        
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
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'username': user['username'],
                    'fullName': user['full_name'],
                    'avatar': user['avatar'],
                    'role': user['role'],
                    'bio': user['bio']
                }
            })
        }
    
    if method == 'PUT':
        if not session_token_header:
            cur.close()
            conn.close()
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({'error': 'Unauthorized'})
            }
        
        user = get_user_from_session(cur, session_token_header)
        
        if not user:
            cur.close()
            conn.close()
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({'error': 'Invalid session'})
            }
        
        body_data = json.loads(event.get('body', '{}'))
        
        if resource == 'admin' and user['role'] == 'admin':
            user_id_to_update = body_data.get('userId')
            is_active = body_data.get('isActive')
            role = body_data.get('role')
            
            if not user_id_to_update:
                cur.close()
                conn.close()
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'userId required'})
                }
            
            updates = []
            params_list = []
            
            if is_active is not None:
                updates.append('is_active = %s')
                params_list.append(is_active)
            
            if role:
                updates.append('role = %s')
                params_list.append(role)
            
            if updates:
                params_list.append(user_id_to_update)
                query = f'''
                    UPDATE users
                    SET {', '.join(updates)}, updated_at = NOW()
                    WHERE id = %s
                    RETURNING id, username, role, is_active
                '''
                
                cur.execute(query, params_list)
                updated_user = cur.fetchone()
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
                        'user': {
                            'id': updated_user['id'],
                            'username': updated_user['username'],
                            'role': updated_user['role'],
                            'isActive': updated_user['is_active']
                        }
                    })
                }
        
        full_name = body_data.get('fullName')
        bio = body_data.get('bio')
        avatar = body_data.get('avatar')
        
        update_fields = []
        params_list = []
        
        if full_name is not None:
            update_fields.append('full_name = %s')
            params_list.append(full_name)
        
        if bio is not None:
            update_fields.append('bio = %s')
            params_list.append(bio)
        
        if avatar is not None:
            update_fields.append('avatar = %s')
            params_list.append(avatar)
        
        if not update_fields:
            cur.close()
            conn.close()
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({'error': 'No fields to update'})
            }
        
        update_fields.append('updated_at = NOW()')
        params_list.append(user['id'])
        
        query = f'''
            UPDATE users
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, username, full_name, avatar, bio, role
        '''
        
        cur.execute(query, params_list)
        updated_user = cur.fetchone()
        
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
                'user': {
                    'id': updated_user['id'],
                    'username': updated_user['username'],
                    'fullName': updated_user['full_name'],
                    'avatar': updated_user['avatar'],
                    'bio': updated_user['bio'],
                    'role': updated_user['role']
                }
            })
        }
    
    if method == 'DELETE':
        headers = event.get('headers', {})
        session_token = headers.get('X-Session-Token') or headers.get('x-session-token')
        
        if session_token:
            cur.execute('''
                DELETE FROM sessions WHERE session_token = %s
            ''', (session_token,))
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
            'body': json.dumps({'success': True, 'message': 'Logged out'})
        }
    
    cur.close()
    conn.close()
    
    return {
        'statusCode': 405,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'isBase64Encoded': False,
        'body': json.dumps({'error': 'Method not allowed'})
    }