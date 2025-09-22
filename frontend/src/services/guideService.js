import apiClient from './api';

// 가이드 페이지 관련 API 서비스
export const guideService = {
  // 문제 상세 정보 조회
  async getProblemDetail(problemId) {
    try {
      const response = await apiClient.get(`/guide/problem/${problemId}`);
      return response.data;
    } catch (error) {
      console.error('Problem Detail API Error:', error);
      throw error;
    }
  },

  // 코드 제출
  async submitCode(codeData) {
    try {
      const response = await apiClient.post('/guide/submit-code', codeData);
      return response.data;
    } catch (error) {
      console.error('Code Submit API Error:', error);
      throw error;
    }
  },

  // 분석을 위한 코드 제출
  async submitCodeForAnalysis(codeData) {
    try {
      const response = await apiClient.post('/guide/submit-for-analysis', codeData);
      return response.data;
    } catch (error) {
      console.error('Code Submit for Analysis API Error:', error);
      throw error;
    }
  },

  // 지원 언어 목록 조회
  async getSupportedLanguages() {
    try {
      const response = await apiClient.get('/guide/languages');
      return response.data;
    } catch (error) {
      console.error('Supported Languages API Error:', error);
      throw error;
    }
  },

  // 언어별 템플릿 조회
  async getLanguageTemplate(language) {
    try {
      const response = await apiClient.get(`/guide/templates/${language}`);
      return response.data;
    } catch (error) {
      console.error('Language Template API Error:', error);
      throw error;
    }
  },

  // 문제 해결 검증
  async verifySolution(problemId, username = 'dlgusxor12') {
    try {
      const response = await apiClient.post('/guide/verify-solution', {
        problem_id: problemId,
        username
      });
      return response.data;
    } catch (error) {
      console.error('Solution Verification API Error:', error);
      throw error;
    }
  },

  // 코드 문법 검사
  async checkSyntax(language, code) {
    try {
      const response = await apiClient.post('/guide/check-syntax', {
        language,
        code
      });
      return response.data;
    } catch (error) {
      console.error('Syntax Check API Error:', error);
      throw error;
    }
  },

  // 제출된 코드 조회
  async getSubmittedCode(submissionId) {
    try {
      const response = await apiClient.get(`/guide/submission/${submissionId}`);
      return response.data;
    } catch (error) {
      console.error('Submitted Code API Error:', error);
      throw error;
    }
  },

  // 제출 정보 상세 조회
  async getSubmissionInfo(submissionId) {
    try {
      const response = await apiClient.get(`/guide/submission/${submissionId}/info`);
      return response.data;
    } catch (error) {
      console.error('Submission Info API Error:', error);
      throw error;
    }
  }
};