import type {
  Item,
  Outfit,
  OutfitSuggestion,
  SuggestResponse,
  Taxonomy,
} from './types'

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail ?? detail
    } catch {
      /* ignore */
    }
    throw new Error(detail)
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export const api = {
  health: () =>
    fetch('/api/health').then((r) => handle<{ status: string; ai_enabled: boolean }>(r)),

  taxonomy: () => fetch('/api/taxonomy').then((r) => handle<Taxonomy>(r)),

  listItems: (filters: Record<string, string> = {}) => {
    const q = new URLSearchParams(
      Object.entries(filters).filter(([, v]) => v),
    ).toString()
    return fetch(`/api/items${q ? `?${q}` : ''}`).then((r) => handle<Item[]>(r))
  },

  createItem: (file: File) => {
    const fd = new FormData()
    fd.append('file', file)
    return fetch('/api/items', { method: 'POST', body: fd }).then((r) => handle<Item>(r))
  },

  updateItem: (id: number, patch: Partial<Item>) =>
    fetch(`/api/items/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patch),
    }).then((r) => handle<Item>(r)),

  deleteItem: (id: number) =>
    fetch(`/api/items/${id}`, { method: 'DELETE' }).then((r) => handle<void>(r)),

  suggestOutfits: (payload: {
    ocasion: string
    clima: string
    preferencias: string
    n_sugerencias: number
  }) =>
    fetch('/api/outfits/suggest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then((r) => handle<SuggestResponse>(r)),

  saveOutfit: (payload: OutfitSuggestion & { ocasion: string }) =>
    fetch('/api/outfits', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).then((r) => handle<Outfit>(r)),

  listOutfits: () => fetch('/api/outfits').then((r) => handle<Outfit[]>(r)),

  deleteOutfit: (id: number) =>
    fetch(`/api/outfits/${id}`, { method: 'DELETE' }).then((r) => handle<void>(r)),
}
