import { useRef, useState } from 'react'
import { api } from '../api'
import type { Item } from '../types'
import { removeBackground } from '../removeBackground'

interface Props {
  onAdded: (item: Item) => void
}

export function UploadPanel({ onAdded }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')
  const [removeBg, setRemoveBg] = useState(true)

  async function handleFiles(files: FileList | null) {
    if (!files || files.length === 0) return
    setError('')
    setUploading(true)
    try {
      const list = Array.from(files)
      for (const [i, original] of list.entries()) {
        const prefix = list.length > 1 ? `(${i + 1}/${list.length}) ` : ''
        let file = original
        if (removeBg) {
          try {
            file = await removeBackground(original, (p) =>
              setStatus(
                p.status === 'descargando'
                  ? `${prefix}Descargando modelo de recorte… ${Math.round(p.progress ?? 0)}% (solo la primera vez)`
                  : `${prefix}Quitando el fondo…`,
              ),
            )
          } catch (e) {
            console.warn('No se pudo quitar el fondo; se sube la foto original', e)
            file = original
          }
        }
        setStatus(`${prefix}Analizando prenda con IA…`)
        const item = await api.createItem(file)
        onAdded(item)
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al subir')
    } finally {
      setUploading(false)
      setStatus('')
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
      onClick={() => !uploading && inputRef.current?.click()}
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
          ? status || 'Procesando…'
          : 'Arrastra fotos de tus prendas o haz clic para subir'}
      </p>
      <span className="hint">JPG, PNG o WEBP · varias a la vez</span>
      <label className="hint" onClick={(e) => e.stopPropagation()}>
        <input
          type="checkbox"
          checked={removeBg}
          disabled={uploading}
          onChange={(e) => setRemoveBg(e.target.checked)}
        />{' '}
        Quitar el fondo automáticamente (en tu dispositivo)
      </label>
      {error && <p className="error">{error}</p>}
    </div>
  )
}
