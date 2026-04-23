import React, { useRef, useCallback, useState } from 'react';
import { WheelSlice, WheelState } from '../../types/wheel';
import { useMusicalWheel } from '../../hooks/useMusicalWheel';
import { WHEEL_RADIUS, WHEEL_COLORS } from '../../config/constants';
import './MusicalWheel.css';

interface MusicalWheelProps {
  slices: WheelSlice[];
  onSliceSelect?: (slice: WheelSlice) => void;
  title?: string;
  showControls?: boolean;
}

const MusicalWheel: React.FC<MusicalWheelProps> = ({
  slices,
  onSliceSelect,
  title = 'Musical Wheel',
  showControls = true,
}) => {
  const wheelRef = useRef<HTMLDivElement>(null);
  const [localRotation, setLocalRotation] = useState(0);
  
  const [state, setCenter, handleStart, handleMove, handleEnd, handleWheelClick] = useMusicalWheel({
    slices,
    onSliceSelect,
    radius: WHEEL_RADIUS,
  });

  const handleReset = useCallback(() => {
    setLocalRotation(0);
  }, [setLocalRotation]);

  const handleRotationChange = (newRotation: number) => {
    setLocalRotation(newRotation);
  };

  return (
    <div className="musical-wheel-container">
      {title && <h2 className="wheel-title">{title}</h2>}
      <div
        ref={wheelRef}
        className="wheel-wrapper"
        onMouseDown={(e) => {
          setCenter(e.currentTarget);
          handleStart(e);
        }}
        onTouchStart={(e) => {
          setCenter(e.currentTarget);
          handleStart(e);
        }}
        onMouseMove={(e) => {
          if (state.isDragging) handleMove(e);
        }}
        onTouchMove={(e) => {
          if (state.isDragging) handleMove(e);
        }}
        onMouseUp={() => {
          if (state.isDragging) handleEnd();
        }}
        onTouchEnd={() => {
          if (state.isDragging) handleEnd();
        }}
      >
        <svg
          width={WHEEL_RADIUS * 2 + 40}
          height={WHEEL_RADIUS * 2 + 40}
          viewBox={`-${WHEEL_RADIUS + 20} -${WHEEL_RADIUS + 20} ${WHEEL_RADIUS * 2 + 40} ${WHEEL_RADIUS * 2 + 40}`}
          className="wheel-svg"
        >
          <circle
            cx="0"
            cy="0"
            r={WHEEL_RADIUS + 10}
            fill="#f0f0f0"
            stroke="#ddd"
            strokeWidth="2"
          />
          {slices.map((slice, index) => {
            const sliceAngle = (index * (360 / slices.length)) - (360 / slices.length) / 2;
            const labelAngle = sliceAngle + 22.5;
            const labelRadius = WHEEL_RADIUS * 0.6;
            const labelX = labelRadius * Math.cos((labelAngle * Math.PI) / 180);
            const labelY = labelRadius * Math.sin((labelAngle * Math.PI) / 180);

            return (
              <g key={slice.id}>
                <path
                  d={`M ${WHEEL_RADIUS * Math.cos((sliceAngle * Math.PI) / 180)} ${WHEEL_RADIUS * Math.sin((sliceAngle * Math.PI) / 180)} A ${WHEEL_RADIUS} ${WHEEL_RADIUS} 0 ${slices.length > 2 ? 1 : 0} 1 ${WHEEL_RADIUS * Math.cos(((sliceAngle + 360 / slices.length) * Math.PI) / 180)} ${WHEEL_RADIUS * Math.sin(((sliceAngle + 360 / slices.length) * Math.PI) / 180)} L ${WHEEL_RADIUS * 0.3 * Math.cos(((sliceAngle + 360 / slices.length) * Math.PI) / 180)} ${WHEEL_RADIUS * 0.3 * Math.sin(((sliceAngle + 360 / slices.length) * Math.PI) / 180)} A ${WHEEL_RADIUS * 0.3} ${WHEEL_RADIUS * 0.3} 0 ${slices.length > 2 ? 1 : 0} 0 ${WHEEL_RADIUS * 0.3 * Math.cos((sliceAngle * Math.PI) / 180)} ${WHEEL_RADIUS * 0.3 * Math.sin((sliceAngle * Math.PI) / 180)} Z`}
                  fill={slice.color}
                  stroke="white"
                  strokeWidth="2"
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
          })}
          <circle
            cx="0"
            cy="0"
            r={WHEEL_RADIUS * 0.3}
            fill="white"
            stroke="#4ECDC4"
            strokeWidth="3"
          />
        </svg>
      </div>
      {showControls && (
        <div className="wheel-controls">
          <button onClick={handleReset} className="btn btn-secondary">
            Reset Rotation
          </button>
          {state.selectedSlice && (
            <div className="selection-info">
              <span>Selected: </span>
              <strong>{state.selectedSlice.value}</strong>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MusicalWheel;
