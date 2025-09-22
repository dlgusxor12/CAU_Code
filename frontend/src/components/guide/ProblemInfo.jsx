import React, { useState, useEffect } from 'react';
import { guideService } from '../../services';

const ProblemInfo = ({ problemNumber }) => {
  const [problemInfo, setProblemInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (problemNumber) {
      fetchProblemInfo(problemNumber);
    } else {
      setProblemInfo(null);
      setError(null);
    }
  }, [problemNumber]);

  const fetchProblemInfo = async (number) => {
    try {
      setLoading(true);
      setError(null);
      const response = await guideService.getProblemDetail(parseInt(number));

      if (response.status === 'success' && response.data) {
        const data = response.data;
        setProblemInfo({
          title: data.title,
          timeLimit: `${Math.round(data.time_limit / 1000)}초`,
          memoryLimit: `${Math.round(data.memory_limit / 1024)}MB`,
          tier: getTierName(data.tier),
          tags: data.algorithms || [],
          submissions: data.submission_count,
          correct: data.accepted_count,
          users: data.solved_count,
          correctRate: data.success_rate ? Math.round(data.success_rate * 100) / 100 : 0
        });
      }
    } catch (error) {
      console.error('Failed to fetch problem info:', error);
      setError('문제 정보를 불러올 수 없습니다.');
      setProblemInfo({
        title: `문제 ${number}번`,
        timeLimit: '-',
        memoryLimit: '-',
        tier: '알 수 없음',
        tags: [],
        submissions: 0,
        correct: 0,
        users: 0,
        correctRate: 0
      });
    } finally {
      setLoading(false);
    }
  };

  const getTierName = (tierId) => {
    const tierNames = {
      0: '언레이티드',
      1: '브론즈 V', 2: '브론즈 IV', 3: '브론즈 III', 4: '브론즈 II', 5: '브론즈 I',
      6: '실버 V', 7: '실버 IV', 8: '실버 III', 9: '실버 II', 10: '실버 I',
      11: '골드 V', 12: '골드 IV', 13: '골드 III', 14: '골드 II', 15: '골드 I',
      16: '플래티넘 V', 17: '플래티넘 IV', 18: '플래티넘 III', 19: '플래티넘 II', 20: '플래티넘 I',
      21: '다이아몬드 V', 22: '다이아몬드 IV', 23: '다이아몬드 III', 24: '다이아몬드 II', 25: '다이아몬드 I',
      26: '루비 V', 27: '루비 IV', 28: '루비 III', 29: '루비 II', 30: '루비 I',
      31: '마스터'
    };
    return tierNames[tierId] || '알 수 없음';
  };

  if (!problemNumber) {
    return (
      <div className="bg-gray-50 rounded-lg p-4 text-center text-gray-500">
        문제 번호를 입력하면 문제 정보가 표시됩니다.
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
          </div>
          <div className="grid grid-cols-4 gap-4 mb-4">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 rounded-lg p-4 text-center text-red-600 mb-6">
        {error}
      </div>
    );
  }

  if (!problemInfo) {
    return null;
  }
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
          <span className="font-medium text-gray-700">정답:</span>
          <span className="ml-2 text-gray-600">{problemInfo.correct.toLocaleString()}</span>
        </div>
        <div>
          <span className="font-medium text-gray-700">맞힌 사람:</span>
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