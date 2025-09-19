import React, { useState, useEffect } from 'react';
import ProblemCard from '../components/ProblemCard';
import RecommendationFilters from '../components/problems/RecommendationFilters';
import RecommendationSettings from '../components/problems/RecommendationSettings';
import ProblemStats from '../components/problems/ProblemStats';

const Problems = () => {
  const [problems, setProblems] = useState([]);
  const [filteredProblems, setFilteredProblems] = useState([]);
  const [filters, setFilters] = useState({ tier: '', algorithm: '', difficulty: '' });
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(false);

  // 초기 문제 데이터
  const initialProblems = [
    {
      id: 2839,
      title: '설탕 배달',
      description: '설탕을 정확히 N킬로그램 배달해야 합니다. 3킬로그램 봉지와 5킬로그램 봉지를 사용하여 최소 봉지 개수를 구하세요.',
      tier: '실버 IV',
      algorithm: '그리디',
      difficulty: '2',
      solved: false
    },
    {
      id: 1541,
      title: '잃어버린 괄호',
      description: '괄호를 적절히 배치하여 식의 값을 최소화하는 문제입니다.',
      tier: '실버 II',
      algorithm: '그리디',
      difficulty: '3',
      solved: false
    },
    {
      id: 11047,
      title: '동전 0',
      description: 'K원을 만드는데 필요한 동전 개수의 최솟값을 구하는 문제입니다.',
      tier: '실버 III',
      algorithm: '그리디',
      difficulty: '3',
      solved: true
    },
    {
      id: 1931,
      title: '회의실 배정',
      description: '회의실을 사용할 수 있는 회의의 최대 개수를 구하는 문제입니다.',
      tier: '실버 I',
      algorithm: '그리디',
      difficulty: '4',
      solved: true
    },
    {
      id: 2750,
      title: '수 정렬하기',
      description: 'N개의 수가 주어졌을 때, 이를 오름차순으로 정렬하는 프로그램을 작성하세요.',
      tier: '브론즈 II',
      algorithm: '정렬',
      difficulty: '1',
      solved: false
    },
    {
      id: 1074,
      title: 'Z',
      description: '재귀적으로 배열을 탐색하며 특정 위치를 찾는 문제입니다.',
      tier: '골드 V',
      algorithm: '구현',
      difficulty: '4',
      solved: false
    }
  ];

  useEffect(() => {
    // 초기 문제 로드
    setProblems(initialProblems);
    setFilteredProblems(initialProblems);
  }, []);

  useEffect(() => {
    // 필터링 적용
    let filtered = problems;

    if (filters.tier) {
      filtered = filtered.filter(problem => problem.tier.includes(filters.tier));
    }
    if (filters.algorithm) {
      filtered = filtered.filter(problem => problem.algorithm === filters.algorithm);
    }
    if (filters.difficulty) {
      filtered = filtered.filter(problem => problem.difficulty === filters.difficulty);
    }

    setFilteredProblems(filtered);
  }, [problems, filters]);

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  const handleSettingsChange = (newSettings, shouldRecommend = false) => {
    setSettings(newSettings);
    
    if (shouldRecommend) {
      setLoading(true);
      // 새로운 추천 로직 시뮬레이션
      setTimeout(() => {
        const recommendedProblems = generateRecommendedProblems(newSettings);
        setProblems(recommendedProblems);
        setLoading(false);
      }, 1500);
    }
  };

  const generateRecommendedProblems = (settings) => {
    // 실제로는 서버에서 AI 추천을 받아올 것
    let recommended = [...initialProblems];
    
    if (settings.recommendationType === 'challenge') {
      // 도전 모드: 더 어려운 문제들
      recommended = recommended.filter(p => 
        p.tier.includes('골드') || p.tier.includes('플래티넘')
      );
    } else if (settings.recommendationType === 'similar') {
      // 유사 문제: 그리디 위주
      recommended = recommended.filter(p => p.algorithm === '그리디');
    }
    
    return recommended.slice(0, settings.problemCount || 5);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">문제 추천</h1>
        <p className="text-gray-600">AI가 당신의 실력에 맞는 문제를 추천해드립니다</p>
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