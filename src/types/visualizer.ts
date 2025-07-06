export type VisualizationType = 'spectrum' | 'waveform' | 'circular' | 'particles' | 'bars' | 'oscilloscope';

export interface VisualizerConfig {
  type: VisualizationType;
  sensitivity: number;
  smoothing: number;
  fftSize: number;
  minDecibels: number;
  maxDecibels: number;
}

export interface AudioData {
  frequencyData: Uint8Array;
  timeDomainData: Uint8Array;
  volume: number;
  peak: number;
}