import { useState } from 'react'
import { api } from '../api'
import type { Item, OutfitSuggestion, Taxonomy } from '../types'

interface Props {
  items: Item[]
  taxonomy: Taxonomy | null
  aiEnabled: boolean
}

export function OutfitGenerator({ items, taxonomy, aiEnabled }: Props) {
  const [ocasion, setOcasion] = useState('casual')
  const [clima, setClima] = useState('')
  const [preferencias, setPreferencias] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [aiUsada, setAiUsada] = useState<boolean | null>(null)
  const [sugerencias, setSugerencias] = useState<OutfitSuggestion[]>([])
  const [savedIds, setSavedIds] = useState<Set<number>>(new Set())

  const byId = new Map(items.map((i) => [i.id, i]))

  async function generate() {
    setLoading(true)
    setError('')
    setSavedIds(new Set())
    try {
      const res = await api.suggestOutfits({ ocasion, clima, preferencias, n_sugerencias: 3 })
      setSugerencias(res.sugerencias)
      setAiUsada(res.ai_usada)
      if (res.sugerencias.length === 0) {
        setError('No se pudieron generar outfits. Añade prendas de varias categorías.')
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error al generar')
    } finally {
      setLoading(false)
    }
  }

  async function save(s: OutfitSuggestion, idx: number) {
    await api.saveOutfit({ ...s, ocasion })
    setSavedIds((prev) => new Set(prev).add(idx))
  }

  return (
    <div className="generator">
      <div className="gen-form">
        <label className="field">
          <span>Ocasión</span>
          <select value={ocasion} onChange={(e) => setOcasion(e.target.value)}>
            {taxonomy?.ocasiones.map((o) => (
              <option key={o}>{o}</option>
            ))}
          </select>
        </label>
        <label className="field">
          <span>Clima / temperatura</span>
          <input
            placeholder="p.ej. frío 8°C, lluvia, calor 30°C"
            value={clima}
            onChange={(e) => setClima(e.target.value)}
          />
        </label>
        <label className="field">
          <span>Preferencias</span>
          <input
            placeholder="p.ej. tonos neutros, cómodo, elegante"
            value={preferencias}
            onChange={(e) => setPreferencias(e.target.value)}
          />
        </label>
        <button className="btn-primary" onClick={generate} disabled={loading}>
          {loading ? 'Generando…' : 'Generar outfits'}
        </button>
      </div>

      {!aiEnabled && (
        <p className="note">
          Modo de prueba: sin API key de Gemini se generan combinaciones básicas. Configura
          la key para sugerencias razonadas según moda, color y clima.
        </p>
      )}
      {aiUsada === true && <p className="note note-ok">Sugerencias generadas con IA (Gemini).</p>}
      {error && <p className="error">{error}</p>}

      <div className="outfits">
        {sugerencias.map((s, idx) => (
          <div className="outfit-card" key={idx}>
            <h3>{s.nombre}</h3>
            <div className="outfit-items">
              {s.item_ids.map((id) => {
                const it = byId.get(id)
                if (!it) return null
                return (
                  <div className="outfit-thumb" key={id}>
                    <img src={it.image_url} alt={it.nombre || it.tipo} />
                    <span>{it.nombre || it.tipo}</span>
                  </div>
                )
              })}
            </div>
            <p className="razon">{s.razon}</p>
            <button
              className="btn-primary"
              onClick={() => save(s, idx)}
              disabled={savedIds.has(idx)}
            >
              {savedIds.has(idx) ? 'Guardado ✓' : 'Guardar outfit'}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
