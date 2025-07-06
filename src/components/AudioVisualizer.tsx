import React, { useRef, useEffect, useState } from 'react';
import { VisualizationType } from '../types/visualizer';

interface AudioVisualizerProps {
  audioElement: HTMLAudioElement | null;
  isPlaying: boolean;
  visualizerType: VisualizationType;
  sensitivity: number;
}

const AudioVisualizer: React.FC<AudioVisualizerProps> = ({
  audioElement,
  isPlaying,
  visualizerType,
  sensitivity,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const analyserRef = useRef<AnalyserNode | null>(null);
  const dataArrayRef = useRef<Uint8Array | null>(null);
  const [audioContext, setAudioContext] = useState<AudioContext | null>(null);

  useEffect(() => {
    if (audioElement && !audioContext) {
      const ctx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const analyser = ctx.createAnalyser();
      const source = ctx.createMediaElementSource(audioElement);
      
      analyser.fftSize = 256;
      analyser.smoothingTimeConstant = 0.8;
      
      source.connect(analyser);
      analyser.connect(ctx.destination);
      
      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      
      setAudioContext(ctx);
      analyserRef.current = analyser;
      dataArrayRef.current = dataArray;
    }
  }, [audioElement, audioContext]);

  useEffect(() => {
    if (isPlaying && audioContext?.state === 'suspended') {
      audioContext.resume();
    }
  }, [isPlaying, audioContext]);

  const drawSpectrum = (ctx: CanvasRenderingContext2D, dataArray: Uint8Array, width: number, height: number) => {
    const barWidth = width / dataArray.length;
    
    for (let i = 0; i < dataArray.length; i++) {
      const barHeight = (dataArray[i] / 255) * height * sensitivity;
      const x = i * barWidth;
      const y = height - barHeight;
      
      const hue = (i / dataArray.length) * 360;
      const gradient = ctx.createLinearGradient(0, height, 0, y);
      gradient.addColorStop(0, `hsl(${hue}, 70%, 50%)`);
      gradient.addColorStop(1, `hsl(${hue}, 70%, 80%)`);
      
      ctx.fillStyle = gradient;
      ctx.fillRect(x, y, barWidth - 1, barHeight);
    }
  };

  const drawWaveform = (ctx: CanvasRenderingContext2D, dataArray: Uint8Array, width: number, height: number) => {
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    const sliceWidth = width / dataArray.length;
    let x = 0;
    
    for (let i = 0; i < dataArray.length; i++) {
      const v = (dataArray[i] / 128.0) * sensitivity;
      const y = (v * height) / 2;
      
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
      
      x += sliceWidth;
    }
    
    ctx.stroke();
  };

  const drawCircular = (ctx: CanvasRenderingContext2D, dataArray: Uint8Array, width: number, height: number) => {
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 4;
    
    for (let i = 0; i < dataArray.length; i++) {
      const angle = (i / dataArray.length) * Math.PI * 2;
      const amplitude = (dataArray[i] / 255) * radius * sensitivity;
      
      const x1 = centerX + Math.cos(angle) * radius;
      const y1 = centerY + Math.sin(angle) * radius;
      const x2 = centerX + Math.cos(angle) * (radius + amplitude);
      const y2 = centerY + Math.sin(angle) * (radius + amplitude);
      
      const hue = (i / dataArray.length) * 360;
      ctx.strokeStyle = `hsl(${hue}, 70%, 60%)`;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    }
  };

  const drawParticles = (ctx: CanvasRenderingContext2D, dataArray: Uint8Array, width: number, height: number) => {
    for (let i = 0; i < dataArray.length; i++) {
      const amplitude = (dataArray[i] / 255) * sensitivity;
      if (amplitude > 0.1) {
        const x = (i / dataArray.length) * width;
        const y = height / 2 + (Math.random() - 0.5) * amplitude * height;
        const size = amplitude * 10;
        
        const hue = (i / dataArray.length) * 360;
        ctx.fillStyle = `hsl(${hue}, 70%, 60%)`;
        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  };

  const drawBars = (ctx: CanvasRenderingContext2D, dataArray: Uint8Array, width: number, height: number) => {
    const barCount = 32;
    const barWidth = width / barCount;
    const binSize = Math.floor(dataArray.length / barCount);
    
    for (let i = 0; i < barCount; i++) {
      let sum = 0;
      for (let j = 0; j < binSize; j++) {
        sum += dataArray[i * binSize + j];
      }
      const average = sum / binSize;
      const barHeight = (average / 255) * height * sensitivity;
      
      const x = i * barWidth;
      const y = height - barHeight;
      
      const hue = (i / barCount) * 360;
      const gradient = ctx.createLinearGradient(0, height, 0, y);
      gradient.addColorStop(0, `hsl(${hue}, 70%, 40%)`);
      gradient.addColorStop(1, `hsl(${hue}, 70%, 70%)`);
      
      ctx.fillStyle = gradient;
      ctx.fillRect(x + 2, y, barWidth - 4, barHeight);
    }
  };

  const drawOscilloscope = (ctx: CanvasRenderingContext2D, dataArray: Uint8Array, width: number, height: number) => {
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 3;
    ctx.beginPath();
    
    const sliceWidth = width / dataArray.length;
    let x = 0;
    
    for (let i = 0; i < dataArray.length; i++) {
      const v = ((dataArray[i] - 128) / 128.0) * sensitivity;
      const y = height / 2 + (v * height) / 4;
      
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
      
      x += sliceWidth;
    }
    
    ctx.stroke();
    
    // Add grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    for (let i = 0; i < 5; i++) {
      const y = (i / 4) * height;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
  };

  const draw = () => {
    const canvas = canvasRef.current;
    const analyser = analyserRef.current;
    const dataArray = dataArrayRef.current;
    
    if (!canvas || !analyser || !dataArray) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    analyser.getByteFrequencyData(dataArray);
    
    // Clear canvas with fade effect
    ctx.fillStyle = 'rgba(15, 23, 42, 0.1)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    switch (visualizerType) {
      case 'spectrum':
        drawSpectrum(ctx, dataArray, canvas.width, canvas.height);
        break;
      case 'waveform':
        analyser.getByteTimeDomainData(dataArray);
        drawWaveform(ctx, dataArray, canvas.width, canvas.height);
        break;
      case 'circular':
        drawCircular(ctx, dataArray, canvas.width, canvas.height);
        break;
      case 'particles':
        drawParticles(ctx, dataArray, canvas.width, canvas.height);
        break;
      case 'bars':
        drawBars(ctx, dataArray, canvas.width, canvas.height);
        break;
      case 'oscilloscope':
        analyser.getByteTimeDomainData(dataArray);
        drawOscilloscope(ctx, dataArray, canvas.width, canvas.height);
        break;
    }
    
    if (isPlaying) {
      animationRef.current = requestAnimationFrame(draw);
    }
  };

  useEffect(() => {
    if (isPlaying) {
      draw();
    } else if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying, visualizerType, sensitivity]);

  return (
    <canvas
      ref={canvasRef}
      width={800}
      height={400}
      className="w-full h-full"
      style={{ background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.7) 100%)' }}
    />
  );
};

export default AudioVisualizer;