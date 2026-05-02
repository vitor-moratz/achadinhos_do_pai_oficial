import { useState, useRef, useEffect } from 'react'
import './CustomSelect.css'

export function CustomSelect({
  value,
  onChange,
  options = [],
  placeholder = 'Selecione',
  className = '',
}) {
  const [open, setOpen] = useState(false)
  const [openUp, setOpenUp] = useState(false)
  const ref = useRef(null)

  const selected = options.find((o) => String(o.value) === String(value))

  // Fechar ao clicar fora
  useEffect(() => {
    function handleOutside(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handleOutside)
    return () => document.removeEventListener('mousedown', handleOutside)
  }, [])

  // ESC fecha o dropdown sem fechar o modal
  useEffect(() => {
    if (!open) return
    function handleKey(e) {
      if (e.key === 'Escape') {
        e.stopPropagation()
        setOpen(false)
      }
    }
    document.addEventListener('keydown', handleKey, true)
    return () => document.removeEventListener('keydown', handleKey, true)
  }, [open])

  function handleToggle() {
    if (!open && ref.current) {
      const rect = ref.current.getBoundingClientRect()
      const spaceBelow = window.innerHeight - rect.bottom
      setOpenUp(spaceBelow < 260)
    }
    setOpen((o) => !o)
  }

  const hasValue = value !== '' && value != null

  return (
    <div
      className={`cselect${open ? ' cselect--open' : ''}${hasValue ? ' cselect--has-value' : ''}${openUp ? ' cselect--up' : ''}${className ? ' ' + className : ''}`}
      ref={ref}
    >
      <button
        type="button"
        className="cselect-trigger"
        onClick={handleToggle}
      >
        <span className="cselect-value">
          {selected ? selected.label : <span className="cselect-ph">{placeholder}</span>}
        </span>
        <svg
          className="cselect-arrow"
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      {open && (
        <ul className="cselect-list" role="listbox">
          {options.map((opt) => (
            <li
              key={String(opt.value)}
              role="option"
              aria-selected={String(opt.value) === String(value)}
              className={`cselect-opt${String(opt.value) === String(value) ? ' cselect-opt--active' : ''}`}
              onMouseDown={(e) => {
                e.preventDefault()
                onChange(opt.value)
                setOpen(false)
              }}
            >
              {opt.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
