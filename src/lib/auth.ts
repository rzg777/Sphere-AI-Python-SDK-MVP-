import { jwtDecode } from 'jwt-decode';

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'admin';
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export interface DecodedToken {
  sub: string;
  email: string;
  name: string;
  role: string;
  exp: number;
}

class AuthService {
  private readonly ACCESS_TOKEN_KEY = 'access_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';

  // Mock user database - in a real app, this would be an API
  private mockUsers = [
    {
      id: '1',
      email: 'user@example.com',
      password: 'password123',
      name: 'Demo User',
      role: 'user' as const
    },
    {
      id: '2',
      email: 'admin@example.com',
      password: 'admin123',
      name: 'Admin User',
      role: 'admin' as const
    }
  ];

  // Generate a simple JWT-like token (in real app, use proper JWT from backend)
  private generateToken(user: any): string {
    const payload = {
      sub: user.id,
      email: user.email,
      name: user.name,
      role: user.role,
      exp: Math.floor(Date.now() / 1000) + (60 * 60) // 1 hour expiry
    };
    return btoa(JSON.stringify(payload)); // Simple base64 encoding for demo
  }

  async login(email: string, password: string): Promise<AuthTokens> {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    const user = this.mockUsers.find(u => u.email === email && u.password === password);
    
    if (!user) {
      throw new Error('Invalid email or password');
    }

    const accessToken = this.generateToken(user);
    const refreshToken = this.generateToken({ ...user, isRefresh: true });

    localStorage.setItem(this.ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);

    return { accessToken, refreshToken };
  }

  logout(): void {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
  }

  getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  isAuthenticated(): boolean {
    const token = this.getAccessToken();
    if (!token) return false;

    try {
      const decoded = this.decodeToken(token);
      return decoded.exp > Math.floor(Date.now() / 1000);
    } catch {
      return false;
    }
  }

  decodeToken(token: string): DecodedToken {
    try {
      return JSON.parse(atob(token)) as DecodedToken;
    } catch {
      throw new Error('Invalid token');
    }
  }

  getCurrentUser(): User | null {
    const token = this.getAccessToken();
    if (!token) return null;

    try {
      const decoded = this.decodeToken(token);
      return {
        id: decoded.sub,
        email: decoded.email,
        name: decoded.name,
        role: decoded.role as 'user' | 'admin'
      };
    } catch {
      return null;
    }
  }

  hasRole(role: string): boolean {
    const user = this.getCurrentUser();
    return user?.role === role;
  }

  // Mock token refresh - in real app, call your refresh endpoint
  async refreshTokens(): Promise<AuthTokens> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const decoded = this.decodeToken(refreshToken);
      const user = this.mockUsers.find(u => u.id === decoded.sub);
      
      if (!user) {
        throw new Error('User not found');
      }

      const newAccessToken = this.generateToken(user);
      localStorage.setItem(this.ACCESS_TOKEN_KEY, newAccessToken);

      return {
        accessToken: newAccessToken,
        refreshToken
      };
    } catch {
      this.logout();
      throw new Error('Token refresh failed');
    }
  }
}

export const authService = new AuthService();