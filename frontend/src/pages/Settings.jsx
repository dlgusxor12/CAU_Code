import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const Settings = () => {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    if (window.confirm('로그아웃하시겠습니까?')) {
      await logout();
      window.location.href = '/login';
    }
  };

  return (
    <div className="min-h-screen bg-[#F2F8FA] py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-8">설정</h1>

          <div className="space-y-8">
            {/* 계정 설정 */}
            <div className="border-b border-gray-200 pb-8">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">계정 설정</h2>

              {user && (
                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-[#2B95C3] to-[#DEACC5] rounded-full flex items-center justify-center">
                      <span className="text-white text-lg font-semibold">
                        {user.name?.charAt(0) || 'U'}
                      </span>
                    </div>
                    <div>
                      <p className="text-lg font-medium text-gray-800">{user.name}</p>
                      <p className="text-sm text-gray-600">{user.email}</p>
                    </div>
                  </div>
                </div>
              )}

              <button
                onClick={handleLogout}
                className="bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors flex items-center space-x-2"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clipRule="evenodd" />
                </svg>
                <span>로그아웃</span>
              </button>
            </div>

            {/* 알림 설정 */}
            <div className="border-b border-gray-200 pb-8">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">알림 설정</h2>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-800">문제 추천 알림</h3>
                    <p className="text-sm text-gray-600">새로운 문제가 추천될 때 알림을 받습니다</p>
                  </div>
                  <div className="text-gray-500 text-sm">곧 지원 예정</div>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-800">주간 리포트</h3>
                    <p className="text-sm text-gray-600">주간 학습 진도 리포트를 받습니다</p>
                  </div>
                  <div className="text-gray-500 text-sm">곧 지원 예정</div>
                </div>
              </div>
            </div>

            {/* 학습 설정 */}
            <div className="border-b border-gray-200 pb-8">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">학습 설정</h2>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-800">선호 프로그래밍 언어</h3>
                    <p className="text-sm text-gray-600">코드 분석 시 기본으로 사용할 언어를 설정합니다</p>
                  </div>
                  <div className="text-gray-500 text-sm">곧 지원 예정</div>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-800">난이도 설정</h3>
                    <p className="text-sm text-gray-600">문제 추천 시 선호하는 난이도 범위를 설정합니다</p>
                  </div>
                  <div className="text-gray-500 text-sm">곧 지원 예정</div>
                </div>
              </div>
            </div>

            {/* 정보 */}
            <div>
              <h2 className="text-xl font-semibold text-gray-800 mb-4">앱 정보</h2>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center space-x-3">
                  <img
                    src="/images/푸앙_열공.png"
                    alt="푸앙"
                    className="w-12 h-12 object-contain"
                  />
                  <div>
                    <h3 className="text-lg font-semibold text-blue-800">CAU Code</h3>
                    <p className="text-blue-700 text-sm">AI 기반 코딩 학습 플랫폼</p>
                    <p className="text-blue-600 text-xs">Version 1.0.0 (Beta)</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;