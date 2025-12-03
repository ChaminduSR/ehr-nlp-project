import { useState, useRef } from 'react'
import axios from 'axios'
import { Button } from './Button'

interface VoiceInputProps {
  onTranscribe: (text: string) => void;
  disabled?: boolean;
}

// Helper to write string to DataView
const writeString = (view: DataView, offset: number, string: string) => {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i))
  }
}

// Helper to convert AudioBuffer to WAV Blob (16-bit Mono)
const audioBufferToWav = (buffer: AudioBuffer): Blob => {
  const numChannels = 1 // Force mono for VOSK
  const sampleRate = buffer.sampleRate
  const format = 1 // PCM
  const bitDepth = 16

  // Flatten to mono if needed
  let data = buffer.getChannelData(0)
  if (buffer.numberOfChannels > 1) {
    // Simple average of first two channels if stereo
    const ch2 = buffer.getChannelData(1)
    const mono = new Float32Array(data.length)
    for (let i = 0; i < data.length; i++) {
      mono[i] = (data[i] + ch2[i]) / 2
    }
    data = mono
  }

  const bytesPerSample = bitDepth / 8
  const blockAlign = numChannels * bytesPerSample
  const byteRate = sampleRate * blockAlign
  const dataSize = data.length * blockAlign
  const bufferSize = 44 + dataSize
  const arrayBuffer = new ArrayBuffer(bufferSize)
  const view = new DataView(arrayBuffer)

  // RIFF chunk
  writeString(view, 0, 'RIFF')
  view.setUint32(4, 36 + dataSize, true)
  writeString(view, 8, 'WAVE')

  // fmt chunk
  writeString(view, 12, 'fmt ')
  view.setUint32(16, 16, true) // Subchunk1Size (16 for PCM)
  view.setUint16(20, format, true)
  view.setUint16(22, numChannels, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, byteRate, true)
  view.setUint16(32, blockAlign, true)
  view.setUint16(34, bitDepth, true)

  // data chunk
  writeString(view, 36, 'data')
  view.setUint32(40, dataSize, true)

  // Write PCM samples
  let offset = 44
  for (let i = 0; i < data.length; i++) {
    const sample = Math.max(-1, Math.min(1, data[i])) // Clamp
    // Scale to 16-bit integer range
    const intSample = sample < 0 ? sample * 0x8000 : sample * 0x7FFF
    view.setInt16(offset, intSample, true)
    offset += 2
  }

  return new Blob([arrayBuffer], { type: 'audio/wav' })
}

export default function VoiceInput({ onTranscribe, disabled }: VoiceInputProps) {
  const [isRecording, setIsRecording] = useState<boolean>(false)
  const [isProcessing, setIsProcessing] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<BlobPart[]>([])

  const startRecording = async () => {
    setError(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (e: BlobEvent) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorder.onstop = async () => {
        const rawBlob = new Blob(chunksRef.current, { type: 'audio/webm' }) // Browser default
        await processAudio(rawBlob)

        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (err: any) {
      console.error('Error accessing microphone:', err)
      setError('Could not access microphone. Please check permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setIsProcessing(true)
    }
  }

  const processAudio = async (rawBlob: Blob) => {
    try {
      // 1. Ensure model is loaded
      await axios.post('/api/v1/voice/load-model')

      // 2. Convert WebM/Ogg Blob to WAV (16-bit Mono) for VOSK
      const arrayBuffer = await rawBlob.arrayBuffer()
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
      const wavBlob = audioBufferToWav(audioBuffer)

      const formData = new FormData()
      formData.append('audio', wavBlob, 'recording.wav')

      const res = await axios.post('/api/v1/voice/transcribe', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      if (res.data.text) {
        onTranscribe(res.data.text)
      }
    } catch (err: any) {
      console.error('Transcription failed:', err)
      setError(err.response?.data?.error || 'Transcription failed')
    } finally {
      setIsProcessing(false)
    }
  }

  if (!navigator.mediaDevices) {
    return <div className="text-sm text-error">Voice input not supported</div>
  }

  return (
    <div className="voice-input-container" style={{ display: 'inline-block' }}>
      {error && <div className="text-sm text-error mb-2">{error}</div>}

      <Button
        variant={isRecording ? 'error' : 'secondary'}
        onClick={isRecording ? stopRecording : startRecording}
        disabled={disabled || isProcessing}
        className="btn-sm"
        title={isRecording ? 'Stop Recording' : 'Start Dictation'}
      >
        {isProcessing ? 'Processing...' : isRecording ? '⏹ Stop' : '🎤 Dictate'}
      </Button>
    </div>
  )
}
