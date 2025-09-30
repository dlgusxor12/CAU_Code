import api from './api';

/**
 * 랭킹 관련 API 호출 서비스
 */

/**
 * 전체 랭킹 조회
 */
export const getGlobalRanking = async (limit = 100) => {
  try {
    const response = await api.get(`/ranking/global`, {
      params: { limit }
    });
    return response.data;
  } catch (error) {
    console.error('Global Ranking API Error:', error);
    throw error;
  }
};

/**
 * 소속별 랭킹 조회
 */
export const getOrganizationRanking = async (organization, limit = 100) => {
  try {
    const response = await api.get(`/ranking/organization/${encodeURIComponent(organization)}`, {
      params: { limit }
    });
    return response.data;
  } catch (error) {
    console.error('Organization Ranking API Error:', error);
    throw error;
  }
};

/**
 * 내 랭킹 정보 조회
 */
export const getMyRank = async (username) => {
  try {
    const response = await api.get(`/ranking/my-rank/${username}`);
    return response.data;
  } catch (error) {
    console.error('My Rank API Error:', error);
    throw error;
  }
};

/**
 * 랭킹 통계 조회
 */
export const getRankingStats = async (organization = null) => {
  try {
    const response = await api.get('/ranking/stats', {
      params: organization ? { organization } : {}
    });
    return response.data;
  } catch (error) {
    console.error('Ranking Stats API Error:', error);
    throw error;
  }
};