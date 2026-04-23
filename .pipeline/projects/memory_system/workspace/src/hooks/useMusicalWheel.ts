import { useState, useCallback, useRef, useEffect } from 'react';
import { WheelState, WheelSlice } from '../types/wheel';

interface UseMusicalWheelProps {
  slices: WheelSlice[];
  onSliceSelect?: (slice: WheelSlice) => void;
  radius?: number;
}

export const useMusicalWheel = ({
  slices,
  onSliceSelect,
  radius = 200,
}: UseMusicalWheelProps): [WheelState, (element: HTMLElement | null) => void, (e: React.MouseEvent | React.TouchEvent) => void, (e: React.MouseEvent | React.TouchEvent) => void, () => void, (slice: WheelSlice, e: React.MouseEvent) => void] => {
  const [state, setState] = useState<WheelState>({
    rotation: 0,
    isDragging: false,
    selectedSlice: null,
  });

  const lastAngleRef = useRef<number | null>(null);
  const centerRef = useRef<{ x: number; y: number } | null>(null);

  const getAngleFromEvent = useCallback((e: React.MouseEvent | React.TouchEvent): number | null => {
    const center = centerRef.current;
    if (!center) return null;

    let clientX: number, clientY: number;
    if ('touches' in e) {
      clientX = e.touches[0].clientX;
      clientY = e.touches[0].clientY;
    } else {
      clientX = (e as React.MouseEvent).clientX;
      clientY = (e as React.MouseEvent).clientY;
    }

    const dx = clientX - center.x;
    const dy = clientY - center.y;
    return Math.atan2(dy, dx) * (180 / Math.PI);
  }, []);

  const handleStart = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    lastAngleRef.current = getAngleFromEvent(e);
    setState(prev => ({ ...prev, isDragging: true, selectedSlice: null }));
  }, [getAngleFromEvent]);

  const handleMove = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    if (!state.isDragging) return;

    const currentAngle = getAngleFromEvent(e);
    if (currentAngle === null || lastAngleRef.current === null) return;

    const delta = currentAngle - lastAngleRef.current;
    lastAngleRef.current = currentAngle;

    setState(prev => ({
      ...prev,
      rotation: (prev.rotation + delta) % 360,
    }));
  }, [state.isDragging, getAngleFromEvent]);

  const handleEnd = useCallback(() => {
    if (state.isDragging && lastAngleRef.current !== null) {
      const center = centerRef.current;
      if (center) {
        const dx = Math.cos(lastAngleRef.current * Math.PI / 180) * radius;
        const dy = Math.sin(lastAngleRef.current * Math.PI / 180) * radius;
        const normalizedAngle = ((lastAngleRef.current + 180) % 360);
        const sliceIndex = Math.floor((normalizedAngle / 360) * slices.length);
        const slice = slices[sliceIndex % slices.length];

        if (slice) {
          setState(prev => ({ ...prev, selectedSlice: slice }));
          onSliceSelect?.(slice);
        }
      }
    }
    lastAngleRef.current = null;
    setState(prev => ({ ...prev, isDragging: false }));
  }, [state.isDragging, lastAngleRef, radius, slices, onSliceSelect]);

  const handleWheelClick = useCallback((slice: WheelSlice, e: React.MouseEvent) => {
    e.stopPropagation();
    setState(prev => ({ ...prev, selectedSlice: slice }));
    onSliceSelect?.(slice);
  }, [onSliceSelect]);

  const setCenter = useCallback((element: HTMLElement | null) => {
    if (element) {
      const rect = element.getBoundingClientRect();
      centerRef.current = {
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2,
      };
    }
  }, []);

  useEffect(() => {
    return () => {
      lastAngleRef.current = null;
    };
  }, []);

  return [state, setCenter, handleStart, handleMove, handleEnd, handleWheelClick];
};
