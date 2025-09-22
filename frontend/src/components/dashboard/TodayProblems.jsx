import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { userService } from '../../services';

const TodayProblems = () => {
  const navigate = useNavigate();
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTodayProblems();
  }, []);

  const fetchTodayProblems = async () => {
    try {
      setLoading(true);
      const response = await userService.getTodayProblems();

      if (response.status === 'success' && response.data?.recommended_problems) {
        const formattedProblems = response.data.recommended_problems.map(problem => ({
          id: problem.problem_id,
          title: problem.title,
          description: problem.description || `${problem.tier_name} 난이도의 문제입니다`,
          tier: problem.tier_name,
          algorithm: problem.tags?.[0] || '미등록',
          tierColor: getTierColor(problem.tier),
          algorithmColor: 'bg-blue-100 text-blue-800'
        }));
        setProblems(formattedProblems);
      } else {
        // Fallback 더미 데이터
        setProblems([
          {
            id: 1920,
            title: '수 찾기',
            description: '이진 탐색을 활용한 문제입니다',
            tier: '실버 IV',
            algorithm: '이진 탐색',
            tierColor: 'bg-yellow-100 text-yellow-800',
            algorithmColor: 'bg-blue-100 text-blue-800'
          }
        ]);
      }
    } catch (error) {
      console.error('Failed to fetch today problems:', error);
      setProblems([]);
    } finally {
      setLoading(false);
    }
  };

  const getTierColor = (tier) => {
    if (!tier) return 'bg-gray-100 text-gray-800';
    if (tier >= 26) return 'bg-red-100 text-red-800'; // Ruby
    if (tier >= 21) return 'bg-blue-100 text-blue-800'; // Diamond
    if (tier >= 16) return 'bg-cyan-100 text-cyan-800'; // Platinum
    if (tier >= 11) return 'bg-yellow-100 text-yellow-800'; // Gold
    if (tier >= 6) return 'bg-gray-100 text-gray-800'; // Silver
    return 'bg-amber-100 text-amber-800'; // Bronze
  };

  const handleSolveProblem = (problemId) => {
    navigate('/guide', { state: { problemId } });
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-900">오늘의 문제</h3>
        <span className="text-sm text-gray-500">{new Date().toISOString().split('T')[0]}</span>
      </div>
      <div className="space-y-4">
        {loading ? (
          <div className="space-y-4">
            {[1, 2].map((item) => (
              <div key={item} className="border rounded-lg p-4 animate-pulse">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="h-4 bg-gray-200 rounded w-48 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-64 mb-2"></div>
                    <div className="flex space-x-2">
                      <div className="h-5 bg-gray-200 rounded w-16"></div>
                      <div className="h-5 bg-gray-200 rounded w-16"></div>
                    </div>
                  </div>
                  <div className="h-8 bg-gray-200 rounded w-20"></div>
                </div>
              </div>
            ))}
          </div>
        ) : problems.length > 0 ? (
          problems.map((problem) => (
            <div key={problem.id} className="border rounded-lg p-4 card-hover cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-gray-900">[{problem.id}] {problem.title}</h4>
                  <p className="text-sm text-gray-600 mt-1">{problem.description}</p>
                  <div className="flex items-center space-x-2 mt-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${problem.tierColor}`}>
                      {problem.tier}
                    </span>
                    <span className={`px-2 py-1 text-xs rounded-full ${problem.algorithmColor}`}>
                      {problem.algorithm}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => handleSolveProblem(problem.id)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  풀어보기
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p>오늘의 추천 문제를 불러오는 중입니다...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TodayProblems;