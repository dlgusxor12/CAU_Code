import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { userService } from '../../services';

const ReviewProblems = () => {
  const navigate = useNavigate();
  const [reviewProblems, setReviewProblems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReviewProblems();
  }, []);

  const fetchReviewProblems = async () => {
    try {
      setLoading(true);
      const response = await userService.getReviewProblems();

      if (response.status === 'success' && response.data?.review_problems) {
        const formattedProblems = response.data.review_problems.map(problem => ({
          id: problem.problem_id,
          title: problem.title,
          description: problem.description || '다시 도전해보세요!',
          tier: problem.tier_name,
          tags: problem.tags || ['미등록'], // 전체 태그 배열 저장
          status: '복습 필요',
          tierColor: getTierColor(problem.tier),
          algorithmColor: 'bg-purple-100 text-purple-800',
          statusColor: 'bg-red-100 text-red-800'
        }));
        setReviewProblems(formattedProblems);
      } else {
        // Fallback 더미 데이터
        setReviewProblems([
          {
            id: 1463,
            title: '1로 만들기',
            description: '동적 계획법 문제 - 다시 도전해보세요!',
            tier: '실버 III',
            algorithm: 'DP',
            status: '틀림',
            tierColor: 'bg-yellow-100 text-yellow-800',
            algorithmColor: 'bg-purple-100 text-purple-800',
            statusColor: 'bg-red-100 text-red-800'
          }
        ]);
      }
    } catch (error) {
      console.error('Failed to fetch review problems:', error);
      setReviewProblems([]);
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

  const handleRetryProblem = (problemId) => {
    navigate('/guide', { state: { problemId, isRetry: true } });
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-6">복습할 문제</h3>
      <div className="space-y-4">
        {loading ? (
          <div className="border border-red-200 rounded-lg p-4 animate-pulse">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-48 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-64 mb-2"></div>
                <div className="flex space-x-2">
                  <div className="h-5 bg-gray-200 rounded w-16"></div>
                  <div className="h-5 bg-gray-200 rounded w-16"></div>
                  <div className="h-5 bg-gray-200 rounded w-16"></div>
                </div>
              </div>
              <div className="h-8 bg-gray-200 rounded w-20"></div>
            </div>
          </div>
        ) : reviewProblems.length > 0 ? (
          reviewProblems.map((problem) => (
            <div key={problem.id} className="border border-red-200 rounded-lg p-4 card-hover cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-gray-900">[{problem.id}] {problem.title}</h4>
                  <p className="text-sm text-gray-600 mt-1">{problem.description}</p>
                  <div className="flex items-center flex-wrap gap-2 mt-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${problem.tierColor}`}>
                      {problem.tier}
                    </span>
                    {problem.tags ? problem.tags.map((tag, index) => (
                      <span key={index} className={`px-2 py-1 text-xs rounded-full ${problem.algorithmColor}`}>
                        {tag}
                      </span>
                    )) : (
                      <span className={`px-2 py-1 text-xs rounded-full ${problem.algorithmColor}`}>
                        미등록
                      </span>
                    )}
                    <span className={`px-2 py-1 text-xs rounded-full ${problem.statusColor}`}>
                      {problem.status}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => handleRetryProblem(problem.id)}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  다시 풀기
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p>복습할 문제가 없습니다. 잘 하고 있어요!</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReviewProblems;