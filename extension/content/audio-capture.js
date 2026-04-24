// LockedIn AI - Audio Capture Content Script
// Integrates audio recording with the overlay UI

class AudioCaptureManager {
  constructor(config) {
    this.config = config;
    this.recorder = null;
    this.isRecording = false;
    this.onTranscriptionCallback = null;
    this.onErrorCallback = null;
  }

  async initialize() {
    console.log('AudioCaptureManager: Initializing');

    this.recorder = new AudioRecorder({
      sampleRate: this.config.AUDIO_SAMPLE_RATE,
      onRecordingStart: () => {
        console.log('AudioCaptureManager: Recording started');
        this.isRecording = true;
      },
      onRecordingStop: async (audioBlob) => {
        console.log('AudioCaptureManager: Recording stopped', audioBlob.size, 'bytes');
        this.isRecording = false;

        // Send to backend for transcription
        if (this.config.AUTO_TRANSCRIBE) {
          await this.transcribeAudio(audioBlob);
        }
      },
      onError: (error) => {
        console.error('AudioCaptureManager: Error', error);
        if (this.onErrorCallback) {
          this.onErrorCallback(error);
        }
      },
    });
  }

  async startRecording() {
    if (!this.recorder) {
      await this.initialize();
    }

    try {
      await this.recorder.startRecording();
      return true;
    } catch (error) {
      console.error('AudioCaptureManager: Failed to start recording', error);
      if (this.onErrorCallback) {
        this.onErrorCallback(error);
      }
      return false;
    }
  }

  stopRecording() {
    if (this.recorder && this.isRecording) {
      this.recorder.stopRecording();
    }
  }

  cancelRecording() {
    if (this.recorder) {
      this.recorder.cancelRecording();
      this.isRecording = false;
    }
  }

  async transcribeAudio(audioBlob) {
    try {
      console.log('AudioCaptureManager: Transcribing audio');

      // Convert to File
      const audioFile = new File([audioBlob], 'recording.webm', {
        type: 'audio/webm',
      });

      // Create FormData
      const formData = new FormData();
      formData.append('audio', audioFile);
      formData.append('language', 'en');

      // Send to backend
      const response = await fetch(
        `${this.config.API_URL}/api/v1/audio/transcribe`,
        {
          method: 'POST',
          headers: {
            'X-API-Key': this.config.API_KEY,
          },
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(`Transcription failed: ${response.statusText}`);
      }

      const result = await response.json();
      console.log('AudioCaptureManager: Transcription result', result);

      // Call callback with transcription
      if (this.onTranscriptionCallback) {
        this.onTranscriptionCallback(result.transcription, result);
      }

      return result.transcription;

    } catch (error) {
      console.error('AudioCaptureManager: Transcription failed', error);
      if (this.onErrorCallback) {
        this.onErrorCallback(error);
      }
      throw error;
    }
  }

  onTranscription(callback) {
    this.onTranscriptionCallback = callback;
  }

  onError(callback) {
    this.onErrorCallback = callback;
  }

  isCurrentlyRecording() {
    return this.isRecording;
  }
}

// Make AudioCaptureManager globally available
if (typeof window !== 'undefined') {
  window.AudioCaptureManager = AudioCaptureManager;
}
