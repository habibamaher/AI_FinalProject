import React from 'react';

const LoadingIndicator: React.FC = () => {
  return (
    <div className="bg-white text-gray-800 px-4 py-3 rounded-lg rounded-bl-none border border-gray-200 shadow-sm">
      <div className="flex space-x-2">
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
      </div>
    </div>
  );
};

export default LoadingIndicator;
