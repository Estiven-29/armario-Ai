/**
 * Quita el fondo de una foto de prenda en el navegador (BEN2, licencia MIT).
 * Basado en el módulo `remove-bg` de https://github.com/midudev/runonweb.ai
 *
 * - Corre en WASM: BEN2 falla en WebGPU por un bug de onnxruntime-web.
 * - Descarga ~219 MB la primera vez (queda en caché del navegador).
 * - Devuelve un PNG con canal alfa.
 */
const MODEL = 'onnx-community/BEN2-ONNX'

export type BgProgress = { status: 'descargando' | 'procesando'; progress?: number }

type Pipe = (images: unknown[]) => Promise<Array<{ toBlob: () => Promise<Blob> }>>

let pipePromise: Promise<Pipe> | null = null

function loadPipe(onProgress?: (p: BgProgress) => void): Promise<Pipe> {
  if (!pipePromise) {
    pipePromise = (async () => {
      const { pipeline, env } = await import('@huggingface/transformers')
      env.allowLocalModels = false
      env.allowRemoteModels = true
      const wasm = env.backends?.onnx?.wasm
      // Sin aislamiento de origen no hay SharedArrayBuffer: un solo hilo evita crashes.
      if (wasm && !globalThis.crossOriginIsolated) wasm.numThreads = 1
      const pipe = await pipeline('background-removal' as never, MODEL, {
        device: 'wasm' as never,
        dtype: 'fp16' as never,
        progress_callback: (d: Record<string, unknown>) => {
          if (d.status === 'progress' && typeof d.progress === 'number') {
            onProgress?.({ status: 'descargando', progress: d.progress })
          }
        },
      })
      return pipe as unknown as Pipe
    })().catch((e) => {
      pipePromise = null // permite reintentar
      throw e
    })
  }
  return pipePromise
}

/** Descarga/inicializa el modelo con antelación (opcional). */
export function preloadBackgroundModel(onProgress?: (p: BgProgress) => void) {
  return loadPipe(onProgress).then(() => undefined)
}

/** Devuelve un File PNG con fondo transparente. */
export async function removeBackground(
  file: File,
  onProgress?: (p: BgProgress) => void,
): Promise<File> {
  const pipe = await loadPipe(onProgress)
  onProgress?.({ status: 'procesando' })
  const { RawImage } = await import('@huggingface/transformers')
  const input = await RawImage.fromBlob(file)
  const [result] = await pipe([input])
  if (!result) throw new Error('No se pudo quitar el fondo')
  const blob = await result.toBlob()
  const name = file.name.replace(/\.[^.]+$/, '') + '.png'
  return new File([blob], name, { type: 'image/png' })
}
