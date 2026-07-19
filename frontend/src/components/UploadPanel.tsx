import { useRef, useState } from 'react'
import { api } from '../api'
import type { Item } from '../types'

interface Props {
  onAdded: (item: Item) => void
}

export function UploadPanel({ onAdded }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')

  async function handleFiles(files: FileList | null) {
    if (!files || files.length === 0) return
    setError('')
    setUploading(true)
    try {
      for (const file of Array.from(files)) {
        const item = await api.createItem(file)
        onAdded(item)
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al subir')
    } finally {
      setUploading(false)
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  return (
    <div
      className="upload"
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault()
        handleFiles(e.dataTransfer.files)
      }}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/png,image/jpeg,image/webp"
        multiple
        hidden
        onChange={(e) => handleFiles(e.target.files)}
      />
      <div className="upload-icon">＋</div>
      <p>
        {uploading
          ? 'Analizando prenda con IA…'
          : 'Arrastra fotos de tus prendas o haz clic para subir'}
      </p>
      <span className="hint">JPG, PNG o WEBP · varias a la vez</span>
      {error && <p className="error">{error}</p>}
    </div>
  )
}
