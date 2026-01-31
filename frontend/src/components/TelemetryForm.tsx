import React, { useState, useEffect } from 'react';
import { TelemetryReading } from '../types';
import { Activity, Zap } from 'lucide-react';

interface Props {
  onSubmit: (data: TelemetryReading) => void;
  isLoading: boolean;
  // NEW: Optional prop to accept data from the Simulator Hook
  values?: TelemetryReading; 
}

export const TelemetryForm: React.FC<Props> = ({ onSubmit, isLoading, values }) => {
  // Preset defaults for quick demo
  const [formData, setFormData] = useState<TelemetryReading>({
    elevator_id: 'KONE-FIN-01',
    velocity_m_s: 0.0,
    door_cycles_count: 15420,
    vibration_level_hz: 0.2,
    error_codes: ['E-302']
  });

  // NEW: Sync internal state when the simulator pushes new data (Live Mode)
  useEffect(() => {
    if (values) {
      setFormData(values);
    }
  }, [values]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'elevator_id' ? value : 
              name === 'error_codes' ? value.split(',').map(s => s.trim()) : Number(value)
    }));
  };

  return (
    <div className="card h-full transition-all duration-300">
      <div className="flex items-center gap-2 mb-6 text-brand-900">
        <Activity className="w-6 h-6" />
        <h2 className="text-xl font-bold">Live Telemetry Stream</h2>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-600 mb-1">Asset ID</label>
          <input name="elevator_id" value={formData.elevator_id} onChange={handleChange} 
                 className="w-full p-2 border rounded font-mono text-sm bg-slate-50" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">Velocity (m/s)</label>
            <input name="velocity_m_s" type="number" step="0.1" value={formData.velocity_m_s.toFixed(2)} onChange={handleChange} 
                   className="w-full p-2 border rounded transition-colors duration-300 ease-in-out" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">Vibration (Hz)</label>
            <input name="vibration_level_hz" type="number" step="0.1" value={formData.vibration_level_hz.toFixed(2)} onChange={handleChange} 
                   className="w-full p-2 border rounded transition-colors duration-300 ease-in-out" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-600 mb-1">Door Cycles</label>
          <input name="door_cycles_count" type="number" value={formData.door_cycles_count} onChange={handleChange} 
                 className="w-full p-2 border rounded" />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-600 mb-1">Error Codes (comma sep)</label>
          <input name="error_codes" value={formData.error_codes.join(', ')} onChange={handleChange} 
                 className="w-full p-2 border rounded bg-red-50 border-red-200 text-red-700 font-mono" />
        </div>

        <button 
          onClick={() => onSubmit(formData)}
          disabled={isLoading}
          className="w-full mt-4 bg-brand-600 hover:bg-brand-700 text-white py-3 rounded-lg font-semibold flex justify-center items-center gap-2 transition-colors"
        >
          {isLoading ? (
            <span className="animate-pulse">Processing...</span>
          ) : (
            <>
              <Zap className="w-5 h-5" />
              Run Agent Diagnostic
            </>
          )}
        </button>
      </div>
    </div>
  );
};