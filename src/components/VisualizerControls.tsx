import React from 'react';
import { BarChart3, Activity, Circle, Sparkles, AlignJustify, Radio } from 'lucide-react';
import { VisualizationType } from '../types/visualizer';

interface VisualizerControlsProps {
  visualizerType: VisualizationType;
  onVisualizerTypeChange: (type: VisualizationType) => void;
  sensitivity: number;
  onSensitivityChange: (sensitivity: number) => void;
}

const visualizerOptions = [
  { type: 'spectrum' as VisualizationType, label: 'Spectrum', icon: BarChart3 },
  { type: 'waveform' as VisualizationType, label: 'Waveform', icon: Activity },
  { type: 'circular' as VisualizationType, label: 'Circular', icon: Circle },
  { type: 'particles' as VisualizationType, label: 'Particles', icon: Sparkles },
  { type: 'bars' as VisualizationType, label: 'Bars', icon: AlignJustify },
  { type: 'oscilloscope' as VisualizationType, label: 'Oscilloscope', icon: Radio },
];

const VisualizerControls: React.FC<VisualizerControlsProps> = ({
  visualizerType,
  onVisualizerTypeChange,
  sensitivity,
  onSensitivityChange,
}) => {
  return (
    <div className="glass-effect p-6 rounded-xl space-y-6">
      <h3 className="text-lg font-semibold gradient-text">Visualizer Controls</h3>
      
      {/* Visualizer Type Selection */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-300">Visualization Type</label>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
          {visualizerOptions.map(({ type, label, icon: Icon }) => (
            <button
              key={type}
              onClick={() => onVisualizerTypeChange(type)}
              className={`p-3 rounded-lg border transition-all ${
                visualizerType === type
                  ? 'bg-primary-600 border-primary-500 text-white'
                  : 'bg-gray-800/50 border-gray-600 text-gray-300 hover:bg-gray-700/50'
              }`}
            >
              <Icon className="w-5 h-5 mx-auto mb-1" />
              <div className="text-xs">{label}</div>
            </button>
          ))}
        </div>
      </div>
      
      {/* Sensitivity Control */}
      <div className="space-y-3">
        <label className="text-sm font-medium text-gray-300">
          Sensitivity: {sensitivity.toFixed(1)}x
        </label>
        <input
          type="range"
          min="0.1"
          max="3"
          step="0.1"
          value={sensitivity}
          onChange={(e) => onSensitivityChange(parseFloat(e.target.value))}
          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
        />
        <div className="flex justify-between text-xs text-gray-500">
          <span>Low</span>
          <span>High</span>
        </div>
      </div>
    </div>
  );
};

export default VisualizerControls;