import React from 'react';
import { WheelSlice, WheelProps } from './types';
import { calculateSliceCoordinates, createArcPath, WHEEL_RADIUS, WHEEL_COLORS } from '../../utils/wheelUtils';

const WheelSliceComponent: React.FC<{
  slice: WheelSlice;
  index: number;
  totalSlices: number;
  rotation: number;
  isSelected: boolean;
  onClick: (slice: WheelSlice, e: React.MouseEvent) => void;
}> = ({ slice, index, totalSlices, rotation, isSelected, onClick }) => {
  const { x, y, angle } = calculateSliceCoordinates(index, totalSlices, WHEEL_RADIUS, rotation);
  
  const labelAngle = angle + 22.5;
  const labelRadius = WHEEL_RADIUS * 0.6;
  const labelX = labelRadius * Math.cos((labelAngle * Math.PI) / 180);
  const labelY = labelRadius * Math.sin((labelAngle * Math.PI) / 180);

  return (
    <g
      onClick={(e) => onClick(slice, e)}
      style={{
        cursor: 'pointer',
        transform: isSelected ? 'scale(1.05)' : 'scale(1)',
        transformOrigin: 'center',
        transition: 'transform 0.2s ease',
      }}
    >
      <path
        d={createArcPath(WHEEL_RADIUS, angle, angle + 360 / totalSlices)}
        fill={slice.color}
        stroke="white"
        strokeWidth="2"
        style={{
          opacity: isSelected ? 1 : 0.9,
        }}
      />
      <text
        x={labelX}
        y={labelY}
        textAnchor="middle"
        dominantBaseline="middle"
        fill="white"
        fontSize="14"
        fontWeight="bold"
        style={{
          pointerEvents: 'none',
          textShadow: '1px 1px 2px rgba(0,0,0,0.3)',
        }}
      >
        {slice.value}
      </text>
    </g>
  );
};

const MusicalWheel: React.FC<WheelProps> = ({
  slices,
  onSliceSelect,
  radius = WHEEL_RADIUS,
  rotation = 0,
  onRotationChange,
}) => {
  const [localRotation, setLocalRotation] = React.useState(rotation);

  const handleRotationChange = (newRotation: number) => {
    setLocalRotation(newRotation);
    onRotationChange?.(newRotation);
  };

  return (
    <svg
      width={radius * 2 + 40}
      height={radius * 2 + 40}
      viewBox={`-${radius + 20} -${radius + 20} ${radius * 2 + 40} ${radius * 2 + 40}`}
      style={{
        display: 'block',
        margin: '0 auto',
      }}
    >
      <circle
        cx="0"
        cy="0"
        r={radius + 10}
        fill="#f0f0f0"
        stroke="#ddd"
        strokeWidth="2"
      />
      {slices.map((slice, index) => (
        <WheelSliceComponent
          key={slice.id}
          slice={slice}
          index={index}
          totalSlices={slices.length}
          rotation={localRotation}
          isSelected={false}
          onClick={onSliceSelect ? onSliceSelect : () => {}}
        />
      ))}
      <circle
        cx="0"
        cy="0"
        r={radius * 0.3}
        fill="white"
        stroke={WHEEL_COLORS[0]}
        strokeWidth="3"
      />
    </svg>
  );
};

export default MusicalWheel;
