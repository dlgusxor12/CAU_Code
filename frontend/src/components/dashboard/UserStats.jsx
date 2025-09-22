import React, { useState, useEffect } from 'react';
import { userService } from '../../services';

const UserStats = () => {
  const [stats, setStats] = useState([
    {
      label: '현재 레이팅',
      value: '...',
      textColor: 'text-gray-900'
    },
    {
      label: '현재 티어',
      value: '...',
      textColor: 'tier-gold'
    },
    {
      label: '해결 문제',
      value: '...',
      textColor: 'text-gray-900'
    }
  ]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserStats();
  }, []);

  const fetchUserStats = async () => {
    try {
      setLoading(true);
      const response = await userService.getUserStats();

      if (response.status === 'success' && response.data) {
        const data = response.data;
        setStats([
          {
            label: '현재 레이팅',
            value: data.current_rating?.toLocaleString() || '0',
            textColor: 'text-gray-900'
          },
          {
            label: '현재 티어',
            value: data.tier_name || 'Unrated',
            textColor: 'tier-gold'
          },
          {
            label: '해결 문제',
            value: data.solved_problems?.toString() || '0',
            textColor: 'text-gray-900'
          }
        ]);
      }
    } catch (error) {
      console.error('Failed to fetch user stats:', error);
    } finally {
      setLoading(false);
    }
  };

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
          <p className={`text-3xl font-bold ${stat.textColor === 'text-gray-900' ? 'text-[#143365]' : stat.textColor}`}>
            {loading ? (
              <div className="animate-pulse bg-gray-200 h-8 w-16 mx-auto rounded"></div>
            ) : (
              stat.value
            )}
          </p>
        </div>
      ))}
    </div>
  );
};

export default UserStats;