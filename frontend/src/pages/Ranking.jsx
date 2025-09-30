import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { getGlobalRanking, getOrganizationRanking, getMyRank, getRankingStats } from '../services/rankingService';

const Ranking = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overall');

  // 데이터 상태
  const [globalRankings, setGlobalRankings] = useState([]);
  const [orgRankings, setOrgRankings] = useState([]);
  const [myRankInfo, setMyRankInfo] = useState(null);
  const [stats, setStats] = useState({
    total_users: 0,
    organization_users: 0,
    avg_solved_count: 0
  });
  const [loading, setLoading] = useState(true);

  const userOrganization = myRankInfo?.organization || '중앙대학교';

  // 데이터 로딩
  useEffect(() => {
    const fetchRankingData = async () => {
      if (!user?.solvedac_username) return;

      setLoading(true);
      try {
        // 병렬로 데이터 가져오기
        const [globalRes, myRankRes, statsRes] = await Promise.all([
          getGlobalRanking(100),
          getMyRank(user.solvedac_username),
          getRankingStats(userOrganization)
        ]);

        setGlobalRankings(globalRes.data?.rankings || []);
        setMyRankInfo(myRankRes.data || null);
        setStats(statsRes.data || {});

        // 내 소속 정보가 있으면 소속 랭킹도 가져오기
        if (myRankRes.data?.organization) {
          const orgRes = await getOrganizationRanking(myRankRes.data.organization, 100);
          setOrgRankings(orgRes.data?.rankings || []);
        }
      } catch (error) {
        console.error('Failed to fetch ranking data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRankingData();
  }, [user]);

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

  const currentData = activeTab === 'overall' ? globalRankings : orgRankings;

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <div className="text-[#2B95C3] text-lg">랭킹 데이터 로딩 중...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* 헤더 */}
      <div className="mb-8 relative">
        <div className="flex items-center space-x-3">
          <img
            src="/images/푸앙_응원.png"
            alt="푸앙"
            className="w-12 h-12 object-contain"
          />
          <div>
            <h1 className="text-3xl font-bold text-[#143365] mb-2">랭킹</h1>
            <p className="text-[#2B95C3]">CAU Code 사용자들의 랭킹을 확인하고 자신의 실력을 점검해보세요</p>
          </div>
        </div>
        <img
          src="/images/푸앙_윙크.png"
          alt="푸앙"
          className="w-16 h-16 object-contain absolute top-0 right-0 opacity-30"
        />
      </div>

      {/* 탭 */}
      <div className="mb-8">
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1 w-fit">
          <button
            onClick={() => setActiveTab('overall')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'overall'
                ? 'bg-white text-[#143365] shadow-sm'
                : 'text-gray-600 hover:text-[#2B95C3]'
            }`}
          >
            전체 랭킹
          </button>
          <button
            onClick={() => setActiveTab('organization')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'organization'
                ? 'bg-white text-[#143365] shadow-sm'
                : 'text-gray-600 hover:text-[#2B95C3]'
            }`}
          >
            소속 랭킹
          </button>
        </div>
      </div>

      {/* 내 랭킹 */}
      <div className="bg-gradient-to-r from-[#2B95C3] to-[#DEACC5] rounded-xl p-6 mb-8 text-white relative overflow-hidden">
        <img
          src="/images/푸앙_의복학위복.png"
          alt="푸앙"
          className="w-20 h-20 object-contain absolute top-4 right-4 opacity-30"
        />
        <h3 className="text-lg font-semibold mb-4">
          내 현재 랭킹 (소속: {myRankInfo?.organization || '미분류'})
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold">#{myRankInfo?.global_rank || '-'}</div>
            <div className="text-sm opacity-80">전체 순위</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{myRankInfo?.total_solved || 0}</div>
            <div className="text-sm opacity-80">해결한 문제</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{myRankInfo?.tier || 'Unrated'}</div>
            <div className="text-sm opacity-80">현재 티어</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{myRankInfo?.rating?.toLocaleString() || 0}</div>
            <div className="text-sm opacity-80">점수</div>
          </div>
        </div>
      </div>

      {/* 랭킹 테이블 */}
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            {activeTab === 'overall' ? '전체 랭킹' : `소속 랭킹 (${userOrganization})`}
          </h3>
          <a
            href="https://solved.ac/ko/ranking/tier"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-[#2B95C3] hover:text-[#143365] hover:bg-blue-50 rounded-lg transition-colors"
          >
            <span>solved.ac 랭킹 보러가기</span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">순위</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">사용자</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">티어</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">점수</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CAU Code 해결 완료</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {currentData.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center text-gray-500">
                    랭킹 데이터가 없습니다
                  </td>
                </tr>
              ) : (
                currentData.map((user) => (
                  <tr key={user.rank} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className="text-2xl mr-2">{getRankIcon(user.rank)}</span>
                        <span className="text-sm font-medium text-gray-900">#{user.rank}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{user.username}</div>
                        <div className="text-sm text-gray-500">{user.organization}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getTierColor(user.tier)}`}>
                        {user.tier}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-medium text-gray-900">
                        {user.rating?.toLocaleString()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {user.cau_solved}개
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border p-6 relative">
          <img
            src="/images/푸앙_기본형.png"
            alt="푸앙"
            className="w-10 h-10 object-contain absolute top-4 right-4 opacity-40"
          />
          <h4 className="text-lg font-semibold text-[#143365] mb-2">총 사용자 수</h4>
          <div className="text-3xl font-bold text-[#2B95C3]">
            {stats.total_users?.toLocaleString() || 0}
          </div>
          <p className="text-sm text-[#143365] mt-1">CAU Code 등록 사용자</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6 relative">
          <img
            src="/images/푸앙_의복학위복.png"
            alt="푸앙"
            className="w-10 h-10 object-contain absolute top-4 right-4 opacity-40"
          />
          <h4 className="text-lg font-semibold text-[#143365] mb-2">내 소속 사용자 수</h4>
          <div className="text-3xl font-bold text-[#DEACC5]">
            {stats.organization_users?.toLocaleString() || 0}
          </div>
          <p className="text-sm text-[#143365] mt-1">{userOrganization} 사용자</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border p-6 relative">
          <img
            src="/images/푸앙_미소.png"
            alt="푸앙"
            className="w-10 h-10 object-contain absolute top-4 right-4 opacity-40"
          />
          <h4 className="text-lg font-semibold text-[#143365] mb-2">평균 해결 문제 수</h4>
          <div className="text-3xl font-bold text-[#D7BCA1]">
            {stats.avg_solved_count?.toLocaleString() || 0}
          </div>
          <p className="text-sm text-[#143365] mt-1">사용자당 평균</p>
        </div>
      </div>
    </div>
  );
};

export default Ranking;