import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App';

// Mock child components if needed, or test integration fully.
// For this level, we test the full integration.

describe('FlowGuard Dashboard Integration', () => {
  
  it('renders the KONE branding and main layout', () => {
    render(<App />);
    
    // Check for Branding
    expect(screen.getByText(/FlowGuard/i)).toBeInTheDocument();
    expect(screen.getByText(/Engine/i)).toBeInTheDocument();
    
    // Check for Simulation Toggle
    expect(screen.getByText(/SIMULATION OFF/i)).toBeInTheDocument();
  });

  it('toggles simulation mode correctly', () => {
    render(<App />);
    
    const toggleBtn = screen.getByText(/SIMULATION OFF/i);
    fireEvent.click(toggleBtn);
    
    // Expect text to change to LIVE MQTT STREAM
    expect(screen.getByText(/LIVE MQTT STREAM/i)).toBeInTheDocument();
  });

  it('renders the Telemetry Form with default values', () => {
    render(<App />);
    
    // Check input fields exist
    expect(screen.getByLabelText(/Asset ID/i)).toHaveValue('KONE-FIN-01');
    expect(screen.getByLabelText(/Door Cycles/i)).toBeInTheDocument();
    
    // Check Submit Button
    expect(screen.getByRole('button', { name: /Run Agent Diagnostic/i })).toBeInTheDocument();
  });

  it('renders the Admin Panel', () => {
    render(<App />);
    expect(screen.getByText(/Knowledge Base \(RAG\) Ops/i)).toBeInTheDocument();
  });
});