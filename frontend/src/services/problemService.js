import apiClient from './api';

// 문제 관련 API 서비스
export const problemService = {
  // 문제 추천 조회
  async getRecommendations(params = {}) {
    try {
      const {
        username = 'dlgusxor12',
        mode = 'adaptive',
        count = 10,
        tier_min = null,
        tier_max = null,
        algorithm = null,
        difficulty_class = null
      } = params;

      const queryParams = new URLSearchParams({
        username,
        mode,
        count: count.toString()
      });

      if (tier_min !== null) queryParams.append('tier_min', tier_min.toString());
      if (tier_max !== null) queryParams.append('tier_max', tier_max.toString());
      if (algorithm) queryParams.append('algorithm', algorithm);
      if (difficulty_class !== null) queryParams.append('difficulty_class', difficulty_class.toString());

      const response = await apiClient.get(`/problems/recommendations?${queryParams}`);
      return response.data;
    } catch (error) {
      console.error('Problem Recommendations API Error:', error);
      throw error;
    }
  },

  // 문제 추천 통계 조회
  async getRecommendationStats(username = 'dlgusxor12') {
    try {
      const response = await apiClient.get(`/problems/stats?username=${username}`);
      return response.data;
    } catch (error) {
      console.error('Problem Stats API Error:', error);
      throw error;
    }
  },

  // 필터 옵션 조회
  async getFilterOptions() {
    try {
      const response = await apiClient.get('/problems/filter-options');
      return response.data;
    } catch (error) {
      console.error('Filter Options API Error:', error);
      throw error;
    }
  },

  // 문제 검색
  async searchProblems(searchParams) {
    try {
      const response = await apiClient.post('/problems/search', searchParams);
      return response.data;
    } catch (error) {
      console.error('Problem Search API Error:', error);
      throw error;
    }
  },

  // 특정 문제 정보 조회
  async getProblemInfo(problemId) {
    try {
      const response = await apiClient.get(`/problems/${problemId}`);
      return response.data;
    } catch (error) {
      console.error('Problem Info API Error:', error);
      throw error;
    }
  },

  // 문제 해결 여부 검증
  async verifyProblemSolution(problemId, username = 'dlgusxor12') {
    try {
      const response = await apiClient.post(`/problems/${problemId}/verify`, {
        username
      });
      return response.data;
    } catch (error) {
      console.error('Problem Verification API Error:', error);
      throw error;
    }
  }
};