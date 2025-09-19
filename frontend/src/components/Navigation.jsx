import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path ? 'text-blue-600 font-semibold' : 'text-gray-600 hover:text-blue-600';
  };

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-1">
            <img
              src="/images/푸앙_열공.png"
              alt="푸앙"
              className="w-10 h-10 object-contain"
            />
            <Link to="/" className="text-2xl font-bold text-blue-600 hover:text-blue-700">
              CAU Code
            </Link>
          </div>
          <div className="flex items-center space-x-6">
            <Link to="/problems" className={`font-medium transition-colors ${isActive('/problems')}`}>
              문제 추천
            </Link>
            <Link to="/guide" className={`font-medium transition-colors ${isActive('/guide')}`}>
              문제 가이드
            </Link>
            <Link to="/ranking" className={`font-medium transition-colors ${isActive('/ranking')}`}>
              랭킹
            </Link>
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-semibold">김</span>
              </div>
              <span className="text-sm font-medium text-gray-700">김중앙</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;