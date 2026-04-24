// LockedIn AI - Audio Recorder
// Handles microphone recording and audio file creation

class AudioRecorder {
  constructor(options = {}) {
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.stream = null;
    this.isRecording = false;

    // Options
    this.sampleRate = options.sampleRate || 16000;
    this.mimeType = options.mimeType || 'audio/webm';

    // Callbacks
    this.onDataAvailable = options.onDataAvailable || null;
    this.onRecordingStart = options.onRecordingStart || null;
    this.onRecordingStop = options.onRecordingStop || null;
    this.onError = options.onError || null;
  }

  async requestPermission() {
    try {
      console.log('AudioRecorder: Requesting microphone permission');

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: this.sampleRate,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      console.log('AudioRecorder: Permission granted');
      return stream;

    } catch (error) {
      console.error('AudioRecorder: Permission denied', error);
      if (this.onError) {
        this.onError(error);
      }
      throw error;
    }
  }

  async startRecording() {
    try {
      if (this.isRecording) {
        console.warn('AudioRecorder: Already recording');
        return;
      }

      // Get microphone stream
      this.stream = await this.requestPermission();

      // Create MediaRecorder
      this.mediaRecorder = new MediaRecorder(this.stream, {
        mimeType: this.mimeType,
      });

      // Reset chunks
      this.audioChunks = [];

      // Handle data available
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);

          // Call callback if provided
          if (this.onDataAvailable) {
            this.onDataAvailable(event.data);
          }
        }
      };

      // Handle stop
      this.mediaRecorder.onstop = () => {
        console.log('AudioRecorder: Recording stopped');
        this.isRecording = false;

        // Stop all tracks
        if (this.stream) {
          this.stream.getTracks().forEach(track => track.stop());
          this.stream = null;
        }

        // Call callback if provided
        if (this.onRecordingStop) {
          const audioBlob = new Blob(this.audioChunks, { type: this.mimeType });
          this.onRecordingStop(audioBlob);
        }
      };

      // Start recording
      this.mediaRecorder.start(1000); // Collect data every 1 second
      this.isRecording = true;

      console.log('AudioRecorder: Recording started');

      // Call callback if provided
      if (this.onRecordingStart) {
        this.onRecordingStart();
      }

    } catch (error) {
      console.error('AudioRecorder: Failed to start recording', error);
      if (this.onError) {
        this.onError(error);
      }
      throw error;
    }
  }

  stopRecording() {
    if (this.mediaRecorder && this.isRecording) {
      console.log('AudioRecorder: Stopping recording');
      this.mediaRecorder.stop();
    } else {
      console.warn('AudioRecorder: Not recording');
    }
  }

  getAudioBlob() {
    if (this.audioChunks.length === 0) {
      return null;
    }
    return new Blob(this.audioChunks, { type: this.mimeType });
  }

  async getAudioFile() {
    const blob = this.getAudioBlob();
    if (!blob) {
      return null;
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const fileName = `recording-${timestamp}.webm`;

    return new File([blob], fileName, { type: this.mimeType });
  }

  cancelRecording() {
    if (this.mediaRecorder && this.isRecording) {
      console.log('AudioRecorder: Cancelling recording');
      this.isRecording = false;
      this.audioChunks = [];

      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop());
        this.stream = null;
      }

      if (this.mediaRecorder.state !== 'inactive') {
        this.mediaRecorder.stop();
      }
    }
  }

  // Helper: Convert blob to base64
  static blobToBase64(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result.split(',')[1]);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  // Helper: Convert blob to array buffer
  static blobToArrayBuffer(blob) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsArrayBuffer(blob);
    });
  }
}

// Make AudioRecorder globally available
if (typeof window !== 'undefined') {
  window.AudioRecorder = AudioRecorder;
}
