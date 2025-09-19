import React from 'react';

const ProblemInfo = ({ problemNumber }) => {
  // 실제로는 API에서 문제 정보를 받아올 것
  const getProblemInfo = (number) => {
    const problems = {
      '1000': {
        title: 'A+B',
        description: '두 정수 A와 B를 입력받은 다음, A+B를 출력하는 프로그램을 작성하시오.',
        timeLimit: '2초',
        memoryLimit: '128MB',
        tier: '브론즈 V',
        tags: ['수학', '구현', '사칙연산']
      },
      '1920': {
        title: '수 찾기',
        description: 'N개의 정수 A[1], A[2], …, A[N]이 주어져 있을 때, 이 안에 X라는 정수가 존재하는지 알아내는 프로그램을 작성하시오.',
        timeLimit: '1초',
        memoryLimit: '128MB',
        tier: '실버 IV',
        tags: ['자료 구조', '정렬', '이진 탐색']
      },
      '11399': {
        title: 'ATM',
        description: '인하은행에는 ATM이 1대밖에 없다. 지금 이 ATM앞에 N명의 사람들이 줄을 서있다.',
        timeLimit: '1초',
        memoryLimit: '256MB',
        tier: '실버 IV',
        tags: ['그리디 알고리즘', '정렬']
      }
    };
    
    return problems[number] || {
      title: `문제 ${number}번`,
      description: '문제 정보를 불러오는 중입니다...',
      timeLimit: '-',
      memoryLimit: '-',
      tier: '알 수 없음',
      tags: []
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
      
      <p className="text-gray-600 mb-4">{problemInfo.description}</p>
      
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