import React, { useEffect, useState } from 'react';

const ContributionGraph = () => {
  const [monthlyData, setMonthlyData] = useState([]);

  useEffect(() => {
    generateMonthlyContribution();
  }, []);

  const generateMonthlyContribution = () => {
    const months = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'];
    const data = [];

    months.forEach((month, index) => {
      const monthData = {
        name: month,
        weeks: []
      };

      // 각 월마다 4-5주 표시
      const weeksInMonth = index === 1 ? 4 : 5; // 2월은 4주, 나머지는 5주
      for (let week = 0; week < weeksInMonth; week++) {
        const weekData = [];
        for (let day = 0; day < 7; day++) {
          const level = Math.floor(Math.random() * 5);
          weekData.push({
            level,
            tooltip: `${month} ${week * 7 + day + 1}일: ${level}개 문제 해결`
          });
        }
        monthData.weeks.push(weekData);
      }
      data.push(monthData);
    });

    setMonthlyData(data);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-6">해결 목록</h3>
      <div className="space-y-4">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>2024년 문제 해결 현황</span>
          <span>총 247개 문제 해결</span>
        </div>
        
        {/* 월별 해결 현황 */}
        <div className="space-y-3">
          <div className="grid grid-cols-12 gap-2 text-xs text-gray-500 mb-2">
            {monthlyData.map((month, index) => (
              <div key={index} className="text-center">{month.name}</div>
            ))}
          </div>
          
          {/* 월별 그리드 */}
          <div className="grid grid-cols-12 gap-2">
            {monthlyData.map((month, monthIndex) => (
              <div key={monthIndex} className="space-y-1">
                {month.weeks.map((week, weekIndex) => (
                  <div key={weekIndex} className="flex space-x-1">
                    {week.map((day, dayIndex) => (
                      <div
                        key={dayIndex}
                        className={`contribution-day level-${day.level}`}
                        title={day.tooltip}
                      />
                    ))}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
        
        <div className="flex items-center justify-between text-xs text-gray-500 pt-4 border-t">
          <span>적음</span>
          <div className="flex space-x-1">
            <div className="contribution-day level-0"></div>
            <div className="contribution-day level-1"></div>
            <div className="contribution-day level-2"></div>
            <div className="contribution-day level-3"></div>
            <div className="contribution-day level-4"></div>
          </div>
          <span>많음</span>
        </div>
      </div>
    </div>
  );
};

export default ContributionGraph;