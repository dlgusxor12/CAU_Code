import React from 'react';
import { useNavigate } from 'react-router-dom';

const ProblemCard = ({ problem, showSolved = false }) => {
  const navigate = useNavigate();

  const handleSolveProblem = () => {
    navigate('/guide', { state: { problemId: problem.id, problemTitle: problem.title } });
  };

  const getTierColor = (tier) => {
    if (tier.includes('브론즈')) return 'bg-amber-100 text-amber-800';
    if (tier.includes('실버')) return 'bg-gray-100 text-gray-800';
    if (tier.includes('골드')) return 'bg-yellow-100 text-yellow-800';
    if (tier.includes('플래티넘')) return 'bg-cyan-100 text-cyan-800';
    if (tier.includes('다이아몬드')) return 'bg-blue-100 text-blue-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getAlgorithmColor = (algorithm) => {
    const colors = {
      '이진 탐색': 'bg-blue-100 text-blue-800',
      '그리디': 'bg-green-100 text-green-800',
      'DP': 'bg-purple-100 text-purple-800',
      '구현': 'bg-orange-100 text-orange-800',
      '그래프': 'bg-red-100 text-red-800',
      '수학': 'bg-indigo-100 text-indigo-800',
      '문자열': 'bg-pink-100 text-pink-800',
      '정렬': 'bg-teal-100 text-teal-800'
    };
    return colors[algorithm] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="border rounded-lg p-4 card-hover cursor-pointer bg-white">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-1">
            <h4 className="font-medium text-gray-900">[{problem.id}] {problem.title}</h4>
            {showSolved && problem.solved && (
              <span className="text-green-600 text-sm">✓</span>
            )}
          </div>
          <p className="text-sm text-gray-600 mb-3">{problem.description}</p>
          <div className="flex items-center space-x-2 flex-wrap gap-1">
            <span className={`px-2 py-1 text-xs rounded-full ${getTierColor(problem.tier)}`}>
              {problem.tier}
            </span>
            <span className={`px-2 py-1 text-xs rounded-full ${getAlgorithmColor(problem.algorithm)}`}>
              {problem.algorithm}
            </span>
            {problem.difficulty && (
              <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
                난이도 {problem.difficulty}
              </span>
            )}
          </div>
        </div>
        <div className="ml-4">
          <button 
            onClick={handleSolveProblem}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            풀어보기
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProblemCard;