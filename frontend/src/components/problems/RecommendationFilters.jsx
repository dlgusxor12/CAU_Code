import React, { useState } from 'react';

const RecommendationFilters = ({ onFilterChange }) => {
  const [filters, setFilters] = useState({
    tier: '',
    algorithm: '',
    difficulty: ''
  });

  const tiers = ['브론즈', '실버', '골드', '플래티넘', '다이아몬드'];
  const algorithms = ['이진 탐색', '그리디', 'DP', '구현', '그래프', '수학', '문자열', '정렬'];
  const difficulties = ['1', '2', '3', '4', '5'];

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const clearFilters = () => {
    const clearedFilters = { tier: '', algorithm: '', difficulty: '' };
    setFilters(clearedFilters);
    onFilterChange(clearedFilters);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">문제 필터</h3>
        <button 
          onClick={clearFilters}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          필터 초기화
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* 티어 필터 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">티어</label>
          <select 
            value={filters.tier}
            onChange={(e) => handleFilterChange('tier', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">모든 티어</option>
            {tiers.map(tier => (
              <option key={tier} value={tier}>{tier}</option>
            ))}
          </select>
        </div>

        {/* 알고리즘 필터 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">알고리즘</label>
          <select 
            value={filters.algorithm}
            onChange={(e) => handleFilterChange('algorithm', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">모든 알고리즘</option>
            {algorithms.map(algorithm => (
              <option key={algorithm} value={algorithm}>{algorithm}</option>
            ))}
          </select>
        </div>

        {/* 난이도 필터 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">난이도</label>
          <select 
            value={filters.difficulty}
            onChange={(e) => handleFilterChange('difficulty', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">모든 난이도</option>
            {difficulties.map(difficulty => (
              <option key={difficulty} value={difficulty}>난이도 {difficulty}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};

export default RecommendationFilters;