'use client';

import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import LoadingSpinner from './LoadingSpinner';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faRobot, faSearch, faChartBar, faWandSparkles } from '@fortawesome/free-solid-svg-icons';
import '@/lib/fontawesome';

interface ProgressStep {
  id: string;
  label: string;
  description: string;
  icon: string;
}

interface ProgressIndicatorProps {
  isLoading: boolean;
  className?: string;
}

const PROGRESS_STEPS: ProgressStep[] = [
  {
    id: 'analyzing',
    label: 'AI Analysis',
    description: 'Expert agents analyzing vehicle specifications...',
    icon: 'robot'
  },
  {
    id: 'searching',
    label: 'Market Search',
    description: 'Searching ikman.lk and riyasewana.com...',
    icon: 'search'
  },
  {
    id: 'extracting',
    label: 'Data Extraction',
    description: 'Extracting advertisement details...',
    icon: 'chart-bar'
  },
  {
    id: 'finalizing',
    label: 'Finalizing',
    description: 'Preparing your comparison report...',
    icon: 'sparkles'
  }
];

export default function ProgressIndicator({ isLoading, className }: ProgressIndicatorProps) {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    if (!isLoading) {
      setCurrentStep(0);
      return;
    }

    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % PROGRESS_STEPS.length);
    }, 4000); // Change step every 4 seconds

    return () => clearInterval(interval);
  }, [isLoading]);

  if (!isLoading) return null;

  const currentStepData = PROGRESS_STEPS[currentStep];

  return (
    <div className={cn('bg-white rounded-lg border shadow-sm p-6', className)}>
      <div className="flex items-center justify-center mb-4">
        <LoadingSpinner size="lg" />
      </div>
      
      <div className="text-center mb-6">
        <div className="text-3xl mb-2">
          <FontAwesomeIcon 
            icon={currentStepData.icon === 'robot' ? faRobot : 
                  currentStepData.icon === 'search' ? faSearch : 
                  currentStepData.icon === 'chart-bar' ? faChartBar : faWandSparkles} 
            className="text-indigo-600" 
          />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-1">
          {currentStepData.label}
        </h3>
        <p className="text-sm text-gray-600">
          {currentStepData.description}
        </p>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
        <div 
          className="bg-indigo-600 h-2 rounded-full transition-all duration-1000 ease-out"
          style={{ width: `${((currentStep + 1) / PROGRESS_STEPS.length) * 100}%` }}
        />
      </div>

      {/* Step indicators */}
      <div className="flex justify-between">
        {PROGRESS_STEPS.map((step, index) => (
          <div key={step.id} className="flex flex-col items-center">
            <div
              className={cn(
                'w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium transition-colors',
                index <= currentStep
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-200 text-gray-500'
              )}
            >
              {index + 1}
            </div>
            <span className="text-xs text-gray-500 mt-1 hidden sm:block">
              {step.label}
            </span>
          </div>
        ))}
      </div>

      <div className="text-center mt-4">
        <p className="text-xs text-gray-500">
          This may take 30-60 seconds. Please wait...
        </p>
      </div>
    </div>
  );
}
