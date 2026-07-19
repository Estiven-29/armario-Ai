import { useEffect, useState } from 'react'
import './App.css'
import { api } from './api'
import type { Item, Taxonomy } from './types'
import { UploadPanel } from './components/UploadPanel'
import { Wardrobe } from './components/Wardrobe'
import { OutfitGenerator } from './components/OutfitGenerator'

type Tab = 'armario' | 'outfits'

function App() {
  const [tab, setTab] = useState<Tab>('armario')
  const [items, setItems] = useState<Item[]>([])
  const [taxonomy, setTaxonomy] = useState<Taxonomy | null>(null)
  const [aiEnabled, setAiEnabled] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.listItems(), api.taxonomy(), api.health()])
      .then(([its, tax, health]) => {
        setItems(its)
        setTaxonomy(tax)
        setAiEnabled(health.ai_enabled)
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="app">
      <header className="header">
        <h1>👕 Armario IA</h1>
        <p>Organiza tu armario y crea outfits con IA</p>
        <nav className="tabs">
          <button
            className={tab === 'armario' ? 'active' : ''}
            onClick={() => setTab('armario')}
          >
            Mi armario ({items.length})
          </button>
          <button
            className={tab === 'outfits' ? 'active' : ''}
            onClick={() => setTab('outfits')}
          >
            Crear outfit
          </button>
        </nav>
      </header>

      <main className="main">
        {loading ? (
          <p className="empty">Cargando…</p>
        ) : tab === 'armario' ? (
          <>
            <UploadPanel onAdded={(item) => setItems((prev) => [item, ...prev])} />
            <Wardrobe
              items={items}
              taxonomy={taxonomy}
              onChange={(u) =>
                setItems((prev) => prev.map((i) => (i.id === u.id ? u : i)))
              }
              onDelete={(id) => {
                api.deleteItem(id)
                setItems((prev) => prev.filter((i) => i.id !== id))
              }}
            />
          </>
        ) : (
          <OutfitGenerator items={items} taxonomy={taxonomy} aiEnabled={aiEnabled} />
        )}
      </main>
    </div>
  )
}

export default App
