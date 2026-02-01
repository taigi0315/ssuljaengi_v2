'use client';

import React from 'react';
import { TimeRangeSelectorProps, TimeRangeOption } from '@/types';

const DEFAULT_TIME_RANGES: TimeRangeOption[] = [
  {
    value: '1h',
    label: '1 Hour',
    description: 'Posts from the last hour'
  },
  {
    value: '1d',
    label: '1 Day',
    description: 'Posts from the last day'
  },
  {
    value: '10d',
    label: '10 Days',
    description: 'Posts from the last 10 days'
  },
  {
    value: '100d',
    label: '100 Days',
    description: 'Posts from the last 100 days'
  }
];

export default function TimeRangeSelector({
  selected,
  onChange,
  options = DEFAULT_TIME_RANGES
}: TimeRangeSelectorProps) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-semibold text-gray-700">
        ⏰ Time Range
      </label>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {options.map((option) => (
          <button
            key={option.value}
            onClick={() => onChange(option.value)}
            className={`
              px-3 py-2.5 text-sm font-medium rounded-lg border-2 transition-all duration-200
              transform hover:scale-105 active:scale-95 focus:ring-2 focus:ring-offset-2
              ${
                selected === option.value
                  ? 'bg-blue-600 text-white border-blue-600 shadow-md hover:bg-blue-700 focus:ring-blue-500'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-blue-50 hover:border-blue-400 focus:ring-blue-300'
              }
            `}
            title={option.description}
            aria-label={`Select ${option.label} time range`}
            aria-pressed={selected === option.value}
          >
            {option.label}
          </button>
        ))}
      </div>
      <p className="text-xs text-gray-500 mt-1">
        Select how far back to search for viral posts
      </p>
    </div>
  );
}