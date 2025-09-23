import React, { createContext, useContext, useReducer, useEffect, useCallback, useRef } from 'react';
import authService from '../services/authService';

/**
 * 전역 인증 상태 관리 Context
 * Phase 3: Frontend Authentication UI
 */

// 인증 상태 초기값
const initialAuthState = {
  isAuthenticated: false,
  isLoading: true,
  user: null,
  error: null,
  verificationStatus: null
};

// 액션 타입들
export const AUTH_ACTIONS = {
  LOADING: 'LOADING',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  UPDATE_USER: 'UPDATE_USER',
  SET_VERIFICATION_STATUS: 'SET_VERIFICATION_STATUS',
  CLEAR_ERROR: 'CLEAR_ERROR'
};

// 인증 상태 리듀서
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOADING:
      return {
        ...state,
        isLoading: action.payload
      };

    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        isAuthenticated: true,
        isLoading: false,
        user: action.payload.user,
        error: null
      };

    case AUTH_ACTIONS.LOGIN_FAILURE:
      return {
        ...state,
        isAuthenticated: false,
        isLoading: false,
        user: null,
        error: action.payload.error
      };

    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        isAuthenticated: false,
        isLoading: false,
        user: null,
        error: null,
        verificationStatus: null
      };

    case AUTH_ACTIONS.UPDATE_USER:
      return {
        ...state,
        user: action.payload.user
      };

    case AUTH_ACTIONS.SET_VERIFICATION_STATUS:
      return {
        ...state,
        verificationStatus: action.payload.status
      };

    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };

    default:
      return state;
  }
};

// AuthContext 생성
const AuthContext = createContext(null);

// AuthProvider 컴포넌트
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialAuthState);
  const isInitialized = useRef(false);

  // 로그아웃
  const handleLogout = useCallback(async () => {
    dispatch({ type: AUTH_ACTIONS.LOADING, payload: true });

    try {
      await authService.logout();
    } catch (error) {
      console.error('로그아웃 처리 중 오류:', error);
    } finally {
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  }, []);

  // 초기 인증 상태 확인
  useEffect(() => {
    if (isInitialized.current) return;

    const initializeAuth = async () => {
      isInitialized.current = true;
      dispatch({ type: AUTH_ACTIONS.LOADING, payload: true });

      try {
        const isAuthInitialized = authService.initializeAuth();

        if (isAuthInitialized) {
          // 저장된 사용자 정보 가져오기
          const storedUser = authService.getStoredUser();

          if (storedUser) {
            dispatch({
              type: AUTH_ACTIONS.LOGIN_SUCCESS,
              payload: { user: storedUser }
            });

            // 서버에서 최신 사용자 정보 가져오기 (백그라운드)
            try {
              const currentUser = await authService.getCurrentUser();
              dispatch({
                type: AUTH_ACTIONS.UPDATE_USER,
                payload: { user: currentUser }
              });
            } catch (error) {
              console.warn('사용자 정보 갱신 실패:', error);
              // 토큰이 만료되었을 수 있으므로 로그아웃 처리
              if (error.response?.status === 401) {
                handleLogout();
              }
            }
          } else {
            dispatch({ type: AUTH_ACTIONS.LOADING, payload: false });
          }
        } else {
          dispatch({ type: AUTH_ACTIONS.LOADING, payload: false });
        }
      } catch (error) {
        console.error('인증 초기화 실패:', error);
        dispatch({ type: AUTH_ACTIONS.LOADING, payload: false });
      }
    };

    initializeAuth();
  }, []);

  // Google OAuth 로그인
  const handleGoogleLogin = async (idToken) => {
    dispatch({ type: AUTH_ACTIONS.LOADING, payload: true });

    try {
      const result = await authService.googleLogin(idToken);

      if (result.success) {
        dispatch({
          type: AUTH_ACTIONS.LOGIN_SUCCESS,
          payload: { user: result.user }
        });
        return { success: true, user: result.user };
      } else {
        dispatch({
          type: AUTH_ACTIONS.LOGIN_FAILURE,
          payload: { error: result.error }
        });
        return { success: false, error: result.error };
      }
    } catch (error) {
      const errorMessage = '로그인 중 오류가 발생했습니다.';
      dispatch({
        type: AUTH_ACTIONS.LOGIN_FAILURE,
        payload: { error: errorMessage }
      });
      return { success: false, error: errorMessage };
    }
  };

  // solved.ac 프로필 인증 요청
  const requestSolvedacVerification = async (solvedacUsername) => {
    try {
      const result = await authService.requestSolvedacVerification(solvedacUsername);
      return result;
    } catch (error) {
      console.error('프로필 인증 요청 실패:', error);
      return { success: false, error: '인증 요청에 실패했습니다.' };
    }
  };

  // 인증 상태 확인
  const checkVerificationStatus = async (verificationCode) => {
    try {
      const result = await authService.checkVerificationStatus(verificationCode);

      if (result.success && result.data.status === 'verified') {
        // 인증이 완료되면 사용자 정보 갱신
        const currentUser = await authService.getCurrentUser();
        dispatch({
          type: AUTH_ACTIONS.UPDATE_USER,
          payload: { user: currentUser }
        });
      }

      dispatch({
        type: AUTH_ACTIONS.SET_VERIFICATION_STATUS,
        payload: { status: result.data }
      });

      return result;
    } catch (error) {
      console.error('인증 상태 확인 실패:', error);
      return { success: false, error: '인증 상태 확인에 실패했습니다.' };
    }
  };

  // 사용자 인증 상태 조회
  const getVerificationStatus = async () => {
    try {
      const result = await authService.getVerificationStatus();

      if (result.success) {
        dispatch({
          type: AUTH_ACTIONS.SET_VERIFICATION_STATUS,
          payload: { status: result.data }
        });
      }

      return result;
    } catch (error) {
      console.error('인증 상태 조회 실패:', error);
      return { success: false, error: '인증 상태 조회에 실패했습니다.' };
    }
  };

  // 에러 클리어
  const clearError = useCallback(() => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  }, []);

  // 사용자 정보 갱신
  const updateUser = (user) => {
    dispatch({
      type: AUTH_ACTIONS.UPDATE_USER,
      payload: { user }
    });
  };

  // Context 값
  const contextValue = {
    // 상태
    ...state,

    // 편의 메서드
    isProfileVerified: state.user?.profile_verified || false,

    // 액션들
    login: handleGoogleLogin,
    logout: handleLogout,
    requestSolvedacVerification,
    checkVerificationStatus,
    getVerificationStatus,
    clearError,
    updateUser
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// AuthContext 사용을 위한 커스텀 훅
export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuth는 AuthProvider 내부에서만 사용할 수 있습니다.');
  }

  return context;
};

export default AuthContext;