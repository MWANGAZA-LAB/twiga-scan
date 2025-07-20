import React, { useState, useEffect } from 'react';
import { X, ChevronLeft, ChevronRight, Play, Camera, Upload, CheckCircle } from 'lucide-react';

interface TutorialStep {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  action?: string;
  highlight?: string;
}

interface TutorialProps {
  isOpen: boolean;
  onClose: () => void;
}

const Tutorial: React.FC<TutorialProps> = ({ isOpen, onClose }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set());

  const tutorialSteps: TutorialStep[] = [
    {
      id: 'welcome',
      title: 'Welcome to Twiga Scan!',
      description: 'Your Bitcoin and Lightning Network QR & URL authentication platform. Let\'s take a quick tour to get you started.',
      icon: <CheckCircle className="w-8 h-8 text-green-500" />,
    },
    {
      id: 'scan-methods',
      title: 'Multiple Scanning Methods',
      description: 'You can scan QR codes using your camera, upload images, or manually enter URLs and payment addresses.',
      icon: <Camera className="w-8 h-8 text-blue-500" />,
      action: 'Try clicking the camera button to start scanning',
      highlight: 'camera-button',
    },
    {
      id: 'supported-formats',
      title: 'Supported Formats',
      description: 'We support Bitcoin URIs (BIP21), Lightning invoices (BOLT11), LNURL, and Lightning Addresses.',
      icon: <Upload className="w-8 h-8 text-purple-500" />,
      action: 'Try scanning this: bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?amount=0.001',
    },
    {
      id: 'verification',
      title: 'Real-time Verification',
      description: 'Every scan is verified in real-time for domain validity, cryptographic signatures, and trusted providers.',
      icon: <CheckCircle className="w-8 h-8 text-green-500" />,
    },
    {
      id: 'history',
      title: 'Scan History',
      description: 'All your scans are logged with detailed information. You can view, search, and manage your scan history.',
      icon: <CheckCircle className="w-8 h-8 text-blue-500" />,
    },
    {
      id: 'api-access',
      title: 'API Access',
      description: 'Developers can integrate Twiga Scan into their applications using our comprehensive REST API.',
      icon: <Play className="w-8 h-8 text-orange-500" />,
    },
  ];

  const handleNext = () => {
    if (currentStep < tutorialSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      completeTutorial();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const completeTutorial = () => {
    setCompletedSteps(new Set(tutorialSteps.map(step => step.id)));
    localStorage.setItem('tutorial-completed', 'true');
    onClose();
  };

  const skipTutorial = () => {
    localStorage.setItem('tutorial-completed', 'true');
    onClose();
  };

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const currentStepData = tutorialSteps[currentStep];
  const progress = ((currentStep + 1) / tutorialSteps.length) * 100;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full p-6 relative">
        {/* Close button */}
        <button
          onClick={skipTutorial}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Progress bar */}
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-6">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Step content */}
        <div className="text-center mb-6">
          <div className="flex justify-center mb-4">
            {currentStepData.icon}
          </div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            {currentStepData.title}
          </h3>
          <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">
            {currentStepData.description}
          </p>
          {currentStepData.action && (
            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <p className="text-blue-700 dark:text-blue-300 text-sm font-medium">
                💡 {currentStepData.action}
              </p>
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className="flex items-center px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-4 h-4 mr-1" />
            Previous
          </button>

          <span className="text-sm text-gray-500 dark:text-gray-400">
            {currentStep + 1} of {tutorialSteps.length}
          </span>

          <button
            onClick={handleNext}
            className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            {currentStep === tutorialSteps.length - 1 ? (
              <>
                Get Started
                <CheckCircle className="w-4 h-4 ml-1" />
              </>
            ) : (
              <>
                Next
                <ChevronRight className="w-4 h-4 ml-1" />
              </>
            )}
          </button>
        </div>

        {/* Skip tutorial */}
        <div className="text-center mt-4">
          <button
            onClick={skipTutorial}
            className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
          >
            Skip tutorial
          </button>
        </div>
      </div>
    </div>
  );
};

export default Tutorial; 