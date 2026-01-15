// 'use client';

// import React, { useState, useEffect } from 'react';
// import { PostCountInputProps } from '@/types';

// const DEFAULT_POST_COUNT = 20;
// const MIN_POST_COUNT = 1;
// const MAX_POST_COUNT = 100;

// export default function PostCountInput({
//   value,
//   onChange,
//   error
// }: PostCountInputProps) {
//   const [inputValue, setInputValue] = useState(value.toString());
//   const [validationError, setValidationError] = useState<string>('');

//   // Update input value when prop changes
//   useEffect(() => {
//     setInputValue(value.toString());
//   }, [value]);

//   const validatePostCount = (count: number): string => {
//     if (isNaN(count)) {
//       return 'Please enter a valid number';
//     }
//     if (count < MIN_POST_COUNT) {
//       return `Post count must be at least ${MIN_POST_COUNT}`;
//     }
//     if (count > MAX_POST_COUNT) {
//       return `Post count cannot exceed ${MAX_POST_COUNT}`;
//     }
//     return '';
//   };

//   const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
//     const newValue = e.target.value;
//     setInputValue(newValue);

//     // Parse and validate the input
//     const numericValue = parseInt(newValue, 10);
//     const errorMessage = validatePostCount(numericValue);
    
//     setValidationError(errorMessage);

//     // Only call onChange if the value is valid
//     if (!errorMessage && !isNaN(numericValue)) {
//       onChange(numericValue);
//     }
//   };

//   const handleBlur = () => {
//     // If input is empty or invalid, reset to default
//     const numericValue = parseInt(inputValue, 10);
//     if (isNaN(numericValue) || validationError) {
//       setInputValue(DEFAULT_POST_COUNT.toString());
//       setValidationError('');
//       onChange(DEFAULT_POST_COUNT);
//     }
//   };

//   const displayError = error || validationError;

//   return (
//     <div className="space-y-2">
//       <label 
//         htmlFor="post-count-input"
//         className="block text-sm font-semibold text-black"
//       >
//         📊 Number of Posts
//       </label>
//       <div className="relative">
//         <input
//           id="post-count-input"
//           type="number"
//           min={MIN_POST_COUNT}
//           max={MAX_POST_COUNT}
//           value={inputValue}
//           onChange={handleInputChange}
//           onBlur={handleBlur}
//           className={`
//             block w-full px-4 py-2.5 pr-16 border-2 rounded-lg shadow-sm text-sm
//             focus:outline-none focus:ring-2 transition-all
//             ${
//               displayError
//                 ? 'border-red-300 focus:border-red-500 focus:ring-red-500 bg-red-50'
//                 : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500 hover:border-gray-400'
//             }
//           `}
//           placeholder={`Enter number (${MIN_POST_COUNT}-${MAX_POST_COUNT})`}
//           aria-invalid={!!displayError}
//           aria-describedby={displayError ? 'post-count-error' : 'post-count-help'}
//         />
//         <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
//           <span className="text-gray-500 text-sm font-medium">posts</span>
//         </div>
//       </div>
//       {displayError && (
//         <div 
//           id="post-count-error"
//           className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-2 flex items-start space-x-2"
//           role="alert"
//         >
//           <span className="text-red-500">⚠️</span>
//           <span>{displayError}</span>
//         </div>
//       )}
//       <div id="post-count-help" className="text-xs text-gray-500 flex items-center justify-between">
//         <span>Default: {DEFAULT_POST_COUNT} posts</span>
//         <span>Range: {MIN_POST_COUNT}-{MAX_POST_COUNT}</span>
//       </div>
//     </div>
//   );
// }

'use client';

import React, { useState, useEffect } from 'react';
import { PostCountInputProps } from '@/types';

/**
 * Constants for the component
 */
const DEFAULT_POST_COUNT = 20;
const MIN_POST_COUNT = 1;
const MAX_POST_COUNT = 100;

export default function PostCountInput({
  value,
  onChange,
  error
}: PostCountInputProps) {
  const [inputValue, setInputValue] = useState(value.toString());
  const [validationError, setValidationError] = useState<string>('');

  // Sync internal state if the external prop changes
  useEffect(() => {
    setInputValue(value.toString());
  }, [value]);

  const validatePostCount = (count: number): string => {
    if (isNaN(count)) {
      return 'Please enter a valid number';
    }
    if (count < MIN_POST_COUNT) {
      return `Post count must be at least ${MIN_POST_COUNT}`;
    }
    if (count > MAX_POST_COUNT) {
      return `Post count cannot exceed ${MAX_POST_COUNT}`;
    }
    return '';
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);

    const numericValue = parseInt(newValue, 10);
    const errorMessage = validatePostCount(numericValue);
    
    setValidationError(errorMessage);

    // Update parent only if value is valid
    if (!errorMessage && !isNaN(numericValue)) {
      onChange(numericValue);
    }
  };

  const handleBlur = () => {
    const numericValue = parseInt(inputValue, 10);
    // If empty or invalid on blur, reset to safe default
    if (isNaN(numericValue) || validationError) {
      setInputValue(DEFAULT_POST_COUNT.toString());
      setValidationError('');
      onChange(DEFAULT_POST_COUNT);
    }
  };

  // Combine external and internal errors
  const displayError = error || validationError;

  return (
    <div className="space-y-2">
      {/* Label: Using gray-900 for maximum visibility */}
      <label 
        htmlFor="post-count-input"
        className="block text-sm font-bold text-gray-900"
      >
        📊 Number of Posts
      </label>

      <div className="relative">
        <input
          id="post-count-input"
          type="number"
          min={MIN_POST_COUNT}
          max={MAX_POST_COUNT}
          value={inputValue}
          onChange={handleInputChange}
          onBlur={handleBlur}
          className={`
            block w-full px-4 py-3 pr-16 border-2 rounded-xl shadow-sm text-base transition-all
            focus:outline-none focus:ring-2
            ${
              displayError
                ? 'border-red-500 focus:border-red-600 focus:ring-red-100 bg-red-50 text-red-900'
                : 'border-gray-300 focus:border-blue-500 focus:ring-blue-100 hover:border-gray-400 text-gray-900'
            }
          `}
          placeholder={`${MIN_POST_COUNT}-${MAX_POST_COUNT}`}
          aria-invalid={!!displayError}
        />
        
        {/* Suffix: Darkened to gray-600 for better contrast */}
        <div className="absolute inset-y-0 right-0 flex items-center pr-4 pointer-events-none">
          <span className="text-gray-600 text-sm font-semibold">posts</span>
        </div>
      </div>

      {/* Footer info: Increased from gray-500 to gray-600 for legibility */}
      <div className="flex items-center justify-between px-1 text-xs font-medium text-gray-600">
        <span>Default: {DEFAULT_POST_COUNT} posts</span>
        <span>Range: {MIN_POST_COUNT}-{MAX_POST_COUNT}</span>
      </div>

      {/* Error Message */}
      {displayError && (
        <div 
          className="flex items-center space-x-2 p-2.5 mt-1 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg animate-in fade-in slide-in-from-top-1"
          role="alert"
        >
          <span>⚠️</span>
          <span className="font-medium">{displayError}</span>
        </div>
      )}
    </div>
  );
}