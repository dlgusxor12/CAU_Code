import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const Profile = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-[#F2F8FA] py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-8">마이페이지</h1>

          {user && (
            <div className="space-y-6">
              {/* 사용자 기본 정보 */}
              <div className="border-b border-gray-200 pb-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">기본 정보</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">이름</label>
                    <div className="text-lg text-gray-800">{user.name}</div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">이메일</label>
                    <div className="text-lg text-gray-800">{user.email}</div>
                  </div>
                </div>
              </div>

              {/* solved.ac 연동 정보 */}
              <div className="border-b border-gray-200 pb-6">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">solved.ac 연동</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">사용자명</label>
                    <div className="text-lg text-gray-800">
                      {user.solvedac_username || '연동되지 않음'}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-600 mb-1">인증 상태</label>
                    <div className="flex items-center space-x-2">
                      {user.profile_verified ? (
                        <>
                          <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                          <span className="text-green-600 font-medium">인증 완료</span>
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5 text-orange-500" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                          </svg>
                          <span className="text-orange-600 font-medium">인증 필요</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* 프로필 관리 */}
              <div>
                <h2 className="text-xl font-semibold text-gray-800 mb-4">프로필 관리</h2>
                <div className="space-y-4">
                  {!user.profile_verified && (
                    <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                      <div className="flex items-center space-x-3">
                        <svg className="w-6 h-6 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                        <div>
                          <h3 className="text-orange-800 font-medium">프로필 인증 필요</h3>
                          <p className="text-orange-700 text-sm">
                            CAU Code의 모든 기능을 사용하려면 solved.ac 프로필 인증이 필요합니다.
                          </p>
                        </div>
                      </div>
                      <div className="mt-4">
                        <button
                          onClick={() => window.location.href = '/auth/solvedac'}
                          className="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors"
                        >
                          지금 인증하기
                        </button>
                      </div>
                    </div>
                  )}

                  <div className="text-center py-8">
                    <p className="text-gray-600">더 많은 프로필 설정 기능이 곧 추가될 예정입니다.</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;