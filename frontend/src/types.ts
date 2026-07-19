export interface Item {
  id: number
  image_path: string
  image_url: string
  nombre: string
  categoria: string
  tipo: string
  color_principal: string
  colores: string[]
  patron: string
  material: string
  estilo: string
  temporada: string
  formalidad: number
  notas: string
  ai_confianza: number
  created_at: string
}

export interface Taxonomy {
  categorias: string[]
  tipos: string[]
  colores: string[]
  patrones: string[]
  materiales: string[]
  estilos: string[]
  temporadas: string[]
  formalidad: number[]
  ocasiones: string[]
}

export interface OutfitSuggestion {
  nombre: string
  item_ids: number[]
  razon: string
}

export interface SuggestResponse {
  sugerencias: OutfitSuggestion[]
  ai_usada: boolean
}

export interface Outfit {
  id: number
  nombre: string
  ocasion: string
  item_ids: number[]
  razon: string
  favorito: boolean
  created_at: string
}
