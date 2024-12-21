import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface PythonEditorProps {
  code: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  showLineNumbers?: boolean;
  minHeight?: string;
  maxHeight?: string;
}

export const PythonEditor: React.FC<PythonEditorProps> = ({
  code,
  onChange,
  placeholder = '# Enter your Python code here...',
  disabled = false,
  showLineNumbers = true,
  minHeight = '200px',
  maxHeight = '600px',
}) => {
  const [isFocused, setIsFocused] = useState(false);

  const handleKeyDown = (e: React.  KeyboardEvent<HTMLTextAreaElement>) => {
    const textarea = e.currentTarget;
    const { selectionStart, selectionEnd, value } = textarea;

    // Handle Tab key
    if (e.key === 'Tab') {
      e.preventDefault();
      
      // Insert 4 spaces for tab
      const newValue = value.substring(0, selectionStart) + '    ' + value.substring(selectionEnd);
      onChange(newValue);
      
      // Move cursor after the inserted spaces
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = selectionStart + 4;
      }, 0);
    }

    // Handle Enter key
    if (e.key === 'Enter') {
      e.preventDefault();
      
      // Get the current line
      const currentLine = value.substring(0, selectionStart).split('\n').pop() || '';
      
      // Calculate the indentation of the current line
      const indentMatch = currentLine.match(/^\s*/);
      const currentIndent = indentMatch ? indentMatch[0] : '';
      
      // Check if the line ends with a colon
      const shouldAddIndent = currentLine.trim().endsWith(':');
      
      // Create the new line with proper indentation
      const newIndent = shouldAddIndent ? currentIndent + '    ' : currentIndent;
      const newValue = value.substring(0, selectionStart) + '\n' + newIndent + value.substring(selectionEnd);
      
      onChange(newValue);
      
      // Move cursor to the start of the new line after indentation
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = selectionStart + 1 + newIndent.length;
      }, 0);
    }

    // Handle Backspace for dedentation
    if (e.key === 'Backspace') {
      const currentLine = value.substring(0, selectionStart).split('\n').pop() || '';
      const lineStart = selectionStart - currentLine.length;
      
      // If at the start of an indented line
      if (currentLine.match(/^\s+$/) && selectionStart === lineStart + currentLine.length) {
        e.preventDefault();
        
        // Remove one level of indentation (4 spaces)
        const newIndent = currentLine.slice(0, Math.max(0, currentLine.length - 4));
        const newValue = value.substring(0, lineStart) + newIndent + value.substring(selectionStart);
        
        onChange(newValue);
        
        // Move cursor to new position
        setTimeout(() => {
          textarea.selectionStart = textarea.selectionEnd = lineStart + newIndent.length;
        }, 0);
      }
    }
  };

  return (
    <div className={`relative rounded-lg border ${isFocused ? 'border-blue-400' : 'border-gray-200'} bg-white shadow-sm overflow-hidden transition-colors`}>
      <div className="flex items-center justify-between px-4 py-2 bg-gray-50 border-b border-gray-200">
        <span className="text-sm font-medium text-gray-700">Python Editor</span>
        <span className="text-xs text-gray-500">
          Press Tab for indentation, Shift+Tab to unindent
        </span>
      </div>

      <div className="relative" style={{ minHeight, maxHeight }}>
        <SyntaxHighlighter
          language="python"
          style={vscDarkPlus}
          showLineNumbers={showLineNumbers}
          customStyle={{
            margin: 0,
            padding: '16px',
            background: 'white',
            fontSize: '14px',
            minHeight,
            maxHeight,
          }}
          className="!bg-white overflow-auto"
        >
          {code || placeholder}
        </SyntaxHighlighter>
        <textarea
          value={code}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          className="absolute inset-0 w-full h-full opacity-0 cursor-text resize-none font-mono p-4 bg-transparent"
          placeholder={placeholder}
          spellCheck={false}
          disabled={disabled}
        />
      </div>

      <div className="flex items-center justify-between px-4 py-2 bg-gray-50 border-t border-gray-200">
        <span className="text-xs text-gray-500">
          {code.split('\n').length} lines | {code.length} characters
        </span>
        <span className="text-xs text-gray-500">
          {isFocused ? 'Editing' : 'Click to edit'}
        </span>
      </div>
    </div>
  );
}; 