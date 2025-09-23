import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Navigation from './components/Navigation';
import Footer from './components/Footer';
import ProtectedRoute, { PublicOnlyRoute, UnverifiedOnlyRoute } from './components/ProtectedRoute';

// Pages
import Dashboard from './pages/Dashboard';
import Problems from './pages/Problems';
import Guide from './pages/Guide';
import Feedback from './pages/Feedback';
import Ranking from './pages/Ranking';

// Authentication Pages
import Login from './pages/Login';
import SolvedacAuth from './pages/SolvedacAuth';
import VerifyAuth from './pages/VerifyAuth';
import Profile from './pages/Profile';
import Settings from './pages/Settings';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-[#F2F8FA] flex flex-col">
          <Routes>
            {/* Public Routes (로그인 없이 접근 가능) */}
            <Route
              path="/login"
              element={
                <PublicOnlyRoute>
                  <Login />
                </PublicOnlyRoute>
              }
            />

            {/* Authentication Routes (로그인 필요하지만 프로필 인증 전) */}
            <Route
              path="/auth/solvedac"
              element={
                <UnverifiedOnlyRoute>
                  <SolvedacAuth />
                </UnverifiedOnlyRoute>
              }
            />
            <Route
              path="/auth/verify"
              element={
                <ProtectedRoute>
                  <VerifyAuth />
                </ProtectedRoute>
              }
            />

            {/* Protected Routes (로그인 + 프로필 인증 필요) */}
            <Route
              path="/"
              element={
                <ProtectedRoute requireProfileVerification={true}>
                  <div className="flex flex-col min-h-screen">
                    <Navigation />
                    <main className="flex-grow">
                      <Dashboard />
                    </main>
                    <Footer />
                  </div>
                </ProtectedRoute>
              }
            />
            <Route
              path="/problems"
              element={
                <ProtectedRoute requireProfileVerification={true}>
                  <div className="flex flex-col min-h-screen">
                    <Navigation />
                    <main className="flex-grow">
                      <Problems />
                    </main>
                    <Footer />
                  </div>
                </ProtectedRoute>
              }
            />
            <Route
              path="/guide"
              element={
                <ProtectedRoute requireProfileVerification={true}>
                  <div className="flex flex-col min-h-screen">
                    <Navigation />
                    <main className="flex-grow">
                      <Guide />
                    </main>
                    <Footer />
                  </div>
                </ProtectedRoute>
              }
            />
            <Route
              path="/feedback"
              element={
                <ProtectedRoute requireProfileVerification={true}>
                  <div className="flex flex-col min-h-screen">
                    <Navigation />
                    <main className="flex-grow">
                      <Feedback />
                    </main>
                    <Footer />
                  </div>
                </ProtectedRoute>
              }
            />
            <Route
              path="/ranking"
              element={
                <ProtectedRoute requireProfileVerification={true}>
                  <div className="flex flex-col min-h-screen">
                    <Navigation />
                    <main className="flex-grow">
                      <Ranking />
                    </main>
                    <Footer />
                  </div>
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute requireProfileVerification={true}>
                  <div className="flex flex-col min-h-screen">
                    <Navigation />
                    <main className="flex-grow">
                      <Profile />
                    </main>
                    <Footer />
                  </div>
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute requireProfileVerification={true}>
                  <div className="flex flex-col min-h-screen">
                    <Navigation />
                    <main className="flex-grow">
                      <Settings />
                    </main>
                    <Footer />
                  </div>
                </ProtectedRoute>
              }
            />

            {/* 404 처리 */}
            <Route
              path="*"
              element={
                <div className="min-h-screen bg-[#F2F8FA] flex items-center justify-center">
                  <div className="text-center space-y-4">
                    <h1 className="text-4xl font-bold text-gray-800">404</h1>
                    <p className="text-gray-600">페이지를 찾을 수 없습니다.</p>
                    <a
                      href="/"
                      className="inline-block bg-[#2B95C3] text-white px-6 py-3 rounded-lg hover:bg-[#1F7AA8] transition-colors"
                    >
                      홈으로 돌아가기
                    </a>
                  </div>
                </div>
              }
            />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;