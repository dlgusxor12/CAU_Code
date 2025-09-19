import React from 'react';
import { useNavigate } from 'react-router-dom';

const ReviewProblems = () => {
  const navigate = useNavigate();

  const reviewProblems = [
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
  ];

  const handleRetryProblem = (problemId) => {
    navigate('/guide', { state: { problemId, isRetry: true } });
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-6">복습할 문제</h3>
      <div className="space-y-4">
        {reviewProblems.map((problem) => (
          <div key={problem.id} className="border border-red-200 rounded-lg p-4 card-hover cursor-pointer">
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
        ))}
      </div>
    </div>
  );
};

export default ReviewProblems;