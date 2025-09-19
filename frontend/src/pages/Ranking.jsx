import React, { useState } from 'react';

const Ranking = () => {
  const [activeTab, setActiveTab] = useState('overall');
  const [timeFilter, setTimeFilter] = useState('weekly');

  const mockRankingData = {
    overall: [
      { rank: 1, username: 'algorithm_master', solvedCount: 1247, tier: '다이아몬드 II', score: 2845, avatar: '🏆' },
      { rank: 2, username: 'code_ninja', solvedCount: 892, tier: '플래티넘 I', score: 2234, avatar: '⚡' },
      { rank: 3, username: 'problem_solver', solvedCount: 756, tier: '플래티넘 III', score: 1987, avatar: '🚀' },
      { rank: 4, username: 'dev_student', solvedCount: 634, tier: '골드 I', score: 1654, avatar: '📚' },
      { rank: 5, username: 'coding_hero', solvedCount: 589, tier: '골드 II', score: 1523, avatar: '💻' },
      { rank: 6, username: 'algorithm_lover', solvedCount: 512, tier: '골드 III', score: 1389, avatar: '❤️' },
      { rank: 7, username: 'smart_coder', solvedCount: 467, tier: '골드 IV', score: 1245, avatar: '🧠' },
      { rank: 8, username: 'future_engineer', solvedCount: 423, tier: '실버 I', score: 1123, avatar: '🔧' },
      { rank: 9, username: 'logic_master', solvedCount: 398, tier: '실버 II', score: 1087, avatar: '🧩' },
      { rank: 10, username: 'code_enthusiast', solvedCount: 356, tier: '실버 III', score: 967, avatar: '🔥' }
    ],
    weekly: [
      { rank: 1, username: 'code_ninja', weeklyCount: 23, tier: '플래티넘 I', weeklyScore: 345, avatar: '⚡' },
      { rank: 2, username: 'algorithm_master', weeklyCount: 19, tier: '다이아몬드 II', weeklyScore: 298, avatar: '🏆' },
      { rank: 3, username: 'problem_solver', weeklyCount: 16, tier: '플래티넘 III', weeklyScore: 267, avatar: '🚀' },
      { rank: 4, username: 'smart_coder', weeklyCount: 14, tier: '골드 IV', weeklyScore: 234, avatar: '🧠' },
      { rank: 5, username: 'dev_student', weeklyCount: 12, tier: '골드 I', weeklyScore: 198, avatar: '📚' }
    ],
    monthly: [
      { rank: 1, username: 'algorithm_master', monthlyCount: 89, tier: '다이아몬드 II', monthlyScore: 1234, avatar: '🏆' },
      { rank: 2, username: 'code_ninja', monthlyCount: 76, tier: '플래티넘 I', monthlyScore: 1098, avatar: '⚡' },
      { rank: 3, username: 'problem_solver', monthlyCount: 64, tier: '플래티넘 III', monthlyScore: 945, avatar: '🚀' },
      { rank: 4, username: 'coding_hero', monthlyCount: 52, tier: '골드 II', monthlyScore: 823, avatar: '💻' },
      { rank: 5, username: 'dev_student', monthlyCount: 47, tier: '골드 I', monthlyScore: 756, avatar: '📚' }
    ]
  };

  const getTierColor = (tier) => {
    if (tier.includes('다이아몬드')) return 'text-blue-600 bg-blue-50';
    if (tier.includes('플래티넘')) return 'text-cyan-600 bg-cyan-50';
    if (tier.includes('골드')) return 'text-yellow-600 bg-yellow-50';
    if (tier.includes('실버')) return 'text-gray-600 bg-gray-50';
    if (tier.includes('브론즈')) return 'text-amber-600 bg-amber-50';
    return 'text-gray-600 bg-gray-50';
  };

  const getRankIcon = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return rank;
  };

  const currentData = timeFilter === 'weekly' ? mockRankingData.weekly : 
                      timeFilter === 'monthly' ? mockRankingData.monthly : 
                      mockRankingData.overall;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">랭킹</h1>
        <p className="text-gray-600">CAU Code 사용자들의 랭킹을 확인하고 자신의 실력을 점검해보세요</p>
      </div>

      {/* 탭 및 필터 */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
          {/* 탭 */}
          <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('overall')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'overall' 
                  ? 'bg-white text-blue-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              전체 랭킹
            </button>
            <button
              onClick={() => setActiveTab('school')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'school' 
                  ? 'bg-white text-blue-600 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              학교 랭킹
            </button>
          </div>

          {/* 시간 필터 */}
          <div className="flex space-x-2">
            {['weekly', 'monthly', 'overall'].map((filter) => (
              <button
                key={filter}
                onClick={() => setTimeFilter(filter)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                  timeFilter === filter 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                }`}
              >
                {filter === 'weekly' ? '주간' : filter === 'monthly' ? '월간' : '전체'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 내 랭킹 */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-6 mb-8 text-white">
        <h3 className="text-lg font-semibold mb-4">내 현재 랭킹</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold">#42</div>
            <div className="text-sm opacity-80">전체 순위</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">156</div>
            <div className="text-sm opacity-80">해결한 문제</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">골드 V</div>
            <div className="text-sm opacity-80">현재 티어</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">1,234</div>
            <div className="text-sm opacity-80">점수</div>
          </div>
        </div>
      </div>

      {/* 랭킹 테이블 */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            {timeFilter === 'weekly' ? '주간' : timeFilter === 'monthly' ? '월간' : '전체'} 랭킹
          </h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">순위</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">사용자</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">티어</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {timeFilter === 'weekly' ? '주간 해결' : timeFilter === 'monthly' ? '월간 해결' : '총 해결'}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">점수</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {currentData.map((user) => (
                <tr key={user.rank} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-2xl mr-2">{getRankIcon(user.rank)}</span>
                      <span className="text-sm font-medium text-gray-900">#{user.rank}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-2xl mr-3">{user.avatar}</span>
                      <div>
                        <div className="text-sm font-medium text-gray-900">{user.username}</div>
                        <div className="text-sm text-gray-500">CAU 컴퓨터공학부</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getTierColor(user.tier)}`}>
                      {user.tier}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {timeFilter === 'weekly' ? user.weeklyCount : 
                     timeFilter === 'monthly' ? user.monthlyCount : 
                     user.solvedCount}개
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm font-medium text-gray-900">
                      {timeFilter === 'weekly' ? user.weeklyScore : 
                       timeFilter === 'monthly' ? user.monthlyScore : 
                       user.score}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-2">총 사용자 수</h4>
          <div className="text-3xl font-bold text-blue-600">2,847</div>
          <p className="text-sm text-gray-600 mt-1">전체 등록된 사용자</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-2">이번 주 활성 사용자</h4>
          <div className="text-3xl font-bold text-green-600">1,234</div>
          <p className="text-sm text-gray-600 mt-1">문제를 해결한 사용자</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-2">평균 해결 문제 수</h4>
          <div className="text-3xl font-bold text-purple-600">87</div>
          <p className="text-sm text-gray-600 mt-1">사용자당 평균</p>
        </div>
      </div>
    </div>
  );
};

export default Ranking;