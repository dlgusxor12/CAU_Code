import apiClient from './api';

/**
 * 인증 관련 API 서비스
 * Phase 3: Frontend Authentication UI
 */

class AuthService {
  constructor() {
    this.tokenKey = 'cau_code_access_token';
    this.refreshTokenKey = 'cau_code_refresh_token';
    this.userKey = 'cau_code_user';
  }

  // 로컬 스토리지에서 토큰 관리
  getAccessToken() {
    return localStorage.getItem(this.tokenKey);
  }

  getRefreshToken() {
    return localStorage.getItem(this.refreshTokenKey);
  }

  getStoredUser() {
    const userData = localStorage.getItem(this.userKey);
    return userData ? JSON.parse(userData) : null;
  }

  setTokens(accessToken, refreshToken, user) {
    localStorage.setItem(this.tokenKey, accessToken);
    localStorage.setItem(this.refreshTokenKey, refreshToken);
    localStorage.setItem(this.userKey, JSON.stringify(user));
  }

  clearTokens() {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.refreshTokenKey);
    localStorage.removeItem(this.userKey);
  }

  // Google OAuth 로그인
  async googleLogin(idToken) {
    try {
      const response = await apiClient.post('/auth/google-login', {
        id_token: idToken
      });

      const { access_token, refresh_token, user } = response.data;

      // 토큰과 사용자 정보 저장
      this.setTokens(access_token, refresh_token, user);

      // axios 인터셉터에 토큰 설정
      this.setupAxiosInterceptors();

      return { success: true, user, message: '로그인 성공' };
    } catch (error) {
      console.error('Google 로그인 실패:', error);
      return {
        success: false,
        error: error.response?.data?.detail || '로그인에 실패했습니다.'
      };
    }
  }

  // 로그아웃
  async logout() {
    try {
      const accessToken = this.getAccessToken();
      if (accessToken) {
        await apiClient.post('/auth/logout', {}, {
          headers: { Authorization: `Bearer ${accessToken}` }
        });
      }
    } catch (error) {
      console.error('로그아웃 API 호출 실패:', error);
    } finally {
      // 로컬 토큰 정리
      this.clearTokens();
      // axios 인터셉터에서 토큰 제거
      delete apiClient.defaults.headers.common['Authorization'];
    }
  }

  // 토큰 갱신
  async refreshAccessToken() {
    try {
      const refreshToken = this.getRefreshToken();
      if (!refreshToken) {
        throw new Error('Refresh token not found');
      }

      // 인터셉터 무한루프 방지를 위해 _retry 플래그 추가
      const response = await apiClient.post('/auth/refresh-token', {}, {
        headers: { Authorization: `Bearer ${refreshToken}` },
        _retry: true // 인터셉터에서 이 요청은 재시도하지 않음
      });

      const { access_token, refresh_token: newRefreshToken, user } = response.data;

      // 새 토큰들 저장
      this.setTokens(access_token, newRefreshToken, user);

      return access_token;
    } catch (error) {
      console.error('토큰 갱신 실패:', error);
      // 갱신 실패 시 로그아웃
      this.clearTokens();
      throw error;
    }
  }

  // 현재 사용자 정보 조회
  async getCurrentUser() {
    try {
      const response = await apiClient.get('/auth/me');
      const user = response.data;

      // 로컬 스토리지 사용자 정보 업데이트
      localStorage.setItem(this.userKey, JSON.stringify(user));

      return user;
    } catch (error) {
      console.error('사용자 정보 조회 실패:', error);
      throw error;
    }
  }

  // solved.ac 프로필 인증 요청
  async requestSolvedacVerification(solvedacUsername) {
    try {
      const response = await apiClient.post('/auth/solvedac-verify', {
        solvedac_username: solvedacUsername
      });

      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('프로필 인증 요청 실패:', error);
      return {
        success: false,
        error: error.response?.data?.detail || '인증 요청에 실패했습니다.'
      };
    }
  }

  // 인증 상태 확인
  async checkVerificationStatus(verificationCode) {
    try {
      const response = await apiClient.post('/auth/check-verification', {
        verification_code: verificationCode
      });

      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('인증 상태 확인 실패:', error);

      // 429 오류 처리
      if (error.response?.status === 429) {
        const rateLimitData = error.response.data?.detail;
        return {
          success: false,
          error: `요청이 너무 많습니다. ${rateLimitData?.window_seconds || 60}초 후에 다시 시도해주세요.`,
          rateLimited: true,
          retryAfter: rateLimitData?.window_seconds || 60
        };
      }

      return {
        success: false,
        error: error.response?.data?.detail || '인증 상태 확인에 실패했습니다.'
      };
    }
  }

  // 사용자 인증 상태 조회
  async getVerificationStatus() {
    try {
      const response = await apiClient.get('/auth/verification-status');
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('인증 상태 조회 실패:', error);
      return {
        success: false,
        error: error.response?.data?.detail || '인증 상태 조회에 실패했습니다.'
      };
    }
  }

  // axios 인터셉터 설정 (토큰 자동 첨부 및 갱신)
  setupAxiosInterceptors() {
    const accessToken = this.getAccessToken();
    if (accessToken) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
    }

    // 응답 인터셉터 - 401 오류 시 토큰 갱신 시도
    apiClient.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const newAccessToken = await this.refreshAccessToken();
            originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
            apiClient.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;

            return apiClient(originalRequest);
          } catch (refreshError) {
            // 토큰 갱신 실패 시 로그인 페이지로 리다이렉트
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // 인증 상태 확인
  isAuthenticated() {
    const accessToken = this.getAccessToken();
    const user = this.getStoredUser();
    return !!(accessToken && user);
  }

  // 프로필 인증 완료 여부 확인
  isProfileVerified() {
    const user = this.getStoredUser();
    return user?.profile_verified || false;
  }

  // 애플리케이션 시작 시 토큰 설정
  initializeAuth() {
    const accessToken = this.getAccessToken();
    if (accessToken) {
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
      this.setupAxiosInterceptors();
      return true;
    }
    return false;
  }
}

// 싱글톤 인스턴스 생성
const authService = new AuthService();

export default authService;