// components/AddToolModal.tsx
import React, { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { PythonEditor } from './PythonEditor';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { X } from "lucide-react";

interface AddToolModalProps {
  isOpen: boolean;
  onClose: () => void;
  onToolAdded?: () => void;
  chatId?: string | null;
}

export const AddToolModal: React.FC<AddToolModalProps> = ({
  isOpen,
  onClose,
  onToolAdded,
  chatId,
}) => {
  const [name, setName] = useState('');
  const [showCodePrompt, setShowCodePrompt] = useState(false);
  const [showCode, setShowCode] = useState(false);
  const [pythonCode, setPythonCode] = useState('');
  const [showDescriptionPrompt, setShowDescriptionPrompt] = useState(false);
  const [showDescription, setShowDescription] = useState(false);
  const [description, setDescription] = useState('');
  const [currentStep, setCurrentStep] = useState<'name' | 'codePrompt' | 'code' | 'descriptionPrompt' | 'description'>('name');
  const [isAddingTool, setIsAddingTool] = useState(false);

  const resetStates = () => {
    setName('');
    setShowCodePrompt(false);
    setShowCode(false);
    setPythonCode('');
    setShowDescriptionPrompt(false);
    setShowDescription(false);
    setDescription('');
    setCurrentStep('name');
  };

  const handleNameSubmit = () => {
    if (name.trim()) {
      setCurrentStep('codePrompt');
      setShowCodePrompt(true);
    }
  };

  const handleCodePrompt = (wantsCode: boolean) => {
    setShowCodePrompt(false);
    if (wantsCode) {
      setShowCode(true);
      setCurrentStep('code');
    } else {
      setCurrentStep('descriptionPrompt');
      setShowDescriptionPrompt(true);
    }
  };

  const handleCodeSubmit = () => {
    if (pythonCode.trim()) {
      handleFinalSubmit();
    } else {
      setShowCode(false);
      setCurrentStep('descriptionPrompt');
      setShowDescriptionPrompt(true);
    }
  };

  const handleDescriptionPrompt = (wantsDescription: boolean) => {
    setShowDescriptionPrompt(false);
    if (wantsDescription) {
      setShowDescription(true);
      setCurrentStep('description');
    } else if (!pythonCode.trim()) {
      // If no code and no description wanted, show error or reset
      alert('Please provide either Python code or a description');
      resetStates();
      onClose();
    } else {
      handleFinalSubmit();
    }
  };

  const isFormValid = () => {
    return name.trim() && (pythonCode.trim() || description.trim());
  };

  const handleFinalSubmit = async () => {
    if (!isFormValid()) return;

    try {
      const toolData = {
        name: name.trim(),
        description: description.trim() || null,
        python_code: pythonCode.trim() || null
      };
      
      if (chatId) {
        const response = await fetch(`http://localhost:8000/chats/${chatId}/tools`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(toolData),
        });

        if (!response.ok) {
          throw new Error('Failed to add tool');
        }

        resetStates();
        await onToolAdded?.();
        onClose();
      }
    } catch (error) {
      console.error('Error adding tool:', error);
    }
  };

  useEffect(() => {
    if (isOpen) {
      setCurrentStep('name');
      setShowCode(false);
      setShowDescriptionPrompt(false);
      setShowDescription(false);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Add Custom Tool</h2>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="space-y-6">
          {currentStep === 'name' && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                Tool Name
              </label>
              <div className="flex gap-2">
                <Input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Enter tool name..."
                  className="flex-1"
                />
                <Button onClick={handleNameSubmit}>Next</Button>
              </div>
            </div>
          )}

          {showCodePrompt && (
            <div className="space-y-2">
              <p className="text-sm text-gray-700">
                Would you like to add Python code?
              </p>
              <div className="flex gap-2">
                <Button onClick={() => handleCodePrompt(true)}>Yes</Button>
                <Button variant="outline" onClick={() => handleCodePrompt(false)}>No</Button>
              </div>
            </div>
          )}

          {showCode && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                Python Code
              </label>
              <div className="space-y-2">
                <PythonEditor
                  code={pythonCode}
                  onChange={setPythonCode}
                  placeholder="# Enter your Python code here..."
                />
                <div className="flex justify-end">
                  <Button onClick={handleCodeSubmit}>
                    {pythonCode.trim() ? 'Submit' : 'Skip'}
                  </Button>
                </div>
              </div>
            </div>
          )}

          {showDescriptionPrompt && (
            <div className="space-y-2">
              <p className="text-sm text-gray-700">
                Would you like to add a description?
                {!pythonCode.trim() && (
                  <span className="text-red-500 ml-1">
                    (Required if no code is provided)
                  </span>
                )}
              </p>
              <div className="flex gap-2">
                <Button onClick={() => handleDescriptionPrompt(true)}>Yes</Button>
                <Button 
                  variant="outline" 
                  onClick={() => handleDescriptionPrompt(false)}
                  disabled={!pythonCode.trim()}
                >
                  No
                </Button>
              </div>
            </div>
          )}

          {showDescription && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                Description
              </label>
              <div className="flex flex-col gap-2">
                <Textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Enter description..."
                  className="resize-none min-h-[100px] p-3"
                />
                <div className="flex justify-end">
                  <Button 
                    onClick={handleFinalSubmit}
                    disabled={!isFormValid()}
                  >
                    Submit
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};