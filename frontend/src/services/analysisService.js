import apiClient from './api';

// 코드 분석 관련 API 서비스
export const analysisService = {
  // 코드 분석 및 피드백
  async analyzeCode(codeData) {
    try {
      const response = await apiClient.post('/analysis/feedback', codeData);
      return response.data;
    } catch (error) {
      console.error('Code Analysis API Error:', error);
      throw error;
    }
  },

  // 제출된 코드 분석
  async analyzeSubmittedCode(submissionId) {
    try {
      const response = await apiClient.post(`/analysis/feedback/submission/${submissionId}`);
      return response.data;
    } catch (error) {
      console.error('Submitted Code Analysis API Error:', error);
      throw error;
    }
  },

  // AI 최적 코드 생성
  async getOptimizedCode(optimizationData) {
    try {
      const response = await apiClient.post('/analysis/optimize', optimizationData);
      return response.data;
    } catch (error) {
      console.error('Code Optimization API Error:', error);
      throw error;
    }
  },

  // 사용자 분석 이력 조회
  async getAnalysisHistory(username = 'dlgusxor12') {
    try {
      const response = await apiClient.get(`/analysis/history/${username}`);
      return response.data;
    } catch (error) {
      console.error('Analysis History API Error:', error);
      throw error;
    }
  },

  // 알고리즘 설명 조회
  async getAlgorithmExplanation(algorithmType, difficultyLevel = 3) {
    try {
      const response = await apiClient.post('/analysis/algorithm/explain', {
        algorithm_type: algorithmType,
        difficulty_level: difficultyLevel
      });
      return response.data;
    } catch (error) {
      console.error('Algorithm Explanation API Error:', error);
      throw error;
    }
  },

  // 코드 비교 분석
  async compareCodes(comparisonData) {
    try {
      const response = await apiClient.post('/analysis/compare', comparisonData);
      return response.data;
    } catch (error) {
      console.error('Code Comparison API Error:', error);
      throw error;
    }
  },

  // 분석 서비스 상태 확인
  async getServiceStatus() {
    try {
      const response = await apiClient.get('/analysis/status');
      return response.data;
    } catch (error) {
      console.error('Analysis Service Status API Error:', error);
      throw error;
    }
  }
};