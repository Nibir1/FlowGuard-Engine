import React, { useState } from 'react';
import axios from 'axios';
import { Database, UploadCloud, FileText, Check } from 'lucide-react';

export const AdminPanel: React.FC = () => {
  const [ingesting, setIngesting] = useState(false);
  const [status, setStatus] = useState<string>("");

  const handleSeed = async () => {
    setIngesting(true);
    setStatus("Connecting to Vector Service...");
    try {
      await axios.post('http://localhost:8000/api/v1/admin/seed');
      setStatus("Success: Technical Manuals Vectorised & Indexed.");
    } catch (e) {
      setStatus("Error: Pipeline failed.");
    } finally {
      setIngesting(false);
    }
  };

  return (
    <div className="card bg-slate-800 text-slate-100 border-slate-700">
      <div className="flex items-center gap-2 mb-4 text-brand-500">
        <Database className="w-5 h-5" />
        <h3 className="font-bold">Knowledge Base (RAG) Ops</h3>
      </div>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between p-3 bg-slate-700/50 rounded border border-slate-600">
          <div className="flex items-center gap-3">
            <FileText className="w-4 h-4 text-slate-400" />
            <span className="text-sm">KONE_Door_Systems_2024.pdf</span>
          </div>
          <span className="text-xs bg-green-900/50 text-green-400 px-2 py-1 rounded">Indexed</span>
        </div>

        <button 
          onClick={handleSeed}
          disabled={ingesting}
          className="w-full py-2 bg-brand-600 hover:bg-brand-500 rounded text-sm font-semibold flex items-center justify-center gap-2 transition-all"
        >
          {ingesting ? (
            <span className="animate-pulse">Ingesting Vectors...</span>
          ) : (
            <>
              <UploadCloud className="w-4 h-4" />
              Run Ingestion Pipeline
            </>
          )}
        </button>
        
        {status && (
          <p className="text-xs text-center text-slate-400 animate-fade-in">
            {status}
          </p>
        )}
      </div>
    </div>
  );
};