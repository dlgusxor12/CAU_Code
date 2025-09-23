import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/**
 * 인증이 필요한 페이지를 보호하는 라우트 컴포넌트
 * Phase 3: Frontend Authentication UI
 */

const ProtectedRoute = ({
  children,
  requireProfileVerification = false,
  redirectTo = '/login'
}) => {
  const { isAuthenticated, isLoading, isProfileVerified } = useAuth();
  const location = useLocation();

  // 로딩 중일 때는 로딩 스피너 표시
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F2F8FA]">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-12 h-12 border-4 border-[#2B95C3] border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-600 text-lg">인증 상태를 확인하고 있습니다...</p>
        </div>
      </div>
    );
  }

  // 인증되지 않은 사용자는 로그인 페이지로 리다이렉트
  if (!isAuthenticated) {
    return (
      <Navigate
        to={redirectTo}
        state={{ from: location.pathname }}
        replace
      />
    );
  }

  // 프로필 인증이 필요한 페이지에서 인증되지 않은 경우
  if (requireProfileVerification && !isProfileVerified) {
    return (
      <Navigate
        to="/auth/solvedac"
        state={{ from: location.pathname }}
        replace
      />
    );
  }

  // 모든 조건을 만족하면 자식 컴포넌트 렌더링
  return children;
};

/**
 * 로그인한 사용자는 접근할 수 없는 페이지 (예: 로그인 페이지)
 */
export const PublicOnlyRoute = ({ children, redirectTo = '/' }) => {
  const { isAuthenticated, isLoading } = useAuth();

  // 로딩 중일 때는 로딩 스피너 표시
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F2F8FA]">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-12 h-12 border-4 border-[#2B95C3] border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-600 text-lg">인증 상태를 확인하고 있습니다...</p>
        </div>
      </div>
    );
  }

  // 이미 로그인한 사용자는 대시보드로 리다이렉트
  if (isAuthenticated) {
    return <Navigate to={redirectTo} replace />;
  }

  // 로그인하지 않은 사용자만 접근 가능
  return children;
};

/**
 * 프로필 인증이 완료되지 않은 사용자만 접근 가능한 페이지
 */
export const UnverifiedOnlyRoute = ({ children, redirectTo = '/' }) => {
  const { isAuthenticated, isLoading, isProfileVerified } = useAuth();

  // 로딩 중일 때는 로딩 스피너 표시
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F2F8FA]">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-12 h-12 border-4 border-[#2B95C3] border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-600 text-lg">인증 상태를 확인하고 있습니다...</p>
        </div>
      </div>
    );
  }

  // 로그인하지 않은 사용자는 로그인 페이지로
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // 이미 프로필 인증이 완료된 사용자는 대시보드로
  if (isProfileVerified) {
    return <Navigate to={redirectTo} replace />;
  }

  // 프로필 인증이 완료되지 않은 사용자만 접근 가능
  return children;
};

export default ProtectedRoute;