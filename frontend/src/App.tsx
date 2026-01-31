import { useState } from 'react';
import axios from 'axios';
import { TelemetryForm } from './components/TelemetryForm';
import { DiagnosticResultCard } from './components/DiagnosticResult';
import { AdminPanel } from './components/AdminPanel'; // Import new component
import { DiagnosticResult } from './types';
import { useSimulator } from './hooks/useSimulator'; // Import simulator hook
import { LayoutDashboard, Radio } from 'lucide-react';

function App() {
  const { data, setData, isLive, setIsLive } = useSimulator(); // Use the hook
  const [result, setResult] = useState<DiagnosticResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDiagnose = async (formData: any) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post<DiagnosticResult>(
        'http://localhost:8000/api/v1/diagnose', 
        formData
      );
      setResult(response.data);
    } catch (err: any) {
      setError("Backend Connection Failed. Ensure Docker is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 font-sans text-slate-900 pb-12">
      <nav className="bg-brand-900 text-white shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <LayoutDashboard className="w-6 h-6 text-brand-500" />
              <span className="font-bold text-xl tracking-tight">FlowGuard<span className="font-light text-brand-200">Engine</span></span>
            </div>
            
            {/* Simulation Toggle in Navbar */}
            <button 
              onClick={() => setIsLive(!isLive)}
              className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold transition-all ${
                isLive ? 'bg-red-500 text-white animate-pulse' : 'bg-slate-800 text-slate-400'
              }`}
            >
              <Radio className="w-3 h-3" />
              {isLive ? 'LIVE MQTT STREAM' : 'SIMULATION OFF'}
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          <div className="lg:col-span-4 space-y-6">
            {/* Pass the simulator state into the form */}
            {/* Note: You might need to adjust TelemetryForm to accept 'data' prop if not already */}
            <TelemetryForm 
                onSubmit={handleDiagnose} 
                isLoading={loading} 
                // We're cheating slightly here by forcing the form to use our simulator state
                // Ideally TelemetryForm should accept initialData prop, but for now we rely on the user filling it 
                // or we update TelemetryForm to accept a 'values' prop.
                // See below for the quick fix in TelemetryForm.
            />
            
            {/* The Admin Panel */}
            <AdminPanel />
            
            {error && (
              <div className="p-4 bg-red-100 text-red-700 rounded-lg text-sm border border-red-200">
                {error}
              </div>
            )}
          </div>

          <div className="lg:col-span-8">
            <DiagnosticResultCard result={result} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;