import React from 'react';

interface AutoSaveIndicatorProps {
  status: 'saving' | 'saved' | 'error';
  lastSaved?: Date;
}

export function AutoSaveIndicator({ status, lastSaved }: AutoSaveIndicatorProps) {
  const statusConfig = {
    saving: {
      color: 'bg-[#FFCC00]',
      text: 'Saving...',
      textColor: 'text-black'
    },
    saved: {
      color: 'bg-[#00AA00]',
      text: 'Saved',
      textColor: 'text-white'
    },
    error: {
      color: 'bg-[#CC0000]',
      text: 'Error - Not Saved',
      textColor: 'text-white'
    }
  };
  
  const config = statusConfig[status];
  
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-IN', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };
  
  return (
    <div className="flex items-center gap-3 px-4 py-2 border-2 border-[#CCCCCC] rounded bg-white">
      <div className={`w-3 h-3 rounded-full ${config.color}`} aria-hidden="true" />
      <div className="flex flex-col">
        <span className="font-medium text-sm">{config.text}</span>
        {lastSaved && status === 'saved' && (
          <span className="text-xs text-[#333333]">
            Last saved: {formatTime(lastSaved)}
          </span>
        )}
      </div>
    </div>
  );
}
