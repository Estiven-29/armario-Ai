import { useState } from 'react'
import { api } from '../api'
import type { Item, Taxonomy } from '../types'

interface Props {
  item: Item
  taxonomy: Taxonomy | null
  selectable?: boolean
  selected?: boolean
  onToggle?: (id: number) => void
  onChange: (item: Item) => void
  onDelete: (id: number) => void
}

export function ItemCard({
  item,
  taxonomy,
  selectable,
  selected,
  onToggle,
  onChange,
  onDelete,
}: Props) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState<Item>(item)
  const [saving, setSaving] = useState(false)

  async function save() {
    setSaving(true)
    try {
      const updated = await api.updateItem(item.id, {
        nombre: draft.nombre,
        categoria: draft.categoria,
        tipo: draft.tipo,
        color_principal: draft.color_principal,
        estilo: draft.estilo,
        temporada: draft.temporada,
        formalidad: Number(draft.formalidad),
        material: draft.material,
        patron: draft.patron,
      })
      onChange(updated)
      setEditing(false)
    } finally {
      setSaving(false)
    }
  }

  function field(label: string, key: keyof Item, options?: string[]) {
    return (
      <label className="field">
        <span>{label}</span>
        {options ? (
          <select
            value={String(draft[key] ?? '')}
            onChange={(e) => setDraft({ ...draft, [key]: e.target.value })}
          >
            <option value="">—</option>
            {options.map((o) => (
              <option key={o} value={o}>
                {o}
              </option>
            ))}
          </select>
        ) : (
          <input
            value={String(draft[key] ?? '')}
            onChange={(e) => setDraft({ ...draft, [key]: e.target.value })}
          />
        )}
      </label>
    )
  }

  return (
    <div className={`card ${selected ? 'card-selected' : ''}`}>
      <div
        className="card-img"
        onClick={() => selectable && onToggle?.(item.id)}
        style={{ cursor: selectable ? 'pointer' : 'default' }}
      >
        <img src={item.image_url} alt={item.nombre || item.tipo} />
        {selectable && <div className="check">{selected ? '✓' : ''}</div>}
        {!item.categoria && !editing && (
          <div className="badge-warn" title="Sin categorizar">?</div>
        )}
      </div>

      {editing ? (
        <div className="card-edit">
          {field('Nombre', 'nombre')}
          {field('Categoría', 'categoria', taxonomy?.categorias)}
          {field('Tipo', 'tipo', taxonomy?.tipos)}
          {field('Color', 'color_principal', taxonomy?.colores)}
          {field('Estilo', 'estilo', taxonomy?.estilos)}
          {field('Temporada', 'temporada', taxonomy?.temporadas)}
          {field('Material', 'material', taxonomy?.materiales)}
          {field('Patrón', 'patron', taxonomy?.patrones)}
          {field('Formalidad (1-5)', 'formalidad')}
          <div className="card-actions">
            <button className="btn-primary" onClick={save} disabled={saving}>
              {saving ? 'Guardando…' : 'Guardar'}
            </button>
            <button
              onClick={() => {
                setDraft(item)
                setEditing(false)
              }}
            >
              Cancelar
            </button>
          </div>
        </div>
      ) : (
        <div className="card-body">
          <strong>{item.nombre || item.tipo || 'Prenda'}</strong>
          <div className="tags">
            {item.categoria && <span className="tag">{item.categoria}</span>}
            {item.color_principal && (
              <span className="tag tag-color">{item.color_principal}</span>
            )}
            {item.estilo && <span className="tag">{item.estilo}</span>}
            {item.temporada && <span className="tag">{item.temporada}</span>}
          </div>
          <div className="card-actions">
            <button onClick={() => setEditing(true)}>Editar</button>
            <button className="btn-danger" onClick={() => onDelete(item.id)}>
              Eliminar
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
