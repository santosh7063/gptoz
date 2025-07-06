import React, { useCallback } from 'react';
import { Upload, Music } from 'lucide-react';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect }) => {
  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    const audioFile = files.find(file => file.type.startsWith('audio/'));
    if (audioFile) {
      onFileSelect(audioFile);
    }
  }, [onFileSelect]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  }, [onFileSelect]);

  return (
    <div
      className="border-2 border-dashed border-gray-600 rounded-xl p-12 text-center hover:border-primary-500 transition-colors cursor-pointer glass-effect"
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      onClick={() => document.getElementById('file-input')?.click()}
    >
      <div className="space-y-4">
        <div className="flex justify-center">
          <div className="p-4 bg-primary-600/20 rounded-full">
            <Music className="w-12 h-12 text-primary-400" />
          </div>
        </div>
        
        <div>
          <h3 className="text-xl font-semibold mb-2">Upload Audio File</h3>
          <p className="text-gray-400 mb-4">
            Drag and drop your audio file here, or click to browse
          </p>
          <p className="text-sm text-gray-500">
            Supports MP3, WAV, OGG, and other audio formats
          </p>
        </div>
        
        <div className="flex items-center justify-center gap-2 text-primary-400">
          <Upload className="w-5 h-5" />
          <span className="font-medium">Choose File</span>
        </div>
      </div>
      
      <input
        id="file-input"
        type="file"
        accept="audio/*"
        onChange={handleFileInput}
        className="hidden"
      />
    </div>
  );
};

export default FileUpload;