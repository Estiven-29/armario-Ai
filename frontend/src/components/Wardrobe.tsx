import { useMemo, useState } from 'react'
import type { Item, Taxonomy } from '../types'
import { ItemCard } from './ItemCard'

interface Props {
  items: Item[]
  taxonomy: Taxonomy | null
  onChange: (item: Item) => void
  onDelete: (id: number) => void
}

export function Wardrobe({ items, taxonomy, onChange, onDelete }: Props) {
  const [categoria, setCategoria] = useState('')
  const [estilo, setEstilo] = useState('')
  const [color, setColor] = useState('')

  const filtered = useMemo(
    () =>
      items.filter(
        (i) =>
          (!categoria || i.categoria === categoria) &&
          (!estilo || i.estilo === estilo) &&
          (!color || i.color_principal === color),
      ),
    [items, categoria, estilo, color],
  )

  return (
    <div>
      <div className="filters">
        <select value={categoria} onChange={(e) => setCategoria(e.target.value)}>
          <option value="">Todas las categorías</option>
          {taxonomy?.categorias.map((c) => (
            <option key={c}>{c}</option>
          ))}
        </select>
        <select value={estilo} onChange={(e) => setEstilo(e.target.value)}>
          <option value="">Todos los estilos</option>
          {taxonomy?.estilos.map((c) => (
            <option key={c}>{c}</option>
          ))}
        </select>
        <select value={color} onChange={(e) => setColor(e.target.value)}>
          <option value="">Todos los colores</option>
          {taxonomy?.colores.map((c) => (
            <option key={c}>{c}</option>
          ))}
        </select>
        <span className="count">{filtered.length} prendas</span>
      </div>

      {filtered.length === 0 ? (
        <p className="empty">No hay prendas con esos filtros. Sube algunas fotos arriba.</p>
      ) : (
        <div className="grid">
          {filtered.map((item) => (
            <ItemCard
              key={item.id}
              item={item}
              taxonomy={taxonomy}
              onChange={onChange}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}
    </div>
  )
}
