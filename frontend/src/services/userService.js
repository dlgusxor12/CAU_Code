import apiClient from './api';

// 사용자 관련 API 서비스
export const userService = {
  // 대시보드 정보 조회
  async getDashboard(username = 'dlgusxor12') {
    try {
      const response = await apiClient.get(`/users/dashboard/${username}`);
      return response.data;
    } catch (error) {
      console.error('Dashboard API Error:', error);
      // 에러 시 더미 데이터 반환
      return {
        status: 'error',
        message: 'Dashboard API 연결 실패',
        data: null
      };
    }
  },

  // 사용자 통계 조회
  async getUserStats(username = 'dlgusxor12') {
    try {
      const response = await apiClient.get(`/users/stats/${username}`);
      return response.data;
    } catch (error) {
      console.error('User Stats API Error:', error);
      // 에러 시 더미 데이터 반환
      return {
        status: 'error',
        message: 'User Stats API 연결 실패',
        data: {
          current_tier: 15,
          tier_name: 'Gold V',
          rating: 1500,
          solved_count: 150,
          attempted_count: 200,
          success_rate: 75.0
        }
      };
    }
  },

  // 기여도 그래프 데이터 조회
  async getContribution(username = 'dlgusxor12') {
    try {
      const response = await apiClient.get(`/users/contribution/${username}`);
      return response.data;
    } catch (error) {
      console.error('Contribution API Error:', error);
      // 에러 시 더미 데이터 반환
      return {
        status: 'error',
        message: 'Contribution API 연결 실패',
        data: []
      };
    }
  },

  // 최근 활동 조회
  async getRecentActivities(username = 'dlgusxor12') {
    try {
      const response = await apiClient.get(`/users/activities/${username}`);
      return response.data;
    } catch (error) {
      console.error('Recent Activities API Error:', error);
      // 에러 시 더미 데이터 반환
      return {
        status: 'error',
        message: 'Recent Activities API 연결 실패',
        data: []
      };
    }
  },

  // 주간 통계 조회
  async getWeeklyStats(username = 'dlgusxor12') {
    try {
      const response = await apiClient.get(`/users/weekly-stats/${username}`);
      return response.data;
    } catch (error) {
      console.error('Weekly Stats API Error:', error);
      // 에러 시 더미 데이터 반환
      return {
        status: 'error',
        message: 'Weekly Stats API 연결 실패',
        data: {
          problems_solved: 12,
          study_time: 8.5,
          streak_days: 5,
          accuracy_rate: 85.2
        }
      };
    }
  },

  // 오늘의 문제 조회
  async getTodayProblems(username = 'dlgusxor12') {
    try {
      const response = await apiClient.get(`/users/todays-problems/${username}`);
      return response.data;
    } catch (error) {
      console.error('Today Problems API Error:', error);
      // 에러 시 더미 데이터 반환
      return {
        status: 'error',
        message: 'Today Problems API 연결 실패',
        data: []
      };
    }
  },

  // 복습 문제 조회
  async getReviewProblems(username = 'dlgusxor12') {
    try {
      const response = await apiClient.get(`/users/review-problems/${username}`);
      return response.data;
    } catch (error) {
      console.error('Review Problems API Error:', error);
      // 에러 시 더미 데이터 반환
      return {
        status: 'error',
        message: 'Review Problems API 연결 실패',
        data: []
      };
    }
  }
};