import React, { useState, useEffect } from 'react';
import { problemService } from '../../services';

const RecommendationFilters = ({ onFilterChange }) => {
  const [filters, setFilters] = useState({
    tier_min: null,
    tier_max: null,
    difficulty_class: null
  });
  // 하드코딩된 티어 옵션 (브론즈, 실버, 골드 단위)
  const tierOptions = [
    { value: 1, label: '브론즈' },
    { value: 6, label: '실버' },
    { value: 11, label: '골드' },
    { value: 16, label: '플래티넘' },
    { value: 21, label: '다이아몬드' },
    { value: 26, label: '루비' }
  ];

  // 하드코딩된 클래스 옵션 (1-10)
  const classOptions = Array.from({ length: 10 }, (_, i) => i + 1);

  // API 호출 제거 - 하드코딩된 옵션 사용

  const handleFilterChange = (key, value) => {
    const parsedValue = value === '' ? null : parseInt(value);
    const newFilters = { ...filters, [key]: parsedValue };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const clearFilters = () => {
    const clearedFilters = { tier_min: null, tier_max: null, difficulty_class: null };
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
        {/* 최소 티어 필터 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">최소 티어</label>
          <select
            value={filters.tier_min || ''}
            onChange={(e) => handleFilterChange('tier_min', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">선택 없음</option>
            {tierOptions.map(tier => (
              <option key={tier.value} value={tier.value}>{tier.label}</option>
            ))}
          </select>
        </div>

        {/* 최대 티어 필터 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">최대 티어</label>
          <select
            value={filters.tier_max || ''}
            onChange={(e) => handleFilterChange('tier_max', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">선택 없음</option>
            {tierOptions.map(tier => (
              <option key={tier.value} value={tier.value}>{tier.label}</option>
            ))}
          </select>
        </div>

        {/* 난이도 클래스 필터 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">난이도 클래스</label>
          <select
            value={filters.difficulty_class || ''}
            onChange={(e) => handleFilterChange('difficulty_class', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">모든 난이도</option>
            {classOptions.map(classNum => (
              <option key={classNum} value={classNum}>클래스 {classNum}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};

export default RecommendationFilters;