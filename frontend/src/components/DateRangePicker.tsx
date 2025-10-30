import React, { useState } from 'react';
import { format, subDays } from 'date-fns';

interface DateRangePickerProps {
  onApply: (startDate: string, endDate: string) => void;
  onReset: () => void;
}

const DateRangePicker: React.FC<DateRangePickerProps> = ({ onApply, onReset }) => {
  const today = format(new Date(), 'yyyy-MM-dd');
  const thirtyDaysAgo = format(subDays(new Date(), 30), 'yyyy-MM-dd');
  
  const [startDate, setStartDate] = useState(thirtyDaysAgo);
  const [endDate, setEndDate] = useState(today);
  const [showPicker, setShowPicker] = useState(false);

  const handleApply = () => {
    if (startDate && endDate) {
      onApply(startDate, endDate);
      setShowPicker(false);
    }
  };

  const handleReset = () => {
    setStartDate(thirtyDaysAgo);
    setEndDate(today);
    onReset();
    setShowPicker(false);
  };

  const quickRanges = [
    { label: 'Last 7 days', days: 7 },
    { label: 'Last 30 days', days: 30 },
    { label: 'Last 60 days', days: 60 },
    { label: 'Last 90 days', days: 90 },
  ];

  const handleQuickRange = (days: number) => {
    const end = new Date();
    const start = subDays(end, days);
    setStartDate(format(start, 'yyyy-MM-dd'));
    setEndDate(format(end, 'yyyy-MM-dd'));
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowPicker(!showPicker)}
        className="flex items-center space-x-2 bg-white border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors shadow-sm"
      >
        <span>📅</span>
        <span className="text-sm font-medium">Custom Date Range</span>
      </button>

      {showPicker && (
        <>
          {/* Overlay */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setShowPicker(false)}
          ></div>

          {/* Picker Panel */}
          <div className="absolute top-full mt-2 right-0 bg-white rounded-lg shadow-xl border border-gray-200 p-4 z-50 w-80 animate-fade-in">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">
              Select Date Range
            </h3>

            {/* Quick Ranges */}
            <div className="mb-4">
              <p className="text-xs text-gray-600 mb-2">Quick Ranges:</p>
              <div className="grid grid-cols-2 gap-2">
                {quickRanges.map((range) => (
                  <button
                    key={range.days}
                    onClick={() => handleQuickRange(range.days)}
                    className="text-xs px-3 py-2 bg-gray-100 hover:bg-blue-100 rounded text-gray-700 hover:text-blue-700 transition-colors"
                  >
                    {range.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Date Inputs */}
            <div className="space-y-3 mb-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Start Date
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  max={endDate}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  End Date
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  min={startDate}
                  max={today}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-between gap-2">
              <button
                onClick={handleReset}
                className="flex-1 px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors text-sm font-medium"
              >
                Reset
              </button>
              <button
                onClick={handleApply}
                className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                Apply
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default DateRangePicker;