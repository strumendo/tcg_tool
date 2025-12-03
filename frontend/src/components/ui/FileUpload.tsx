'use client';

import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { CloudArrowUpIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface FileUploadProps {
  onUpload: (files: File[]) => void;
  accept?: Record<string, string[]>;
  maxSize?: number;
  multiple?: boolean;
  className?: string;
  label?: string;
  hint?: string;
}

export function FileUpload({
  onUpload,
  accept,
  maxSize = 50 * 1024 * 1024, // 50MB default
  multiple = false,
  className,
  label = 'Upload a file',
  hint = 'or drag and drop',
}: FileUploadProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      onUpload(acceptedFiles);
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple,
  });

  return (
    <div
      {...getRootProps()}
      className={clsx(
        'relative flex flex-col items-center justify-center w-full h-48 border-2 border-dashed rounded-xl cursor-pointer transition-colors',
        isDragActive && !isDragReject && 'border-pokemon-blue bg-blue-50',
        isDragReject && 'border-pokemon-red bg-red-50',
        !isDragActive && 'border-gray-300 hover:border-gray-400 bg-gray-50',
        className
      )}
    >
      <input {...getInputProps()} />
      <CloudArrowUpIcon
        className={clsx(
          'w-12 h-12 mb-4',
          isDragActive && !isDragReject && 'text-pokemon-blue',
          isDragReject && 'text-pokemon-red',
          !isDragActive && 'text-gray-400'
        )}
      />
      <p className="text-sm font-medium text-gray-700">{label}</p>
      <p className="text-xs text-gray-500 mt-1">{hint}</p>
      {isDragReject && (
        <p className="text-xs text-pokemon-red mt-2">File type not accepted</p>
      )}
    </div>
  );
}
