import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, Upload, Volume2, Settings, Zap } from 'lucide-react';
import AudioVisualizer from './components/AudioVisualizer';
import VisualizerControls from './components/VisualizerControls';
import FileUpload from './components/FileUpload';
import { VisualizationType } from './types/visualizer';

function App() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [audioUrl, setAudioUrl] = useState<string>('');
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [visualizerType, setVisualizerType] = useState<VisualizationType>('spectrum');
  const [sensitivity, setSensitivity] = useState(1);
  const [showControls, setShowControls] = useState(true);
  
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    if (audioFile) {
      const url = URL.createObjectURL(audioFile);
      setAudioUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [audioFile]);

  const togglePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleVolumeChange = (newVolume: number) => {
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      {/* Header */}
      <header className="p-6 border-b border-white/10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-primary-500 to-accent-500 rounded-lg">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold gradient-text">Vizzy</h1>
            <span className="text-gray-400 text-sm">Music Visualizer</span>
          </div>
          
          <button
            onClick={() => setShowControls(!showControls)}
            className="p-2 glass-effect rounded-lg hover:bg-white/20 transition-colors"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* File Upload */}
        {!audioFile && (
          <div className="text-center py-12">
            <FileUpload onFileSelect={setAudioFile} />
          </div>
        )}

        {/* Main Visualizer */}
        {audioFile && (
          <div className="space-y-6">
            {/* Audio Controls */}
            <div className="audio-controls">
              <button
                onClick={togglePlayPause}
                className="p-3 bg-primary-600 hover:bg-primary-700 rounded-full transition-colors"
                disabled={!audioUrl}
              >
                {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
              </button>
              
              <div className="flex-1 space-y-2">
                <div className="flex items-center justify-between text-sm text-gray-300">
                  <span>{audioFile.name}</span>
                  <span>{formatTime(currentTime)} / {formatTime(duration)}</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-primary-500 to-accent-500 h-2 rounded-full transition-all duration-100"
                    style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
                  />
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <Volume2 className="w-5 h-5 text-gray-400" />
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={volume}
                  onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                  className="w-20"
                />
              </div>
            </div>

            {/* Visualizer Controls */}
            {showControls && (
              <VisualizerControls
                visualizerType={visualizerType}
                onVisualizerTypeChange={setVisualizerType}
                sensitivity={sensitivity}
                onSensitivityChange={setSensitivity}
              />
            )}

            {/* Audio Visualizer */}
            <div className="visualizer-container h-96">
              <AudioVisualizer
                audioElement={audioRef.current}
                isPlaying={isPlaying}
                visualizerType={visualizerType}
                sensitivity={sensitivity}
              />
            </div>

            {/* Hidden Audio Element */}
            <audio
              ref={audioRef}
              src={audioUrl}
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleLoadedMetadata}
              onEnded={() => setIsPlaying(false)}
              volume={volume}
            />
          </div>
        )}

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-6 mt-12">
          <div className="glass-effect p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-3 gradient-text">Real-time Analysis</h3>
            <p className="text-gray-300 text-sm">
              Advanced audio analysis with frequency spectrum visualization and waveform rendering.
            </p>
          </div>
          
          <div className="glass-effect p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-3 gradient-text">Multiple Visualizers</h3>
            <p className="text-gray-300 text-sm">
              Choose from spectrum bars, waveforms, circular patterns, and particle effects.
            </p>
          </div>
          
          <div className="glass-effect p-6 rounded-xl">
            <h3 className="text-lg font-semibold mb-3 gradient-text">Customizable</h3>
            <p className="text-gray-300 text-sm">
              Adjust sensitivity, colors, and visualization parameters to match your style.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;