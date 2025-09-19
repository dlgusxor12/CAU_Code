import React from 'react';
import { useNavigate } from 'react-router-dom';

const TodayProblems = () => {
  const navigate = useNavigate();

  const problems = [
    {
      id: 1920,
      title: '수 찾기',
      description: '이진 탐색을 활용한 문제입니다',
      tier: '실버 IV',
      algorithm: '이진 탐색',
      tierColor: 'bg-yellow-100 text-yellow-800',
      algorithmColor: 'bg-blue-100 text-blue-800'
    },
    {
      id: 11399,
      title: 'ATM',
      description: '그리디 알고리즘의 기본 문제입니다',
      tier: '실버 IV',
      algorithm: '그리디',
      tierColor: 'bg-yellow-100 text-yellow-800',
      algorithmColor: 'bg-green-100 text-green-800'
    }
  ];

  const handleSolveProblem = (problemId) => {
    navigate('/guide', { state: { problemId } });
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-900">오늘의 문제</h3>
        <span className="text-sm text-gray-500">2024.12.19</span>
      </div>
      <div className="space-y-4">
        {problems.map((problem) => (
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
        ))}
      </div>
    </div>
  );
};

export default TodayProblems;