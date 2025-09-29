import React, { useState, useEffect } from 'react';
import ProblemCard from '../components/ProblemCard';
import RecommendationFilters from '../components/problems/RecommendationFilters';
import RecommendationSettings from '../components/problems/RecommendationSettings';
import ProblemStats from '../components/problems/ProblemStats';
import { problemService } from '../services';

const Problems = () => {
  const [problems, setProblems] = useState([]);
  const [filteredProblems, setFilteredProblems] = useState([]);
  const [filters, setFilters] = useState({ tier_min: null, tier_max: null, difficulty_class: null });
  const [settings, setSettings] = useState({
    recommendationType: 'ai_recommendation',
    problemCount: 5
  });
  const [loading, setLoading] = useState(false);
  const [hasRequestedRecommendation, setHasRequestedRecommendation] = useState(false);

  // 초기 로드 제거 - 사용자가 직접 추천 요청해야 함

  useEffect(() => {
    // 필터링 적용
    if (Object.values(filters).some(filter => filter !== null && filter !== '')) {
      searchProblemsWithFilters();
    } else {
      setFilteredProblems(problems);
    }
  }, [filters]);

  const loadInitialRecommendations = async () => {
    try {
      setLoading(true);
      const response = await problemService.getRecommendations({
        username: 'dlgusxor12',
        mode: settings.recommendationType,
        count: settings.problemCount
      });

      if (response.status === 'success' && response.data) {
        const transformedProblems = transformBackendProblems(response.data.problems);
        setProblems(transformedProblems);
        setFilteredProblems(transformedProblems);
      }
    } catch (error) {
      console.error('Failed to load initial recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchProblemsWithFilters = async () => {
    try {
      setLoading(true);
      const response = await problemService.searchProblems(filters);

      if (response.status === 'success' && response.data) {
        const transformedProblems = transformBackendProblems(response.data.problems);
        setFilteredProblems(transformedProblems);
      }
    } catch (error) {
      console.error('Failed to search problems with filters:', error);
      setFilteredProblems(problems);
    } finally {
      setLoading(false);
    }
  };

  const transformBackendProblems = (backendProblems) => {
    return backendProblems.map(problem => ({
      id: problem.problem_id || problem.id,
      title: problem.title || 'Unknown',
      description: problem.description || 'No description available',
      tier: problem.tier_name || 'Unknown',
      algorithm: problem.algorithm_tags?.[0] || 'Unknown',
      difficulty: problem.difficulty_class?.toString() || '1',
      solved: problem.is_solved || false
    }));
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  const handleSettingsChange = async (newSettings, shouldRecommend = false) => {
    setSettings(newSettings);

    if (shouldRecommend) {
      try {
        setLoading(true);
        setHasRequestedRecommendation(true);

        // 기존 문제 목록 강제 초기화 (새로운 추천을 받기 전)
        setProblems([]);
        setFilteredProblems([]);

        // 짧은 지연 후 API 호출 (상태 업데이트 보장)
        await new Promise(resolve => setTimeout(resolve, 100));

        const response = await problemService.getRecommendations({
          username: 'dlgusxor12',
          mode: newSettings.recommendationType,
          count: newSettings.problemCount,
          ...filters
        });

        if (response.status === 'success' && response.data) {
          const transformedProblems = transformBackendProblems(response.data.problems);
          setProblems(transformedProblems);
          setFilteredProblems(transformedProblems);
        }
      } catch (error) {
        console.error('Failed to get new recommendations:', error);
        // 오류 발생 시에도 빈 배열로 설정하여 "조건에 맞는 문제가 없습니다" 메시지 표시
        setProblems([]);
        setFilteredProblems([]);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 relative">
        <div className="flex items-center space-x-3">
          <img
            src="/images/푸앙_열공.png"
            alt="푸앙"
            className="w-12 h-12 object-contain"
          />
          <div>
            <h1 className="text-3xl font-bold text-[#143365] mb-2">문제 추천</h1>
            <p className="text-[#2B95C3]">AI가 당신의 실력에 맞는 문제를 추천해드립니다</p>
          </div>
        </div>
        <img
          src="/images/푸앙_응원.png"
          alt="푸앙"
          className="w-16 h-16 object-contain absolute top-0 right-0 opacity-30"
        />
      </div>

      {/* 통계 */}
      <ProblemStats />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* 왼쪽 사이드바 */}
        <div className="lg:col-span-1 space-y-6">
          <RecommendationSettings onSettingsChange={handleSettingsChange} />
          <RecommendationFilters onFilterChange={handleFilterChange} />
        </div>

        {/* 오른쪽 메인 콘텐츠 */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900">
                추천 문제 ({filteredProblems.length}개)
              </h3>
              {loading && (
                <div className="flex items-center space-x-2 text-blue-600">
                  <div className="animate-spin w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                  <span className="text-sm">AI가 분석 중...</span>
                </div>
              )}
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
                  <p className="text-gray-600">당신에게 맞는 문제를 찾고 있습니다...</p>
                </div>
              </div>
            ) : !hasRequestedRecommendation ? (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  <img
                    src="/images/푸앙_열공.png"
                    alt="푸앙"
                    className="w-20 h-20 mx-auto opacity-60 mb-4"
                  />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  문제 추천을 시작해보세요!
                </h3>
                <p className="text-gray-600 mb-4">
                  왼쪽의 "새로운 문제 추천받기" 버튼을 눌러<br />
                  AI가 당신에게 맞는 문제를 추천받아보세요.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredProblems.length > 0 ? (
                  filteredProblems.map((problem) => (
                    <ProblemCard
                      key={problem.id}
                      problem={problem}
                      showSolved={true}
                    />
                  ))
                ) : (
                  <div className="text-center py-12">
                    <div className="text-gray-400 mb-4">
                      <svg className="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                      </svg>
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      조건에 맞는 문제가 없습니다
                    </h3>
                    <p className="text-gray-600">
                      필터 조건을 변경하거나 새로운 추천을 받아보세요.
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Problems;