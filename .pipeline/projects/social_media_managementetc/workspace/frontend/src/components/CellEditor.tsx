import React, { useState, useEffect, useRef } from 'react'

interface CellEditorProps {
  value: string
  onSave: (value: string) => void
  onCancel: () => void
}

export function CellEditor({ value, onSave, onCancel }: CellEditorProps) {
  const [inputValue, setInputValue] = useState(value)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSave = () => {
    onSave(inputValue)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSave()
    if (e.key === 'Escape') onCancel()
  }

  return (
    <input
      ref={inputRef}
      value={inputValue}
      onChange={e => setInputValue(e.target.value)}
      onKeyDown={handleKeyDown}
      onBlur={handleSave}
      style={{ width: '100%', padding: '4px', border: '1px solid #007bff', borderRadius: '4px' }}
    />
  )
}
