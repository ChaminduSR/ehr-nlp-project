"""Voice recognition endpoints - VOSK transcription (async)"""
import asyncio
import json
import os

from flask import Blueprint, request, jsonify

voice_bp = Blueprint('voice', __name__)

# Global VOSK model (lazy loaded)
vosk_model = None

@voice_bp.route('/load-model', methods=['POST'])
def load_vosk_model():
    """Load VOSK model on first use (lazy loading)"""
    global vosk_model

    if vosk_model is None:
        try:
            from vosk import Model

            model_path = os.path.join('static', 'models', 'vosk-model-small-en-us-0.15')

            # Check if model exists
            if not os.path.exists(model_path):
                return jsonify({
                    'status': 'error',
                    'error': f'VOSK model not found at {model_path}. Please download it first.'
                }), 404

            vosk_model = Model(model_path)

            return jsonify({
                'status': 'loaded',
                'model': 'vosk-model-small-en-us-0.15',
                'message': '✅ VOSK model ready'
            }), 200

        except ImportError:
            return jsonify({
                'status': 'error',
                'error': 'vosk package not installed. Run: pip install vosk'
            }), 500
        except Exception as e:
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500
    else:
        return jsonify({
            'status': 'already_loaded',
            'message': 'VOSK model already loaded'
        }), 200


def _process_audio_sync(audio_data, vosk_model_ref):
    """Synchronous audio processing (runs in executor)"""
    from vosk import KaldiRecognizer
    import wave
    import io

    audio_stream = io.BytesIO(audio_data)
    wf = wave.open(audio_stream, 'rb')

    # Validate audio format
    if wf.getnchannels() != 1:
        raise ValueError(f'Audio must be mono (1 channel), got {wf.getnchannels()}')
    if wf.getsampwidth() != 2:
        raise ValueError(f'Audio must be 16-bit PCM, got sample width {wf.getsampwidth()}')
    if wf.getframerate() not in [8000, 16000, 32000, 48000]:
        raise ValueError(f'Sample rate must be 8000, 16000, 32000, or 48000 Hz, got {wf.getframerate()}')

    # Create recognizer
    rec = KaldiRecognizer(vosk_model_ref, wf.getframerate())
    rec.SetWords(True)

    # Process audio
    transcribed_text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            transcribed_text += result.get('text', '') + " "

    # Get final result
    final_result = json.loads(rec.FinalResult())
    transcribed_text += final_result.get('text', '')

    # Calculate duration
    duration_seconds = wf.getnframes() / float(wf.getframerate())

    return {
        'text': transcribed_text.strip(),
        'duration_seconds': round(duration_seconds, 2),
        'sample_rate': wf.getframerate()
    }


@voice_bp.route('/transcribe', methods=['POST'])
async def transcribe_audio():
    """Transcribe audio file to text using VOSK (async)"""
    global vosk_model

    # Check if model is loaded
    if vosk_model is None:
        return jsonify({
            'error': 'VOSK model not loaded. Call /api/v1/voice/load-model first',
            'hint': 'POST to /api/v1/voice/load-model before transcribing'
        }), 400

    # Check if audio file provided
    if 'audio' not in request.files:
        return jsonify({
            'error': 'No audio file provided',
            'hint': 'Send audio file as form-data with key "audio"'
        }), 400

    audio_file = request.files['audio']

    if audio_file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    try:
        # Read audio data
        audio_data = audio_file.read()

        # Run CPU-bound transcription in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            _process_audio_sync,
            audio_data,
            vosk_model
        )

        return jsonify({
            'success': True,
            'text': result['text'],
            'duration_seconds': result['duration_seconds'],
            'sample_rate': result['sample_rate'],
            'model_used': 'vosk-model-small-en-us-0.15'
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'hint': 'Audio must be WAV format (mono, 16-bit PCM, 8-48kHz)'
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'type': type(e).__name__
        }), 500
