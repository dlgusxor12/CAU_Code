import React from 'react';

const ProblemInfo = ({ problemNumber }) => {
  // 실제로는 API에서 문제 정보를 받아올 것
  const getProblemInfo = (number) => {
    const problems = {
      '1000': {
        title: 'A+B',
        timeLimit: '2초',
        memoryLimit: '128MB',
        tier: '브론즈 V',
        tags: ['수학', '구현', '사칙연산'],
        submissions: 2847692,
        correct: 1892456,
        users: 1638923,
        correctRate: 66.4
      },
      '1920': {
        title: '수 찾기',
        timeLimit: '1초',
        memoryLimit: '128MB',
        tier: '실버 IV',
        tags: ['자료 구조', '정렬', '이진 탐색'],
        submissions: 425687,
        correct: 178923,
        users: 145782,
        correctRate: 42.0
      },
      '11399': {
        title: 'ATM',
        timeLimit: '1초',
        memoryLimit: '256MB',
        tier: '실버 IV',
        tags: ['그리디 알고리즘', '정렬'],
        submissions: 267891,
        correct: 189234,
        users: 156789,
        correctRate: 70.6
      }
    };

    return problems[number] || {
      title: `문제 ${number}번`,
      timeLimit: '-',
      memoryLimit: '-',
      tier: '알 수 없음',
      tags: [],
      submissions: 0,
      correct: 0,
      users: 0,
      correctRate: 0
    };
  };

  if (!problemNumber) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 text-center text-gray-500">
        문제 번호를 입력하면 문제 정보가 표시됩니다.
      </div>
    );
  }

  const problemInfo = getProblemInfo(problemNumber);
  const getTierColor = (tier) => {
    if (tier.includes('브론즈')) return 'bg-amber-100 text-amber-800';
    if (tier.includes('실버')) return 'bg-gray-100 text-gray-800';
    if (tier.includes('골드')) return 'bg-yellow-100 text-yellow-800';
    if (tier.includes('플래티넘')) return 'bg-cyan-100 text-cyan-800';
    if (tier.includes('다이아몬드')) return 'bg-blue-100 text-blue-800';
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-gray-900">
          문제 {problemNumber}번 - {problemInfo.title}
        </h3>
        <span className={`px-3 py-1 text-sm rounded-full font-medium ${getTierColor(problemInfo.tier)}`}>
          {problemInfo.tier}
        </span>
      </div>
      
      
      <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
        <div>
          <span className="font-medium text-gray-700">시간 제한:</span>
          <span className="ml-2 text-gray-600">{problemInfo.timeLimit}</span>
        </div>
        <div>
          <span className="font-medium text-gray-700">메모리 제한:</span>
          <span className="ml-2 text-gray-600">{problemInfo.memoryLimit}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4 text-sm">
        <div>
          <span className="font-medium text-gray-700">제출:</span>
          <span className="ml-2 text-gray-600">{problemInfo.submissions.toLocaleString()}</span>
        </div>
        <div>
          <span className="font-medium text-gray-700">맞은 횟수:</span>
          <span className="ml-2 text-gray-600">{problemInfo.correct.toLocaleString()}</span>
        </div>
        <div>
          <span className="font-medium text-gray-700">푼 사람 수:</span>
          <span className="ml-2 text-gray-600">{problemInfo.users.toLocaleString()}</span>
        </div>
        <div>
          <span className="font-medium text-gray-700">정답 비율:</span>
          <span className="ml-2 text-gray-600">{problemInfo.correctRate}%</span>
        </div>
      </div>
      
      {problemInfo.tags.length > 0 && (
        <div>
          <span className="font-medium text-gray-700 text-sm">태그:</span>
          <div className="flex flex-wrap gap-2 mt-2">
            {problemInfo.tags.map((tag, index) => (
              <span 
                key={index}
                className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}
      
      <div className="mt-4 pt-4 border-t">
        <a 
          href={`https://www.acmicpc.net/problem/${problemNumber}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 hover:text-blue-700 text-sm font-medium"
        >
          백준에서 문제 보기 →
        </a>
      </div>
    </div>
  );
};

export default ProblemInfo;