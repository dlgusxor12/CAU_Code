import React from 'react';

const WeeklyStats = () => {
  const stats = [
    {
      title: '해결한 문제',
      value: '12개',
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
      title: '연속 해결 일수',
      value: '5일',
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
      title: '정답률',
      value: '78%',
      icon: (
        <svg className="w-4 h-4 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
        </svg>
      ),
      bgColor: 'bg-orange-50',
      iconBgColor: 'bg-orange-100',
      textColor: 'text-orange-600'
    }
  ];

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
            <span className={`font-bold ${stat.textColor} text-lg`}>{stat.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WeeklyStats;