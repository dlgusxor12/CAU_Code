import React from 'react';

const UserStats = () => {
  const stats = [
    {
      label: '현재 레이팅',
      value: '1,847',
      textColor: 'text-gray-900'
    },
    {
      label: '현재 티어',
      value: '골드 III',
      textColor: 'tier-gold'
    },
    {
      label: '해결 문제',
      value: '247',
      textColor: 'text-gray-900'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      {stats.map((stat, index) => (
        <div key={index} className="bg-white rounded-xl shadow-sm border p-6 card-hover text-center">
          <p className="text-gray-500 text-sm font-medium mb-2">{stat.label}</p>
          <p className={`text-3xl font-bold ${stat.textColor}`}>{stat.value}</p>
        </div>
      ))}
    </div>
  );
};

export default UserStats;