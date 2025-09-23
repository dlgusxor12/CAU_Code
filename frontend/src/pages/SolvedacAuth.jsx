import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * solved.ac 프로필 연동 페이지
 * Phase 3: Frontend Authentication UI
 */

const SolvedacAuth = () => {
  const navigate = useNavigate();
  const { user, requestSolvedacVerification, getVerificationStatus, logout } = useAuth();

  const [step, setStep] = useState('input'); // 'input', 'verification', 'completed'
  const [solvedacUsername, setSolvedacUsername] = useState('');
  const [verificationData, setVerificationData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // 페이지 로드 시 현재 인증 상태 확인
    checkCurrentVerificationStatus();
  }, []);

  // 현재 인증 상태 확인
  const checkCurrentVerificationStatus = async () => {
    try {
      const result = await getVerificationStatus();
      if (result.success && result.data) {
        const status = result.data.status;

        if (status === 'verified') {
          setStep('completed');
        } else if (status === 'pending') {
          setVerificationData(result.data);
          setStep('verification');
        }
      }
    } catch (error) {
      console.error('인증 상태 확인 실패:', error);
    }
  };

  // solved.ac 사용자명 입력 처리
  const handleUsernameSubmit = async (e) => {
    e.preventDefault();

    if (!solvedacUsername.trim()) {
      setError('solved.ac 사용자명을 입력해주세요.');
      return;
    }

    // 사용자명 유효성 검사 (3-20자, 영문/숫자/언더스코어)
    const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
    if (!usernameRegex.test(solvedacUsername)) {
      setError('유효하지 않은 사용자명입니다. (3-20자, 영문/숫자/언더스코어만 허용)');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const result = await requestSolvedacVerification(solvedacUsername);

      if (result.success) {
        setVerificationData(result.data);
        setStep('verification');
      } else {
        setError(result.error);
      }
    } catch (error) {
      console.error('인증 요청 실패:', error);
      setError('인증 요청 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // 인증 완료 후 대시보드로 이동
  const handleContinue = () => {
    navigate('/', { replace: true });
  };

  // 로그아웃 처리
  const handleLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  // 단계별 렌더링
  const renderStep = () => {
    switch (step) {
      case 'input':
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                solved.ac 프로필 연동
              </h2>
              <p className="text-gray-600">
                CAU Code를 사용하기 위해 solved.ac 계정 연동이 필요합니다
              </p>
            </div>

            <form onSubmit={handleUsernameSubmit} className="space-y-4">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                  solved.ac 사용자명
                </label>
                <input
                  type="text"
                  id="username"
                  value={solvedacUsername}
                  onChange={(e) => setSolvedacUsername(e.target.value)}
                  placeholder="예: dlgusxor12"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#2B95C3] focus:border-transparent"
                  disabled={isLoading}
                />
                <p className="mt-2 text-sm text-gray-500">
                  solved.ac 프로필에서 확인할 수 있는 사용자명을 입력하세요
                </p>
              </div>

              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                    <span className="text-red-700 text-sm">{error}</span>
                  </div>
                </div>
              )}

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-[#2B95C3] text-white py-3 px-4 rounded-lg font-semibold hover:bg-[#1F7AA8] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>처리 중...</span>
                  </div>
                ) : (
                  '인증 시작'
                )}
              </button>
            </form>

            <div className="text-center">
              <button
                onClick={handleLogout}
                className="text-gray-500 hover:text-gray-700 text-sm"
              >
                다른 계정으로 로그인
              </button>
            </div>
          </div>
        );

      case 'verification':
        return (
          <div className="space-y-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-[#FFF3CD] rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-[#856404]" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
              </div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                프로필 인증 진행 중
              </h2>
              <p className="text-gray-600">
                다음 단계를 따라 인증을 완료해주세요
              </p>
            </div>

            {verificationData && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="font-semibold text-blue-800 mb-4">인증 단계:</h3>
                <div className="space-y-3 text-sm text-blue-700">
                  <div className="flex items-start space-x-2">
                    <span className="font-semibold text-blue-800">1.</span>
                    <span>solved.ac에 로그인하세요</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span className="font-semibold text-blue-800">2.</span>
                    <span>프로필 설정으로 이동하세요</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span className="font-semibold text-blue-800">3.</span>
                    <div>
                      <span>자기소개란에 다음 인증 코드를 추가하세요:</span>
                      <div className="mt-2 p-3 bg-white border border-blue-300 rounded font-mono text-lg text-center">
                        {verificationData.verification_code}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span className="font-semibold text-blue-800">4.</span>
                    <span>저장 후 아래 "인증 확인" 버튼을 클릭하세요</span>
                  </div>
                </div>

                {verificationData.expires_at && (
                  <div className="mt-4 text-xs text-blue-600">
                    ⏰ 인증 코드는 {new Date(verificationData.expires_at).toLocaleString('ko-KR')}까지 유효합니다
                  </div>
                )}
              </div>
            )}

            <div className="flex space-x-4">
              <button
                onClick={() => navigate('/auth/verify', {
                  state: { verificationCode: verificationData?.verification_code }
                })}
                className="flex-1 bg-[#2B95C3] text-white py-3 px-4 rounded-lg font-semibold hover:bg-[#1F7AA8] transition-colors"
              >
                인증 확인
              </button>
              <button
                onClick={() => {
                  setStep('input');
                  setError('');
                  setSolvedacUsername('');
                  setVerificationData(null);
                }}
                className="flex-1 bg-gray-500 text-white py-3 px-4 rounded-lg font-semibold hover:bg-gray-600 transition-colors"
              >
                다시 시도
              </button>
            </div>
          </div>
        );

      case 'completed':
        return (
          <div className="space-y-6 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
              <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                인증 완료!
              </h2>
              <p className="text-gray-600">
                solved.ac 프로필 연동이 성공적으로 완료되었습니다
              </p>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-green-700 text-sm">
                이제 CAU Code의 모든 기능을 사용하실 수 있습니다!
              </p>
            </div>
            <button
              onClick={handleContinue}
              className="w-full bg-[#2B95C3] text-white py-3 px-4 rounded-lg font-semibold hover:bg-[#1F7AA8] transition-colors"
            >
              시작하기
            </button>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-[#F2F8FA] flex items-center justify-center px-4">
      <div className="max-w-lg w-full">
        {/* 로고 */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-2">
            <img
              src="/images/푸앙_열공.png"
              alt="푸앙"
              className="w-12 h-12 object-contain"
            />
            <h1 className="text-2xl font-bold text-[#143365]">CAU Code</h1>
          </div>
        </div>

        {/* 사용자 정보 */}
        {user && (
          <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-[#2B95C3] to-[#DEACC5] rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-semibold">
                  {user.name?.charAt(0) || 'U'}
                </span>
              </div>
              <div>
                <p className="font-medium text-gray-800">{user.name}</p>
                <p className="text-sm text-gray-600">{user.email}</p>
              </div>
            </div>
          </div>
        )}

        {/* 메인 카드 */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          {renderStep()}
        </div>

        {/* 도움말 */}
        <div className="mt-6 bg-white rounded-lg shadow-sm p-6">
          <h3 className="font-semibold text-gray-800 mb-3">
            왜 solved.ac 연동이 필요한가요?
          </h3>
          <div className="space-y-2 text-sm text-gray-600">
            <p>• 개인 맞춤형 문제 추천을 위해 현재 실력 파악</p>
            <p>• 해결한 문제 기록 및 학습 진도 추적</p>
            <p>• AI 기반 난이도 조절 및 약점 분석</p>
            <p>• 실시간 티어 및 레이팅 정보 제공</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SolvedacAuth;