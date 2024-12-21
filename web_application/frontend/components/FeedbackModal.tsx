import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { X, Plus, Save } from 'lucide-react';

interface FeedbackModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSaveFeedback: (feedback: FeedbackData) => Promise<void>;
  jargonWords?: Array<{ word: string; meaning: string }>;
}

interface FeedbackItem {
  word: string;
  meaning: string;
  isPreFilled: boolean;
}

interface FeedbackData {
  feedback: string;
  clarification: Array<{ word: string; meaning: string }>;  
}

export function FeedbackModal({ isOpen, onClose, onSaveFeedback, jargonWords = [] }: FeedbackModalProps) {
  const [description, setDescription] = useState('');
  const [items, setItems] = useState<FeedbackItem[]>(() => 
    jargonWords.length > 0 
      ? jargonWords.map(jargon => ({
          word: jargon.word,
          meaning: jargon.meaning || '',
          isPreFilled: true
        }))
      : [{ word: '', meaning: '', isPreFilled: false }]
  );
  const [isSubmitted, setIsSubmitted] = useState(false);

  useEffect(() => {
    if (jargonWords.length > 0) {
      const jargonItems = jargonWords.map(jargon => ({
        word: jargon.word,
        meaning: jargon.meaning || '',
        isPreFilled: true
      }));
      setItems(jargonItems);
    }
  }, [jargonWords]);

  const handleAddItem = () => {
    setItems([...items, { word: '', meaning: '', isPreFilled: false }]);
  };

  const handleRemoveItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleItemChange = (index: number, field: 'word' | 'meaning', value: string) => {
    const newItems = [...items];
    newItems[index][field] = value;
    setItems(newItems);
  };

  const handleSubmit = async () => {
    const validItems = items.filter(item => item.word.trim() && item.meaning.trim())
      .map(({ word, meaning }) => ({ word, meaning }));
    
    try {
      setIsSubmitted(true);
      
      await onSaveFeedback({
        feedback: description,
        clarification: validItems
      }); 
      
      setTimeout(() => {
        setIsSubmitted(false);
        onClose();
      }, 2000);
    } catch (error) {
      console.error('Error sending feedback:', error);
      setIsSubmitted(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl mx-4">
        <div className="flex justify-between items-center p-4 border-b">
          <h3 className="text-lg font-semibold">Provide Detailed Feedback</h3>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
        
        <div className="p-4 space-y-4">
          {isSubmitted ? (
            <div className="text-center space-y-2">
              <p className="text-lg font-medium">Thank you for your feedback!</p>
              <p className="text-sm text-gray-600">Regenerating a new response based on your feedback...</p>
            </div>
          ) : (
            <>
              <div>
                <label className="block text-sm font-medium mb-2">Description</label>
                <Textarea
                  placeholder="Please describe why this response was incorrect..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="min-h-[100px]"
                />
              </div>

              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <label className="block text-sm font-medium">Words and Meanings</label>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleAddItem}
                    className="flex items-center gap-1"
                  >
                    <Plus className="h-4 w-4" /> Add Custom Word
                  </Button>
                </div>

                {items.map((item, index) => (
                  <div key={index} className="flex gap-2 items-start">
                    <Input
                      placeholder="Word"
                      value={item.word}
                      onChange={(e) => handleItemChange(index, 'word', e.target.value)}
                      className="flex-1"
                      disabled={item.isPreFilled}
                      readOnly={item.isPreFilled}
                    />
                    <Input
                      placeholder="Enter meaning..."
                      value={item.meaning}
                      onChange={(e) => handleItemChange(index, 'meaning', e.target.value)}
                      className="flex-1"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => handleRemoveItem(index)}
                      disabled={item.isPreFilled}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        {!isSubmitted && (
          <div className="p-4 border-t">
            <Button
              type="button"
              onClick={handleSubmit}
              className="ml-auto flex items-center gap-2"
            >
              <Save className="h-4 w-4" /> Save Feedback
            </Button>
          </div>
        )}
      </div>
    </div>
  );
} 