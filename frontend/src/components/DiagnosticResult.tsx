import React from 'react';
import { DiagnosticResult } from '../types';
import { AlertTriangle, CheckCircle, BookOpen, AlertOctagon } from 'lucide-react';
import clsx from 'clsx';

interface Props {
  result: DiagnosticResult | null;
}

export const DiagnosticResultCard: React.FC<Props> = ({ result }) => {
  if (!result) {
    return (
      <div className="card h-full flex flex-col items-center justify-center text-slate-400 min-h-[400px]">
        <ActivityIcon />
        <p className="mt-4">Waiting for telemetry data...</p>
      </div>
    );
  }

  // Determine color based on severity
  const severityColor = result.severity_score >= 7 ? 'text-red-600' : result.severity_score >= 4 ? 'text-amber-600' : 'text-green-600';
  const badgeColor = result.severity_score >= 7 ? 'bg-red-100 text-red-800' : 'bg-amber-100 text-amber-800';

  return (
    <div className="card border-l-4 border-l-brand-600 animate-fade-in">
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Diagnostic Report</h2>
          <p className="text-slate-500 text-sm mt-1">{result.root_cause_hypothesis}</p>
        </div>
        <div className={clsx("flex flex-col items-end", severityColor)}>
          <span className="text-4xl font-black">{result.severity_score}/10</span>
          <span className="text-xs font-bold uppercase tracking-wider">Severity</span>
        </div>
      </div>

      {/* Summary */}
      <div className="mb-6 bg-slate-50 p-4 rounded border border-slate-100">
        <p className="text-slate-700 leading-relaxed">{result.fault_summary}</p>
      </div>

      {/* Actions */}
      <div className="mb-6">
        <h3 className="font-bold text-slate-900 mb-3 flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-brand-600" />
          Recommended Actions
        </h3>
        <div className="space-y-3">
          {result.recommended_actions.map((action, idx) => (
            <div key={idx} className="flex gap-3 items-start bg-white p-3 rounded border border-slate-200">
              <span className="bg-slate-100 text-slate-600 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0">
                {action.step_order}
              </span>
              <div>
                <p className="text-slate-800 text-sm font-medium">{action.instruction}</p>
                {action.tool_required && (
                  <span className="text-xs text-slate-400 mt-1 block">Tool: {action.tool_required}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Safety & References */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-red-50 p-4 rounded border border-red-100">
          <h4 className="font-bold text-red-800 text-sm mb-2 flex items-center gap-2">
            <AlertOctagon className="w-4 h-4" />
            Safety Protocols
          </h4>
          <ul className="list-disc list-inside text-xs text-red-700 space-y-1">
            {result.safety_warnings.map((w, i) => <li key={i}>{w}</li>)}
          </ul>
        </div>

        <div className="bg-blue-50 p-4 rounded border border-blue-100">
          <h4 className="font-bold text-blue-800 text-sm mb-2 flex items-center gap-2">
            <BookOpen className="w-4 h-4" />
            References
          </h4>
          <div className="flex flex-wrap gap-2">
            {result.cited_manual_references.map((ref, i) => (
              <span key={i} className="px-2 py-1 bg-white rounded text-xs text-blue-600 border border-blue-200 shadow-sm">
                Manual ID: {ref.substring(0, 8)}...
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const ActivityIcon = () => (
  <svg className="w-16 h-16 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
  </svg>
);