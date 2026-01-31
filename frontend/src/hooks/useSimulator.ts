import { useState, useEffect, useCallback } from 'react';
import { TelemetryReading } from '../types';

const INITIAL_STATE: TelemetryReading = {
  elevator_id: 'KONE-FIN-01',
  velocity_m_s: 0.0,
  door_cycles_count: 15420,
  vibration_level_hz: 0.2,
  error_codes: ['E-302']
};

export const useSimulator = () => {
  const [data, setData] = useState<TelemetryReading>(INITIAL_STATE);
  const [isLive, setIsLive] = useState(false);

  // Simulate "Normal" vs "Error" states
  const generatePacket = useCallback(() => {
    const isError = Math.random() > 0.7; // 30% chance of glitch
    
    setData(prev => ({
      ...prev,
      timestamp: new Date().toISOString(),
      // Add realistic "jitter" to sensor values
      velocity_m_s: Math.abs(prev.velocity_m_s + (Math.random() - 0.5) * 0.1), 
      vibration_level_hz: isError ? 4.0 + Math.random() : 0.2 + Math.random() * 0.1,
      door_cycles_count: prev.door_cycles_count + 1,
      error_codes: isError ? ['E-302'] : []
    }));
  }, []);

  useEffect(() => {
    let interval: any;
    if (isLive) {
      interval = setInterval(generatePacket, 2000); // Update every 2s
    }
    return () => clearInterval(interval);
  }, [isLive, generatePacket]);

  return { data, setData, isLive, setIsLive };
};