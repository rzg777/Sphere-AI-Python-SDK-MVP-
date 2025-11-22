import { demoAuthServer } from './demoAuthServer';
import { AdminSummary, AuthTokens, User } from './auth.types';

class AuthService {
  private readonly ACCESS_TOKEN_KEY = 'access_token';
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private currentUser: User | null = null;

  constructor() {
    if (typeof window !== 'undefined') {
      this.accessToken = window.localStorage.getItem(this.ACCESS_TOKEN_KEY);
    }
  }

  private persistAccessToken(token: string | null) {
    if (typeof window === 'undefined') {
      return;
    }
    if (token) {
      window.localStorage.setItem(this.ACCESS_TOKEN_KEY, token);
    } else {
      window.localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    }
  }

  private setSession(tokens: AuthTokens, user?: User) {
    this.accessToken = tokens.accessToken;
    this.refreshToken = tokens.refreshToken;
    this.persistAccessToken(tokens.accessToken);
    if (user) {
      this.currentUser = user;
    }
  }

  getCachedUser(): User | null {
    return this.currentUser;
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  getRefreshToken(): string | null {
    return this.refreshToken;
  }

  async login(email: string, password: string): Promise<AuthTokens> {
    const response = await demoAuthServer.login(email, password);
    this.setSession({ accessToken: response.accessToken, refreshToken: response.refreshToken }, response.user);
    return { accessToken: response.accessToken, refreshToken: response.refreshToken };
  }

  async logout(): Promise<void> {
    await demoAuthServer.revokeSession(this.refreshToken);
    this.accessToken = null;
    this.refreshToken = null;
    this.currentUser = null;
    this.persistAccessToken(null);
  }

  async getProfile(force = false): Promise<User | null> {
    if (!force && this.currentUser) {
      return this.currentUser;
    }
    if (!this.accessToken) {
      return null;
    }
    try {
      const profile = await demoAuthServer.getProfile(this.accessToken);
      this.currentUser = profile;
      return profile;
    } catch (error) {
      const refreshed = await this.tryRefreshTokens();
      if (!refreshed) {
        return null;
      }
      const profile = await demoAuthServer.getProfile(this.accessToken!);
      this.currentUser = profile;
      return profile;
    }
  }

  private async tryRefreshTokens(): Promise<boolean> {
    if (!this.refreshToken) {
      await this.logout();
      return false;
    }
    try {
      const tokens = await demoAuthServer.refreshSession(this.refreshToken);
      this.setSession(tokens);
      return true;
    } catch {
      await this.logout();
      return false;
    }
  }

  async refreshTokens(): Promise<AuthTokens> {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }
    const tokens = await demoAuthServer.refreshSession(this.refreshToken);
    this.setSession(tokens);
    return tokens;
  }

  async isAuthenticated(): Promise<boolean> {
    const profile = await this.getProfile();
    return Boolean(profile);
  }

  async hasRole(role: User['role']): Promise<boolean> {
    const profile = await this.getProfile();
    return profile?.role === role;
  }

  async getAdminSummary(): Promise<AdminSummary | null> {
    if (!this.accessToken) {
      return null;
    }
    try {
      return await demoAuthServer.getAdminSummary(this.accessToken);
    } catch (error) {
      const refreshed = await this.tryRefreshTokens();
      if (!refreshed || !this.accessToken) {
        return null;
      }
      return demoAuthServer.getAdminSummary(this.accessToken);
    }
  }
}

export const authService = new AuthService();
export type { User, AuthTokens, AdminSummary } from './auth.types';
