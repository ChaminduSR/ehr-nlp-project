// Voice Recorder for VOSK (Vanilla JS)

const VoiceRecorder = {
    isRecording: false,
    mediaRecorder: null,
    chunks: [],

    // Helper: Write string to DataView
    writeString(view, offset, string) {
        for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i));
        }
    },

    // Helper: Convert AudioBuffer to WAV Blob (16-bit Mono)
    audioBufferToWav(buffer) {
        const numChannels = 1; // Force mono for VOSK
        const sampleRate = buffer.sampleRate;
        const format = 1; // PCM
        const bitDepth = 16;

        // Flatten to mono if needed
        let data = buffer.getChannelData(0);
        if (buffer.numberOfChannels > 1) {
            const ch2 = buffer.getChannelData(1);
            const mono = new Float32Array(data.length);
            for (let i = 0; i < data.length; i++) {
                mono[i] = (data[i] + ch2[i]) / 2;
            }
            data = mono;
        }

        const bytesPerSample = bitDepth / 8;
        const blockAlign = numChannels * bytesPerSample;
        const byteRate = sampleRate * blockAlign;
        const dataSize = data.length * blockAlign;
        const bufferSize = 44 + dataSize;
        const arrayBuffer = new ArrayBuffer(bufferSize);
        const view = new DataView(arrayBuffer);

        // RIFF chunk
        this.writeString(view, 0, 'RIFF');
        view.setUint32(4, 36 + dataSize, true);
        this.writeString(view, 8, 'WAVE');

        // fmt chunk
        this.writeString(view, 12, 'fmt ');
        view.setUint32(16, 16, true); // Subchunk1Size (16 for PCM)
        view.setUint16(20, format, true);
        view.setUint16(22, numChannels, true);
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, byteRate, true);
        view.setUint16(32, blockAlign, true);
        view.setUint16(34, bitDepth, true);

        // data chunk
        this.writeString(view, 36, 'data');
        view.setUint32(40, dataSize, true);

        // Write PCM samples
        let offset = 44;
        for (let i = 0; i < data.length; i++) {
            const sample = Math.max(-1, Math.min(1, data[i])); // Clamp
            // Scale to 16-bit integer range
            const intSample = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
            view.setInt16(offset, intSample, true);
            offset += 2;
        }

        return new Blob([arrayBuffer], { type: 'audio/wav' });
    },

    async start() {
        try {
            // Ensure model is loaded (lazy load)
            await fetch('/api/v1/voice/load-model', { method: 'POST' });

            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.chunks = [];

            this.mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    this.chunks.push(e.data);
                }
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            return true;
        } catch (err) {
            console.error("Error starting recording:", err);
            alert("Could not access microphone. Please check permissions.");
            return false;
        }
    },

    stop() {
        return new Promise((resolve, reject) => {
            if (!this.mediaRecorder || !this.isRecording) {
                resolve(null);
                return;
            }

            this.mediaRecorder.onstop = async () => {
                try {
                    const rawBlob = new Blob(this.chunks, { type: 'audio/webm' });

                    // Convert to AudioBuffer then to WAV
                    const arrayBuffer = await rawBlob.arrayBuffer();
                    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
                    const wavBlob = this.audioBufferToWav(audioBuffer);

                    // Send to backend
                    const formData = new FormData();
                    formData.append('audio', wavBlob, 'recording.wav');

                    const response = await fetch('/api/v1/voice/transcribe', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();

                    // Stop all tracks
                    this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
                    this.isRecording = false;

                    if (result.text) {
                        resolve(result.text);
                    } else {
                        reject(result.error || "Transcription failed");
                    }
                } catch (err) {
                    reject(err);
                }
            };

            this.mediaRecorder.stop();
        });
    }
};

window.VoiceRecorder = VoiceRecorder;
