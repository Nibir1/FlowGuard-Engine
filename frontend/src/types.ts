export interface TelemetryReading {
  elevator_id: string;
  timestamp?: string;
  velocity_m_s: number;
  door_cycles_count: number;
  vibration_level_hz: number;
  error_codes: string[];
}

export interface MaintenanceStep {
  step_order: number;
  instruction: string;
  tool_required?: string;
}

export interface DiagnosticResult {
  fault_summary: string;
  root_cause_hypothesis: string;
  severity_score: number;
  cited_manual_references: string[];
  recommended_actions: MaintenanceStep[];
  safety_warnings: string[];
}