export interface WheelSlice {
  id: string;
  value: string | number;
  color: string;
  label?: string;
}

export interface WheelState {
  rotation: number;
  isDragging: boolean;
  selectedSlice: WheelSlice | null;
}

export interface WheelProps {
  slices: WheelSlice[];
  onSliceSelect?: (slice: WheelSlice) => void;
  radius?: number;
  rotation?: number;
  onRotationChange?: (rotation: number) => void;
}
