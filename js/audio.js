/**
 * 8-Bit Retro Sound Synthesizer using Web Audio API
 */
class SoundEngine {
  constructor() {
    this.ctx = null;
    this.enabled = true;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  toggleSound() {
    this.enabled = !this.enabled;
    return this.enabled;
  }

  playTone(freq, type = 'square', duration = 0.1, gainVal = 0.15) {
    if (!this.enabled) return;
    this.init();
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
      gain.gain.setValueAtTime(gainVal, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);

      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + duration);
    } catch (e) {
      console.warn("Audio play error", e);
    }
  }

  // ボタン押し音
  playButton() {
    this.playTone(600, 'square', 0.05, 0.1);
  }

  // キャンセル音
  playCancel() {
    this.playTone(300, 'square', 0.08, 0.1);
  }

  // 正解！ (ファンファーレ)
  playCorrect() {
    if (!this.enabled) return;
    this.init();
    const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
    notes.forEach((freq, idx) => {
      setTimeout(() => {
        this.playTone(freq, 'triangle', 0.15, 0.2);
      }, idx * 90);
    });
  }

  // 不正解 / 逃げられた音
  playWrong() {
    if (!this.enabled) return;
    this.init();
    const notes = [350, 300, 250, 200];
    notes.forEach((freq, idx) => {
      setTimeout(() => {
        this.playTone(freq, 'sawtooth', 0.12, 0.12);
      }, idx * 100);
    });
  }

  // すいこみ音 (Inhale)
  playInhale() {
    if (!this.enabled) return;
    this.init();
    try {
      const bufferSize = this.ctx.sampleRate * 0.4;
      const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        data[i] = (Math.random() * 2 - 1) * Math.sin(i / 100);
      }
      const noise = this.ctx.createBufferSource();
      noise.buffer = buffer;

      const filter = this.ctx.createBiquadFilter();
      filter.type = 'bandpass';
      filter.frequency.setValueAtTime(400, this.ctx.currentTime);
      filter.frequency.linearRampToValueAtTime(1200, this.ctx.currentTime + 0.4);

      const gain = this.ctx.createGain();
      gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.4);

      noise.connect(filter);
      filter.connect(gain);
      gain.connect(this.ctx.destination);
      noise.start();
    } catch (e) {}
  }

  // もぐもぐ・食べる音
  playEat() {
    if (!this.enabled) return;
    this.init();
    [400, 600, 500, 750].forEach((freq, i) => {
      setTimeout(() => {
        this.playTone(freq, 'triangle', 0.08, 0.18);
      }, i * 80);
    });
  }

  // なでなで・ごきげん音
  playHappy() {
    if (!this.enabled) return;
    this.init();
    [600, 800, 1000].forEach((freq, i) => {
      setTimeout(() => {
        this.playTone(freq, 'sine', 0.1, 0.15);
      }, i * 70);
    });
  }

  // 進化ファンファーレ！ (Evolution Triumph)
  playEvolution() {
    if (!this.enabled) return;
    this.init();
    const chords = [
      { f: 523.25, d: 0.15 }, // C
      { f: 659.25, d: 0.15 }, // E
      { f: 783.99, d: 0.15 }, // G
      { f: 1046.5, d: 0.15 }, // C6
      { f: 880.00, d: 0.15 }, // A5
      { f: 1046.5, d: 0.15 }, // C6
      { f: 1174.6, d: 0.25 }, // D6
      { f: 1318.5, d: 0.5 },  // E6
    ];
    chords.forEach((note, idx) => {
      setTimeout(() => {
        this.playTone(note.f, 'triangle', note.d, 0.25);
        this.playTone(note.f / 2, 'square', note.d, 0.15);
      }, idx * 130);
    });
  }
}

export const sound = new SoundEngine();
