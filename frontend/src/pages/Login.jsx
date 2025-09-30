import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * Google OAuth 로그인 페이지
 * Phase 3: Frontend Authentication UI
 */

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, guestLogin, error, isLoading, clearError } = useAuth();

  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [isGuestLoading, setIsGuestLoading] = useState(false);
  const [loginError, setLoginError] = useState('');

  // 리다이렉트할 경로 (로그인 전에 접근하려던 페이지)
  const from = location.state?.from || '/';

  useEffect(() => {
    // 에러 상태 초기화
    clearError();
    setLoginError('');

    // Google Identity Services 스크립트 로드
    if (!window.google) {
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = initializeGoogleSignIn;
      document.head.appendChild(script);
    } else {
      initializeGoogleSignIn();
    }

    return () => {
      // 컴포넌트 언마운트 시 에러 클리어
      clearError();
    };
  }, []);

  // Google Sign-In 초기화
  const initializeGoogleSignIn = () => {
    if (window.google) {
      window.google.accounts.id.initialize({
        client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
        callback: handleGoogleResponse,
        auto_select: false,
        cancel_on_tap_outside: false
      });

      // Google 로그인 버튼 렌더링
      window.google.accounts.id.renderButton(
        document.getElementById('googleSignInButton'),
        {
          theme: 'outline',
          size: 'large',
          width: 300,
          text: 'signin_with',
          shape: 'rectangular',
          logo_alignment: 'left'
        }
      );
    }
  };

  // Google OAuth 응답 처리
  const handleGoogleResponse = async (response) => {
    if (!response.credential) {
      setLoginError('Google 로그인에 실패했습니다.');
      return;
    }

    setIsGoogleLoading(true);
    setLoginError('');

    try {
      const result = await login(response.credential);

      if (result.success) {
        // 로그인 성공 시 원래 가려던 페이지 또는 대시보드로 이동
        const redirectTo = result.user.profile_verified ? from : '/auth/solvedac';
        navigate(redirectTo, { replace: true });
      } else {
        setLoginError(result.error || '로그인에 실패했습니다.');
      }
    } catch (error) {
      console.error('로그인 처리 중 오류:', error);
      setLoginError('로그인 처리 중 오류가 발생했습니다.');
    } finally {
      setIsGoogleLoading(false);
    }
  };

  // 게스트 로그인 처리
  const handleGuestLogin = async () => {
    setIsGuestLoading(true);
    setLoginError('');

    try {
      const result = await guestLogin();

      if (result.success) {
        // 게스트 계정은 이미 프로필 인증이 완료되어 있으므로 바로 대시보드로
        navigate(from, { replace: true });
      } else {
        setLoginError(result.error || '게스트 로그인에 실패했습니다.');
      }
    } catch (error) {
      console.error('게스트 로그인 처리 중 오류:', error);
      setLoginError('게스트 로그인 처리 중 오류가 발생했습니다.');
    } finally {
      setIsGuestLoading(false);
    }
  };

  // 표시할 에러 메시지 결정
  const displayError = loginError || error;

  return (
    <div className="min-h-screen bg-[#F2F8FA] flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* 로고 및 타이틀 */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <img
              src="/images/푸앙_열공.png"
              alt="푸앙"
              className="w-16 h-16 object-contain"
            />
            <h1 className="text-3xl font-bold text-[#143365]">CAU Code</h1>
          </div>
          <p className="text-gray-600 text-lg">
            AI 기반 코딩 학습 플랫폼
          </p>
        </div>

        {/* 로그인 카드 */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">
              로그인
            </h2>
            <p className="text-gray-600">
              Google 계정으로 간편하게 시작하세요
            </p>
          </div>

          {/* 에러 메시지 */}
          {displayError && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="text-red-700 text-sm font-medium">
                  {displayError}
                </span>
              </div>
            </div>
          )}

          {/* Google 로그인 버튼 */}
          <div className="space-y-4">
            <div className="flex justify-center">
              {(isLoading || isGoogleLoading) ? (
                <div className="flex items-center justify-center space-x-2 py-3 px-6 bg-gray-100 rounded-lg">
                  <div className="w-5 h-5 border-2 border-[#2B95C3] border-t-transparent rounded-full animate-spin"></div>
                  <span className="text-gray-600">로그인 중...</span>
                </div>
              ) : (
                <div id="googleSignInButton"></div>
              )}
            </div>

            {/* 구분선 */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">또는</span>
              </div>
            </div>

            {/* 게스트 로그인 버튼 */}
            <div className="flex justify-center">
              <button
                onClick={handleGuestLogin}
                disabled={isLoading || isGuestLoading || isGoogleLoading}
                className={`
                  w-full max-w-[300px] py-3 px-6 rounded-lg font-medium
                  transition-all duration-200
                  flex items-center justify-center space-x-2
                  ${isGuestLoading
                    ? 'bg-gray-100 cursor-not-allowed'
                    : 'bg-[#143365] hover:bg-[#1a4080] text-white shadow-md hover:shadow-lg'
                  }
                `}
              >
                {isGuestLoading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-[#2B95C3] border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-gray-600">로그인 중...</span>
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                    </svg>
                    <span>게스트로 체험하기</span>
                  </>
                )}
              </button>
            </div>

            {/* 추가 정보 */}
            <div className="text-center text-sm text-gray-500 space-y-2">
              <p>
                로그인 후 solved.ac 프로필 연동이 필요합니다
              </p>
              <p className="text-xs">
                게스트 모드는 dlgusxor12 계정으로 플랫폼을 체험합니다
              </p>
              <p className="text-xs">
                Google 계정 정보는 안전하게 보호됩니다
              </p>
            </div>
          </div>
        </div>

        {/* 기능 안내 */}
        <div className="mt-8 bg-white rounded-lg shadow-sm p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 text-center">
            CAU Code의 주요 기능
          </h3>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-[#2B95C3] rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span className="text-gray-700">AI 기반 맞춤형 문제 추천</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-[#DEACC5] rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z" />
                </svg>
              </div>
              <span className="text-gray-700">실시간 코드 피드백 및 분석</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-[#143365] rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                  <path fillRule="evenodd" d="M4 5a2 2 0 012-2v1a1 1 0 002 0V3a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 2a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
                </svg>
              </div>
              <span className="text-gray-700">학습 진도 추적 및 통계</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;