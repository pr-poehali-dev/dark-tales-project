const AUTH_API = 'https://functions.poehali.dev/52f7c095-46c6-423b-a7f1-107fcec4ad8d';
const SESSION_KEY = 'horror_session_token';

export interface User {
  id: number;
  email: string;
  username: string;
  fullName: string;
  avatar: string | null;
  role: string;
  bio?: string;
}

export const authService = {
  async register(email: string, password: string, username: string, fullName: string) {
    const response = await fetch(AUTH_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'register',
        email,
        password,
        username,
        fullName
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Registration failed');
    }

    if (data.token) {
      localStorage.setItem(SESSION_KEY, data.token);
    }

    return data;
  },

  async login(email: string, password: string) {
    const response = await fetch(AUTH_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'login',
        email,
        password
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Login failed');
    }

    if (data.token) {
      localStorage.setItem(SESSION_KEY, data.token);
    }

    return data;
  },

  async getCurrentUser(): Promise<User | null> {
    const token = localStorage.getItem(SESSION_KEY);

    if (!token) {
      return null;
    }

    try {
      const response = await fetch(AUTH_API, {
        method: 'GET',
        headers: {
          'X-Session-Token': token
        }
      });

      if (!response.ok) {
        localStorage.removeItem(SESSION_KEY);
        return null;
      }

      const data = await response.json();
      return data.user;
    } catch {
      localStorage.removeItem(SESSION_KEY);
      return null;
    }
  },

  async logout() {
    const token = localStorage.getItem(SESSION_KEY);

    if (token) {
      try {
        await fetch(AUTH_API, {
          method: 'DELETE',
          headers: {
            'X-Session-Token': token
          }
        });
      } catch (e) {
        console.error('Logout error:', e);
      }
    }

    localStorage.removeItem(SESSION_KEY);
  },

  getToken(): string | null {
    return localStorage.getItem(SESSION_KEY);
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem(SESSION_KEY);
  }
};