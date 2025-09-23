import React, { useState, useEffect } from 'react';
import { userService } from '../../services';

const WeeklyStats = () => {
  const [stats, setStats] = useState([
    {
      title: '해결한 문제',
      value: '...',
      icon: (
        <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
      ),
      bgColor: 'bg-blue-50',
      iconBgColor: 'bg-blue-100',
      textColor: 'text-blue-600'
    },
    {
      title: '새로운 알고리즘',
      value: '...',
      icon: (
        <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
          <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
        </svg>
      ),
      bgColor: 'bg-green-50',
      iconBgColor: 'bg-green-100',
      textColor: 'text-green-600'
    },
    {
      title: '피드백 요청 수',
      value: '...',
      icon: (
        <svg className="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
          <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/>
          <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"/>
        </svg>
      ),
      bgColor: 'bg-purple-50',
      iconBgColor: 'bg-purple-100',
      textColor: 'text-purple-600'
    }
  ]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWeeklyStats();
  }, []);

  const fetchWeeklyStats = async () => {
    try {
      setLoading(true);
      const response = await userService.getWeeklyStats();

      if (response.status === 'success' && response.data) {
        const data = response.data;
        setStats([
          {
            title: '해결한 문제',
            value: `${data.problems_solved || 0}개`,
            icon: (
              <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            ),
            bgColor: 'bg-blue-50',
            iconBgColor: 'bg-blue-100',
            textColor: 'text-blue-600'
          },
          {
            title: '새로운 알고리즘',
            value: `${data.new_algorithms || 0}개`,
            icon: (
              <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
              </svg>
            ),
            bgColor: 'bg-green-50',
            iconBgColor: 'bg-green-100',
            textColor: 'text-green-600'
          },
          {
            title: '피드백 요청 수',
            value: `${data.feedback_requests || 0}개`,
            icon: (
              <svg className="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/>
                <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"/>
              </svg>
            ),
            bgColor: 'bg-purple-50',
            iconBgColor: 'bg-purple-100',
            textColor: 'text-purple-600'
          }
        ]);
      }
    } catch (error) {
      console.error('Failed to fetch weekly stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">이번 주 통계</h3>
      <div className="space-y-4">
        {stats.map((stat, index) => (
          <div key={index} className={`flex justify-between items-center p-3 ${stat.bgColor} rounded-lg`}>
            <div className="flex items-center space-x-3">
              <div className={`w-8 h-8 ${stat.iconBgColor} rounded-full flex items-center justify-center`}>
                {stat.icon}
              </div>
              <span className="text-gray-700 font-medium">{stat.title}</span>
            </div>
            <span className={`font-bold ${stat.textColor} text-lg`}>
              {loading ? (
                <div className="animate-pulse bg-gray-200 h-5 w-8 rounded"></div>
              ) : (
                stat.value
              )}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WeeklyStats;