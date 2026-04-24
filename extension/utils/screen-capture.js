// LockedIn AI - Screen Capture
// Handles screenshot capture for OCR

class ScreenCapture {
  constructor(options = {}) {
    this.onCapture = options.onCapture || null;
    this.onError = options.onError || null;
  }

  async captureActiveTab() {
    try {
      console.log('ScreenCapture: Capturing active tab');

      // Request screenshot from background script
      const response = await new Promise((resolve, reject) => {
        chrome.runtime.sendMessage(
          { action: 'capture-screen' },
          (response) => {
            if (chrome.runtime.lastError) {
              reject(chrome.runtime.lastError);
            } else {
              resolve(response);
            }
          }
        );
      });

      if (!response.success) {
        throw new Error(response.error || 'Screen capture failed');
      }

      console.log('ScreenCapture: Capture successful');

      const dataUrl = response.dataUrl;

      // Call callback if provided
      if (this.onCapture) {
        this.onCapture(dataUrl);
      }

      return dataUrl;

    } catch (error) {
      console.error('ScreenCapture: Failed to capture screen', error);
      if (this.onError) {
        this.onError(error);
      }
      throw error;
    }
  }

  async captureFullPage() {
    // Note: Full page capture would require scrolling and stitching
    // For MVP, we'll use single viewport capture
    console.warn('ScreenCapture: Full page capture not yet implemented, using viewport capture');
    return this.captureActiveTab();
  }

  // Helper: Convert data URL to Blob
  static dataUrlToBlob(dataUrl) {
    const parts = dataUrl.split(',');
    const contentType = parts[0].split(':')[1].split(';')[0];
    const raw = window.atob(parts[1]);
    const rawLength = raw.length;
    const uInt8Array = new Uint8Array(rawLength);

    for (let i = 0; i < rawLength; i++) {
      uInt8Array[i] = raw.charCodeAt(i);
    }

    return new Blob([uInt8Array], { type: contentType });
  }

  // Helper: Convert data URL to File
  static dataUrlToFile(dataUrl, fileName = 'screenshot.png') {
    const blob = ScreenCapture.dataUrlToBlob(dataUrl);
    return new File([blob], fileName, { type: 'image/png' });
  }

  // Helper: Resize image if too large
  static async resizeImage(dataUrl, maxWidth = 1920, maxHeight = 1080) {
    return new Promise((resolve, reject) => {
      const img = new Image();

      img.onload = () => {
        let width = img.width;
        let height = img.height;

        // Calculate new dimensions if image is too large
        if (width > maxWidth || height > maxHeight) {
          const ratio = Math.min(maxWidth / width, maxHeight / height);
          width = Math.floor(width * ratio);
          height = Math.floor(height * ratio);
        }

        // Create canvas and resize
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);

        const resizedDataUrl = canvas.toDataURL('image/png');
        resolve(resizedDataUrl);
      };

      img.onerror = reject;
      img.src = dataUrl;
    });
  }

  // Helper: Crop image to region
  static async cropImage(dataUrl, cropRegion) {
    return new Promise((resolve, reject) => {
      const img = new Image();

      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = cropRegion.width;
        canvas.height = cropRegion.height;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(
          img,
          cropRegion.x, cropRegion.y, cropRegion.width, cropRegion.height,
          0, 0, cropRegion.width, cropRegion.height
        );

        const croppedDataUrl = canvas.toDataURL('image/png');
        resolve(croppedDataUrl);
      };

      img.onerror = reject;
      img.src = dataUrl;
    });
  }
}

// Make ScreenCapture globally available
if (typeof window !== 'undefined') {
  window.ScreenCapture = ScreenCapture;
}
