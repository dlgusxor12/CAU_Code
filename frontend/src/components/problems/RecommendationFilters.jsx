import React, { useState, useEffect } from 'react';
import { problemService } from '../../services';

const RecommendationFilters = ({ onFilterChange }) => {
  const [filters, setFilters] = useState({
    tier_min: null,
    tier_max: null,
    algorithm: '',
    difficulty_class: null
  });
  const [filterOptions, setFilterOptions] = useState({
    available_tiers: [],
    available_algorithms: [],
    difficulty_classes: []
  });

  useEffect(() => {
    loadFilterOptions();
  }, []);

  const loadFilterOptions = async () => {
    try {
      const response = await problemService.getFilterOptions();
      if (response.status === 'success' && response.data) {
        setFilterOptions(response.data);
      }
    } catch (error) {
      console.error('Failed to load filter options:', error);
    }
  };

  const handleFilterChange = (key, value) => {
    const parsedValue = value === '' ? null : (key.includes('tier') || key === 'difficulty_class' ? parseInt(value) : value);
    const newFilters = { ...filters, [key]: parsedValue };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const clearFilters = () => {
    const clearedFilters = { tier_min: null, tier_max: null, algorithm: '', difficulty_class: null };
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
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 최소 티어 필터 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">최소 티어</label>
          <select
            value={filters.tier_min || ''}
            onChange={(e) => handleFilterChange('tier_min', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">선택 없음</option>
            {filterOptions.available_tiers.map(tier => (
              <option key={tier.tier_id} value={tier.tier_id}>{tier.tier_name}</option>
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
            {filterOptions.available_tiers.map(tier => (
              <option key={tier.tier_id} value={tier.tier_id}>{tier.tier_name}</option>
            ))}
          </select>
        </div>

        {/* 알고리즘 필터 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">알고리즘</label>
          <select
            value={filters.algorithm || ''}
            onChange={(e) => handleFilterChange('algorithm', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">모든 알고리즘</option>
            {filterOptions.available_algorithms.map(algorithm => (
              <option key={algorithm.tag_name} value={algorithm.tag_name}>
                {algorithm.tag_name} ({algorithm.problem_count})
              </option>
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
            {filterOptions.difficulty_classes.map(difficulty => (
              <option key={difficulty} value={difficulty}>클래스 {difficulty}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};

export default RecommendationFilters;