import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * 실시간 인증 진행 상태 페이지
 * Phase 3: Frontend Authentication UI
 */

const VerifyAuth = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { checkVerificationStatus, user } = useAuth();

  const [verificationCode, setVerificationCode] = useState('');
  const [status, setStatus] = useState('checking'); // 'checking', 'pending', 'verified', 'failed', 'expired'
  const [statusData, setStatusData] = useState(null);
  const [timeLeft, setTimeLeft] = useState(null);
  const [error, setError] = useState('');

  const countdownIntervalRef = useRef(null);

  useEffect(() => {
    // URL에서 인증 코드 가져오기
    const code = location.state?.verificationCode || new URLSearchParams(location.search).get('code');

    if (code) {
      setVerificationCode(code);
      checkStatus(code);
    } else {
      setError('인증 코드가 제공되지 않았습니다.');
      setStatus('failed');
    }

    return () => {
      // 컴포넌트 언마운트 시 카운트다운 정리
      if (countdownIntervalRef.current) {
        clearInterval(countdownIntervalRef.current);
      }
    };
  }, [location]);

  // 인증 상태 확인
  const checkStatus = async (code) => {
    try {
      setError('');

      const result = await checkVerificationStatus(code);

      if (result.success && result.data) {
        const data = result.data;
        setStatusData(data);

        switch (data.status) {
          case 'verified':
            setStatus('verified');
            // 3초 후 대시보드로 이동
            setTimeout(() => {
              navigate('/', { replace: true });
            }, 3000);
            break;

          case 'pending':
            setStatus('pending');
            if (data.expires_at) {
              updateTimeLeft(data.expires_at);
              startCountdown(data.expires_at);
            }
            break;

          case 'expired':
            setStatus('expired');
            break;

          case 'failed':
            setStatus('failed');
            setError(data.failed_reason || '인증에 실패했습니다.');
            break;

          default:
            setStatus('pending');
            break;
        }
      } else {
        // Rate limit 처리
        if (result.rateLimited) {
          setError(result.error);
          return;
        }

        setError(result.error || '인증 상태 확인에 실패했습니다.');
        setStatus('failed');
      }
    } catch (error) {
      console.error('인증 상태 확인 오류:', error);
      setError('인증 상태 확인 중 오류가 발생했습니다.');
      setStatus('failed');
    }
  };


  // 남은 시간 계산
  const updateTimeLeft = (expiresAt) => {
    const now = new Date();
    const expiry = new Date(expiresAt);
    const diff = expiry - now;

    if (diff <= 0) {
      setTimeLeft(null);
      setStatus('expired');
      setIsPolling(false);
    } else {
      setTimeLeft(diff);
    }
  };

  // 카운트다운 시작
  const startCountdown = (expiresAt) => {
    countdownIntervalRef.current = setInterval(() => {
      updateTimeLeft(expiresAt);
    }, 1000);
  };

  // 시간 포맷팅
  const formatTimeLeft = (milliseconds) => {
    if (!milliseconds) return '';

    const minutes = Math.floor(milliseconds / 60000);
    const seconds = Math.floor((milliseconds % 60000) / 1000);

    return `${minutes}분 ${seconds}초`;
  };

  // 수동 재확인
  const handleManualCheck = () => {
    if (verificationCode) {
      checkStatus(verificationCode);
    }
  };

  // 다시 시도
  const handleRetry = () => {
    navigate('/auth/solvedac', { replace: true });
  };

  // 상태별 렌더링
  const renderStatus = () => {
    switch (status) {
      case 'checking':
        return (
          <div className="text-center space-y-4">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
              <div className="w-8 h-8 border-4 border-[#2B95C3] border-t-transparent rounded-full animate-spin"></div>
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                인증 상태 확인 중
              </h2>
              <p className="text-gray-600">
                잠시만 기다려주세요...
              </p>
            </div>
          </div>
        );

      case 'pending':
        return (
          <div className="text-center space-y-6">
            <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto">
              <svg className="w-8 h-8 text-yellow-600 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>

            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                인증 진행 중
              </h2>
              <p className="text-gray-600">
                solved.ac 프로필 자기소개란에 인증 코드가 추가되기를 기다리고 있습니다
              </p>
            </div>

            {verificationCode && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-blue-700 text-sm mb-2">인증 코드:</p>
                <div className="font-mono text-lg bg-white border border-blue-300 rounded p-3">
                  {verificationCode}
                </div>
              </div>
            )}

            {timeLeft && (
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                <div className="flex items-center justify-center space-x-2">
                  <svg className="w-5 h-5 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                  </svg>
                  <span className="text-orange-700 font-medium">
                    남은 시간: {formatTimeLeft(timeLeft)}
                  </span>
                </div>
              </div>
            )}

            <div className="space-y-3">
              <button
                onClick={handleManualCheck}
                className="w-full bg-[#2B95C3] text-white py-3 px-4 rounded-lg font-semibold hover:bg-[#1F7AA8] transition-colors"
              >
                지금 확인하기
              </button>

              <div className="text-sm text-gray-500">
                <p>💡 solved.ac 자기소개란에 인증 코드를 추가한 후 저장하세요</p>
                <p>✅ 변경을 완료했다면 "지금 확인하기" 버튼을 눌러주세요</p>
              </div>
            </div>
          </div>
        );

      case 'verified':
        return (
          <div className="text-center space-y-6">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
              <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>

            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                인증 완료! 🎉
              </h2>
              <p className="text-gray-600">
                solved.ac 프로필 연동이 성공적으로 완료되었습니다
              </p>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-green-700 text-sm">
                잠시 후 대시보드로 자동 이동됩니다...
              </p>
            </div>

            <button
              onClick={() => navigate('/', { replace: true })}
              className="w-full bg-[#2B95C3] text-white py-3 px-4 rounded-lg font-semibold hover:bg-[#1F7AA8] transition-colors"
            >
              지금 시작하기
            </button>
          </div>
        );

      case 'expired':
        return (
          <div className="text-center space-y-6">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
              <svg className="w-8 h-8 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>

            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                인증 시간 만료
              </h2>
              <p className="text-gray-600">
                인증 코드의 유효 시간이 만료되었습니다
              </p>
            </div>

            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-700 text-sm">
                새로운 인증 코드를 발급받아 다시 시도해주세요
              </p>
            </div>

            <button
              onClick={handleRetry}
              className="w-full bg-[#2B95C3] text-white py-3 px-4 rounded-lg font-semibold hover:bg-[#1F7AA8] transition-colors"
            >
              다시 시도하기
            </button>
          </div>
        );

      case 'failed':
        return (
          <div className="text-center space-y-6">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
              <svg className="w-8 h-8 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>

            <div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                인증 실패
              </h2>
              <p className="text-gray-600">
                프로필 인증 과정에서 문제가 발생했습니다
              </p>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-700 text-sm">
                  {typeof error === 'string' ? error : JSON.stringify(error)}
                </p>
              </div>
            )}

            <div className="space-y-3">
              <button
                onClick={handleRetry}
                className="w-full bg-[#2B95C3] text-white py-3 px-4 rounded-lg font-semibold hover:bg-[#1F7AA8] transition-colors"
              >
                다시 시도하기
              </button>

              <button
                onClick={handleManualCheck}
                className="w-full bg-gray-500 text-white py-3 px-4 rounded-lg font-semibold hover:bg-gray-600 transition-colors"
              >
                상태 다시 확인
              </button>
            </div>
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
          {renderStatus()}
        </div>

        {/* 도움말 */}
        {status === 'pending' && (
          <div className="mt-6 bg-white rounded-lg shadow-sm p-6">
            <h3 className="font-semibold text-gray-800 mb-3">
              📝 인증 진행 방법
            </h3>
            <div className="space-y-2 text-sm text-gray-600">
              <p>1. solved.ac에 로그인합니다</p>
              <p>2. 프로필 설정 → 자기소개란으로 이동합니다</p>
              <p>3. 위의 인증 코드를 자기소개란에 추가합니다</p>
              <p>4. 변경 사항을 저장합니다</p>
              <p>5. "지금 확인하기" 버튼을 눌러 인증을 완료합니다</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VerifyAuth;