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

  const getStatImage = (index) => {
    const images = ['/images/푸앙_열공.png', '/images/푸앙_윙크.png', '/images/푸앙_미소.png'];
    return images[index];
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      {stats.map((stat, index) => (
        <div key={index} className="bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition-shadow text-center relative">
          <img
            src={getStatImage(index)}
            alt="푸앙"
            className="w-8 h-8 object-contain absolute top-4 right-4 opacity-60"
          />
          <p className="text-[#143365] text-sm font-medium mb-2">{stat.label}</p>
          <p className={`text-3xl font-bold ${stat.textColor === 'text-gray-900' ? 'text-[#143365]' : stat.textColor}`}>{stat.value}</p>
        </div>
      ))}
    </div>
  );
};

export default UserStats;