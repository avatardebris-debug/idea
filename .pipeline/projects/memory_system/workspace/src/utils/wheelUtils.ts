import { WheelSlice } from './types';

export const calculateSliceAngle = (index: number, totalSlices: number): number => {
  return (index * (360 / totalSlices)) - (360 / totalSlices) / 2;
};

export const calculateSliceCoordinates = (
  index: number,
  totalSlices: number,
  radius: number,
  rotation: number
): { x: number; y: number; angle: number } => {
  const angle = calculateSliceAngle(index, totalSlices) + rotation;
  const angleRad = (angle * Math.PI) / 180;
  
  return {
    x: radius * Math.cos(angleRad),
    y: radius * Math.sin(angleRad),
    angle,
  };
};

export const createArcPath = (
  radius: number,
  startAngle: number,
  endAngle: number,
  innerRadius: number = 0
): string => {
  const startRad = (startAngle * Math.PI) / 180;
  const endRad = (endAngle * Math.PI) / 180;
  
  const x1 = radius * Math.cos(startRad);
  const y1 = radius * Math.sin(startRad);
  const x2 = radius * Math.cos(endRad);
  const y2 = radius * Math.sin(endRad);
  
  const x3 = innerRadius * Math.cos(endRad);
  const y3 = innerRadius * Math.sin(endRad);
  const x4 = innerRadius * Math.cos(startRad);
  const y4 = innerRadius * Math.sin(startRad);
  
  const largeArcFlag = Math.abs(endAngle - startAngle) > 180 ? 1 : 0;
  
  return `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} L ${x3} ${y3} A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${x4} ${y4} Z`;
};

export const rotatePoint = (
  x: number,
  y: number,
  angle: number,
  center: { x: number; y: number }
): { x: number; y: number } => {
  const rad = (angle * Math.PI) / 180;
  const cos = Math.cos(rad);
  const sin = Math.sin(rad);
  
  const nx = (x - center.x) * cos - (y - center.y) * sin + center.x;
  const ny = (x - center.x) * sin + (y - center.y) * cos + center.y;
  
  return { x: nx, y: ny };
};

export const generateSlices = (
  count: number,
  colors: string[],
  values: (string | number)[] = []
): WheelSlice[] => {
  const slices: WheelSlice[] = [];
  
  for (let i = 0; i < count; i++) {
    const value = values[i] ?? i + 1;
    slices.push({
      id: `slice-${i}`,
      value,
      color: colors[i % colors.length],
    });
  }
  
  return slices;
};
