import React, { useRef, useEffect, useState } from 'react';

interface Joint {
  id: string;
  name: string;
  x: number;
  y: number;
  swelling: number; // 0-3
  tenderness: boolean;
}

const INITIAL_JOINTS: Joint[] = [
  // Right hand
  { id: 'r-thumb-ip', name: 'R Thumb IP', x: 150, y: 100, swelling: 0, tenderness: false },
  { id: 'r-index-pip', name: 'R Index PIP', x: 180, y: 80, swelling: 0, tenderness: false },
  { id: 'r-middle-pip', name: 'R Middle PIP', x: 200, y: 70, swelling: 0, tenderness: false },
  { id: 'r-ring-pip', name: 'R Ring PIP', x: 220, y: 80, swelling: 0, tenderness: false },
  { id: 'r-pinky-pip', name: 'R Pinky PIP', x: 240, y: 95, swelling: 0, tenderness: false },
  
  // Right wrist
  { id: 'r-wrist', name: 'R Wrist', x: 190, y: 150, swelling: 0, tenderness: false },
  
  // Left hand
  { id: 'l-thumb-ip', name: 'L Thumb IP', x: 450, y: 100, swelling: 0, tenderness: false },
  { id: 'l-index-pip', name: 'L Index PIP', x: 420, y: 80, swelling: 0, tenderness: false },
  { id: 'l-middle-pip', name: 'L Middle PIP', x: 400, y: 70, swelling: 0, tenderness: false },
  { id: 'l-ring-pip', name: 'L Ring PIP', x: 380, y: 80, swelling: 0, tenderness: false },
  { id: 'l-pinky-pip', name: 'L Pinky PIP', x: 360, y: 95, swelling: 0, tenderness: false },
  
  // Left wrist
  { id: 'l-wrist', name: 'L Wrist', x: 410, y: 150, swelling: 0, tenderness: false },
  
  // Elbows
  { id: 'r-elbow', name: 'R Elbow', x: 150, y: 250, swelling: 0, tenderness: false },
  { id: 'l-elbow', name: 'L Elbow', x: 450, y: 250, swelling: 0, tenderness: false },
  
  // Shoulders
  { id: 'r-shoulder', name: 'R Shoulder', x: 100, y: 350, swelling: 0, tenderness: false },
  { id: 'l-shoulder', name: 'L Shoulder', x: 500, y: 350, swelling: 0, tenderness: false },
  
  // Knees
  { id: 'r-knee', name: 'R Knee', x: 200, y: 450, swelling: 0, tenderness: false },
  { id: 'l-knee', name: 'L Knee', x: 400, y: 450, swelling: 0, tenderness: false },
];

interface JointAssessmentProps {
  onChange?: (joints: Joint[]) => void;
}

export function JointAssessment({ onChange }: JointAssessmentProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [joints, setJoints] = useState<Joint[]>(INITIAL_JOINTS);
  const [selectedJoint, setSelectedJoint] = useState<string | null>(null);
  
  const JOINT_RADIUS = 20;
  
  useEffect(() => {
    drawCanvas();
  }, [joints, selectedJoint]);
  
  const drawCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw title
    ctx.fillStyle = '#000000';
    ctx.font = '600 18px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Joint Assessment - Click for Swelling (0-3), Right-Click for Tenderness', canvas.width / 2, 30);
    
    // Draw side labels
    ctx.font = '400 16px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
    ctx.fillText('Right Side', 150, 60);
    ctx.fillText('Left Side', 450, 60);
    
    // Draw joints
    joints.forEach(joint => {
      const isSelected = selectedJoint === joint.id;
      
      // Draw swelling circle (larger based on swelling grade)
      const swellingRadius = JOINT_RADIUS + (joint.swelling * 5);
      if (joint.swelling > 0) {
        ctx.fillStyle = '#FF9900';
        ctx.globalAlpha = 0.3;
        ctx.beginPath();
        ctx.arc(joint.x, joint.y, swellingRadius, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;
      }
      
      // Draw main joint circle
      ctx.fillStyle = isSelected ? '#0066CC' : '#FFFFFF';
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(joint.x, joint.y, JOINT_RADIUS, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      
      // Draw tenderness indicator (red cross)
      if (joint.tenderness) {
        ctx.strokeStyle = '#CC0000';
        ctx.lineWidth = 3;
        const crossSize = 10;
        ctx.beginPath();
        ctx.moveTo(joint.x - crossSize, joint.y - crossSize);
        ctx.lineTo(joint.x + crossSize, joint.y + crossSize);
        ctx.moveTo(joint.x + crossSize, joint.y - crossSize);
        ctx.lineTo(joint.x - crossSize, joint.y + crossSize);
        ctx.stroke();
      }
      
      // Draw swelling grade
      if (joint.swelling > 0) {
        ctx.fillStyle = '#000000';
        ctx.font = '600 14px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(joint.swelling.toString(), joint.x, joint.y + 5);
      }
      
      // Draw joint name
      ctx.fillStyle = '#333333';
      ctx.font = '400 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(joint.name, joint.x, joint.y + JOINT_RADIUS + 15);
    });
  };
  
  const findJointAtPosition = (x: number, y: number): Joint | null => {
    const canvas = canvasRef.current;
    if (!canvas) return null;
    
    const rect = canvas.getBoundingClientRect();
    const canvasX = x - rect.left;
    const canvasY = y - rect.top;
    
    return joints.find(joint => {
      const distance = Math.sqrt(
        Math.pow(canvasX - joint.x, 2) + Math.pow(canvasY - joint.y, 2)
      );
      return distance <= JOINT_RADIUS;
    }) || null;
  };
  
  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const joint = findJointAtPosition(e.clientX, e.clientY);
    if (!joint) return;
    
    // Cycle through swelling grades 0 -> 1 -> 2 -> 3 -> 0
    const newJoints = joints.map(j => {
      if (j.id === joint.id) {
        return { ...j, swelling: (j.swelling + 1) % 4 };
      }
      return j;
    });
    
    setJoints(newJoints);
    setSelectedJoint(joint.id);
    
    if (onChange) {
      onChange(newJoints);
    }
  };
  
  const handleCanvasRightClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    
    const joint = findJointAtPosition(e.clientX, e.clientY);
    if (!joint) return;
    
    // Toggle tenderness
    const newJoints = joints.map(j => {
      if (j.id === joint.id) {
        return { ...j, tenderness: !j.tenderness };
      }
      return j;
    });
    
    setJoints(newJoints);
    setSelectedJoint(joint.id);
    
    if (onChange) {
      onChange(newJoints);
    }
  };
  
  const handleReset = () => {
    setJoints(INITIAL_JOINTS);
    setSelectedJoint(null);
    if (onChange) {
      onChange(INITIAL_JOINTS);
    }
  };
  
  const getTotalCounts = () => {
    const swollenCount = joints.filter(j => j.swelling > 0).length;
    const tenderCount = joints.filter(j => j.tenderness).length;
    return { swollenCount, tenderCount };
  };
  
  const { swollenCount, tenderCount } = getTotalCounts();
  
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3>Joint Assessment</h3>
        <button
          onClick={handleReset}
          className="px-4 py-2 border-2 border-[#CCCCCC] rounded bg-white hover:bg-[#F5F5F5]"
        >
          Reset All
        </button>
      </div>
      
      <div className="border-2 border-[#CCCCCC] rounded bg-white p-4">
        <canvas
          ref={canvasRef}
          width={600}
          height={550}
          onClick={handleCanvasClick}
          onContextMenu={handleCanvasRightClick}
          className="w-full cursor-pointer"
          aria-label="Interactive joint assessment canvas. Click joints to mark swelling grade 0-3. Right-click joints to mark tenderness."
        />
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 border-2 border-[#CCCCCC] rounded bg-white">
          <div className="text-sm text-[#333333]">Swollen Joints</div>
          <div className="text-2xl font-medium">{swollenCount}/28</div>
        </div>
        <div className="p-4 border-2 border-[#CCCCCC] rounded bg-white">
          <div className="text-sm text-[#333333]">Tender Joints</div>
          <div className="text-2xl font-medium">{tenderCount}/28</div>
        </div>
      </div>
      
      <div className="p-4 border-2 border-[#CCCCCC] rounded bg-[#F5F5F5]">
        <h4 className="mb-2">Instructions</h4>
        <ul className="space-y-1 text-sm">
          <li>• <strong>Left Click</strong> on joint: Cycle through swelling grades (0 → 1 → 2 → 3 → 0)</li>
          <li>• <strong>Right Click</strong> on joint: Toggle tenderness (red cross)</li>
          <li>• Swelling grades: 0 = None, 1 = Mild, 2 = Moderate, 3 = Severe</li>
        </ul>
      </div>
    </div>
  );
}
