import React, { useState, useRef, useEffect } from 'react';

export interface Option {
  label: string;
  value: string;
}

interface MultiSelectProps {
  options: Option[];
  value: string[];
  onChange: (selected: string[]) => void;
  placeholder?: string;
  label?: string;
}

export const MultiSelect: React.FC<MultiSelectProps> = ({
  options,
  value,
  onChange,
  placeholder = 'Select items',
  label,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const toggleOption = (optionValue: string) => {
    const updated = value.includes(optionValue)
      ? value.filter((v) => v !== optionValue)
      : [...value, optionValue];
    onChange(updated);
  };

  const removeOption = (e: React.MouseEvent, optionValue: string) => {
    e.stopPropagation();
    onChange(value.filter((v) => v !== optionValue));
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const selectedOptions = options.filter((opt) => value.includes(opt.value));

  return (
    <div className="multi-select-wrapper" ref={containerRef}>
      {label && <label className="multi-select-label">{label}</label>}
      <div className="multi-select-container">
        <div className="multi-select-trigger" onClick={() => setIsOpen(!isOpen)}>
          {selectedOptions.length === 0 ? (
            <span className="multi-select-placeholder">{placeholder}</span>
          ) : (
            selectedOptions.map((opt) => (
              <span key={opt.value} className="multi-select-chip">
                {opt.label}
                <button
                  type="button"
                  className="chip-remove"
                  onClick={(e) => removeOption(e, opt.value)}
                >
                  &times;
                </button>
              </span>
            ))
          )}
        </div>

        {isOpen && (
          <div className="multi-select-dropdown">
            {options.map((opt) => {
              const isSelected = value.includes(opt.value);
              return (
                <div
                  key={opt.value}
                  className={`multi-select-option ${isSelected ? 'selected' : ''}`}
                  onClick={() => toggleOption(opt.value)}
                >
                  {opt.label}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};