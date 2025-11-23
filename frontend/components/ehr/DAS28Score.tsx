import React from 'react';

interface DAS28ScoreProps {
  score: number;
  showLabel?: boolean;
}

export function DAS28Score({ score, showLabel = true }: DAS28ScoreProps) {
  const getScoreCategory = (score: number) => {
    if (score < 2.6) return {
      label: 'Remission',
      color: 'bg-[#00AA00]',
      textColor: 'text-white'
    };
    if (score < 3.2) return {
      label: 'Low Activity',
      color: 'bg-[#FFCC00]',
      textColor: 'text-black'
    };
    if (score <= 5.1) return {
      label: 'Moderate Activity',
      color: 'bg-[#FF9900]',
      textColor: 'text-white'
    };
    return {
      label: 'High Activity',
      color: 'bg-[#CC0000]',
      textColor: 'text-white'
    };
  };
  
  const category = getScoreCategory(score);
  
  return (
    <div className="flex flex-col gap-2">
      {showLabel && (
        <label className="block">DAS28 Score</label>
      )}
      <div className={`flex items-center justify-between px-4 py-3 border-2 rounded ${category.color} ${category.textColor}`}>
        <span className="font-medium">Score: {score.toFixed(2)}</span>
        <span className="font-medium">{category.label}</span>
      </div>
    </div>
  );
}

interface DAS28CalculatorProps {
  tenderJointCount: number;
  swollenJointCount: number;
  esr: number;
  patientGlobal: number;
  onCalculate?: (score: number) => void;
}

export function DAS28Calculator({ 
  tenderJointCount, 
  swollenJointCount, 
  esr, 
  patientGlobal,
  onCalculate 
}: DAS28CalculatorProps) {
  const calculateDAS28 = () => {
    // DAS28-ESR formula
    const score = 0.56 * Math.sqrt(tenderJointCount) + 
                  0.28 * Math.sqrt(swollenJointCount) + 
                  0.70 * Math.log(esr) + 
                  0.014 * patientGlobal;
    
    if (onCalculate) {
      onCalculate(score);
    }
    
    return score;
  };
  
  const score = calculateDAS28();
  
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 border-2 border-[#CCCCCC] rounded bg-white">
          <div className="text-sm text-[#333333]">Tender Joints</div>
          <div className="text-2xl font-medium">{tenderJointCount}</div>
        </div>
        <div className="p-4 border-2 border-[#CCCCCC] rounded bg-white">
          <div className="text-sm text-[#333333]">Swollen Joints</div>
          <div className="text-2xl font-medium">{swollenJointCount}</div>
        </div>
        <div className="p-4 border-2 border-[#CCCCCC] rounded bg-white">
          <div className="text-sm text-[#333333]">ESR (mm/hr)</div>
          <div className="text-2xl font-medium">{esr}</div>
        </div>
        <div className="p-4 border-2 border-[#CCCCCC] rounded bg-white">
          <div className="text-sm text-[#333333]">Patient Global (0-100)</div>
          <div className="text-2xl font-medium">{patientGlobal}</div>
        </div>
      </div>
      
      <DAS28Score score={score} showLabel={false} />
    </div>
  );
}
