/**
 * Kirby Pet & Lifecycle System
 * 2-day access lifecycle, offline simulation, poops, illness, death, rebirth, and random parameters
 */

import { sound } from './audio.js';

export class KirbyPet {
  constructor(storage) {
    this.storage = storage;
    this.saveData = storage.loadGameData();
    this.pet = this.saveData.pet;
    this.currentState = 'idle'; // idle, eating, happy, sleeping, evolving, inhaling, sick, dead, walking, skill, jumping
    this.idleAction = null; // 現在のアイドルアクション名
    this.idleTimer = null;
    this.idleActionTimer = null;
    this.onStateChange = null;
    this.onEvolution = null;
    this.onRebirth = null;
    this.onDeath = null;

    // 1. オフライン時間経過の適用
    this.applyOfflineProgress();

    // 2. 定期的なライフサイクル更新（毎分）
    this.startLifeCycle();
  }

  get formInfo() {
    if (!this.storage.evolutionTree) return null;
    return this.storage.evolutionTree.evolutions.find(e => e.id === this.pet.currentFormId) || 
           this.storage.evolutionTree.evolutions[0];
  }

  get currentSpritePath() {
    if (this.pet.isDead) {
      return './assets/sprites/pet_ghost.webp';
    }
    if (this.pet.isSick) {
      return './assets/sprites/pet_sick.webp';
    }
    if (this.currentState === 'eating') {
      return './assets/sprites/pet_eating.webp';
    }
    if (this.currentState === 'inhaling') {
      return './assets/sprites/pet_inhale.webp';
    }
    const info = this.formInfo;
    if (!info) return './assets/sprites/pet_baby.webp';
    return `./assets/sprites/pet_${info.spriteKey}.webp`;
  }

  // --- オフライン時間経過シミュレーション ---
  applyOfflineProgress() {
    const now = Date.now();
    const lastAccess = this.saveData.lastAccessTime || now;
    const elapsedSec = Math.max(0, Math.floor((now - lastAccess) / 1000));

    if (elapsedSec <= 5) {
      this.save();
      return;
    }

    const elapsedHours = elapsedSec / 3600;

    // 1. うんちの増加 (4時間に1個、最大12個)
    const newPoops = Math.floor(elapsedHours / 4);
    if (newPoops > 0) {
      this.pet.poopCount = Math.min(12, (this.pet.poopCount || 0) + newPoops);
    }

    // 2. 満腹度の減少 (48時間で100%消費 -> 1時間あたり約2.08%)
    const hungerDrop = elapsedHours * (100 / 48);
    this.pet.hunger = Math.max(0, (this.pet.hunger || 100) - hungerDrop);

    // 3. HPの減少 (通常1時間あたり約2.08%、うんち1個あたり +0.1倍加速)
    // うんちが溜まっているほどHP減少が激しくなる
    const poopMultiplier = 1.0 + ((this.pet.poopCount || 0) * 0.1);
    const baseEnergyDropRate = (100 / 48); // 1時間あたり約2.08%
    const energyDrop = elapsedHours * baseEnergyDropRate * poopMultiplier;
    this.pet.energy = Math.max(0, (this.pet.energy || 100) - energyDrop);

    // 4. ごきげん度の減少 (48時間で100%)
    const happyDrop = elapsedHours * (100 / 48);
    this.pet.happy = Math.max(0, (this.pet.happy || 100) - happyDrop);

    // 5. 病気・死亡判定
    if (this.pet.energy <= 0) {
      if (!this.pet.isSick && !this.pet.isDead) {
        this.pet.isSick = true;
        this.pet.sickStartTime = lastAccess + Math.floor((100 / (baseEnergyDropRate * poopMultiplier)) * 3600 * 1000);
      }
    }

    // 病気から24時間放置で死亡
    if (this.pet.isSick && !this.pet.isDead) {
      const sickDurationSec = (now - (this.pet.sickStartTime || now)) / 1000;
      if (sickDurationSec >= 24 * 3600) {
        this.pet.isDead = true;
        this.pet.isSick = false;
        this.pet.deadTime = (this.pet.sickStartTime || now) + 24 * 3600 * 1000;
      }
    }

    // 6. 最終進化の翌日転生判定 (第4形態到達後24時間経過)
    if (this.pet.stage === 4 && this.pet.finalEvoTime && !this.pet.isDead) {
      const evoDurationHours = (now - this.pet.finalEvoTime) / (3600 * 1000);
      if (evoDurationHours >= 24) {
        this.reincarnateToBaby();
      }
    }

    this.save();
  }

  startLifeCycle() {
    // 1分ごとに減少＆うんち＆状態チェック
    setInterval(() => {
      if (this.pet.isDead) return;

      const now = Date.now();
      const elapsedMin = 1;
      const elapsedHours = elapsedMin / 60;

      // 満腹度減少
      this.pet.hunger = Math.max(0, this.pet.hunger - elapsedHours * (100 / 48));

      // HP減少（うんち倍率適用）
      const poopMultiplier = 1.0 + ((this.pet.poopCount || 0) * 0.1);
      this.pet.energy = Math.max(0, this.pet.energy - elapsedHours * (100 / 48) * poopMultiplier);

      // ごきげん減少
      this.pet.happy = Math.max(0, this.pet.happy - elapsedHours * (100 / 48));

      // 4時間ごとにうんち (確率または時間)
      if (Math.random() < (1 / 240) && this.pet.poopCount < 12) {
        this.pet.poopCount = Math.min(12, this.pet.poopCount + 1);
      }

      // 病気判定
      if (this.pet.energy <= 0 && !this.pet.isSick && !this.pet.isDead) {
        this.pet.isSick = true;
        this.pet.sickStartTime = now;
      }

      // 死亡判定 (病気で24時間経過)
      if (this.pet.isSick && !this.pet.isDead && this.pet.sickStartTime) {
        if ((now - this.pet.sickStartTime) >= 24 * 3600 * 1000) {
          this.pet.isDead = true;
          this.pet.isSick = false;
          this.pet.deadTime = now;
          if (this.onDeath) this.onDeath();
        }
      }

      // 翌日転生判定
      if (this.pet.stage === 4 && this.pet.finalEvoTime && !this.pet.isDead) {
        if ((now - this.pet.finalEvoTime) >= 24 * 3600 * 1000) {
          this.reincarnateToBaby();
        }
      }

      this.save();
      if (this.onStateChange) this.onStateChange();
    }, 60000);
  }

  save() {
    this.saveData.pet = this.pet;
    this.storage.saveGameData(this.saveData);
  }

  // --- ごはんをあげる（乱数パラメータ） ---
  feed(foodId) {
    if (this.pet.isDead) {
      if (foodId === 'maxim_tomato') {
        return this.reviveWithTomato();
      }
      return { success: false, msg: "死んでしまっています。マキシムトマトで生き返らせてください！" };
    }

    const food = this.storage.foods.find(f => f.id === foodId);
    if (!food) return { success: false, msg: "食べ物が見つかりません" };

    const count = this.pet.inventory[foodId] || 0;
    if (count <= 0) {
      return { success: false, msg: "アイテムがありません！" };
    }

    // 消費
    this.pet.inventory[foodId]--;

    // 満腹度・HP・ごきげん度上昇
    this.pet.hunger = Math.min(100, this.pet.hunger + food.hunger);
    this.pet.energy = Math.min(100, this.pet.energy + (food.hunger * 0.8));
    this.pet.happy = Math.min(100, this.pet.happy + food.happy);

    // HP回復による病気治癒
    if (this.pet.energy >= 30 && this.pet.isSick) {
      this.pet.isSick = false;
      this.pet.sickStartTime = null;
    }

    // 裏パラメータ加算（基礎値 ± 2 のランダム幅）
    for (const [paramKey, baseVal] of Object.entries(food.params)) {
      let randomVal = baseVal;
      if (typeof baseVal === 'number' && baseVal >= 5) {
        // ±2 の乱数（例: 15 -> 13..17）
        const delta = Math.floor(Math.random() * 5) - 2;
        randomVal = Math.max(1, baseVal + delta);
      }
      this.pet.hiddenParams[paramKey] = (this.pet.hiddenParams[paramKey] || 0) + randomVal;
    }

    // もぐもぐアニメーション＆SE
    this.currentState = 'eating';
    sound.playEat();
    if (this.onStateChange) this.onStateChange();

    setTimeout(() => {
      this.currentState = 'idle';
      const evoResult = this.checkEvolution();
      this.save();
      if (this.onStateChange) this.onStateChange();

      if (evoResult.evolved) {
        this.triggerEvolution(evoResult.newForm);
      }
    }, 1800);

    return {
      success: true,
      food,
      hunger: this.pet.hunger,
      happy: this.pet.happy,
      energy: this.pet.energy
    };
  }

  // --- おそうじ（うんちをすべて吸い込む） ---
  clean() {
    if (this.pet.poopCount <= 0) {
      sound.playHappy();
      return { cleaned: 0 };
    }

    const count = this.pet.poopCount;
    sound.playInhale();
    this.currentState = 'inhaling';
    this.pet.poopCount = 0;
    this.pet.happy = Math.min(100, this.pet.happy + count * 5);
    this.pet.energy = Math.min(100, this.pet.energy + 10);
    if (this.onStateChange) this.onStateChange();

    setTimeout(() => {
      this.currentState = 'idle';
      sound.playHappy();
      this.save();
      if (this.onStateChange) this.onStateChange();
    }, 1200);

    return { cleaned: count };
  }

  // なでる
  playWithPet() {
    if (this.pet.isDead) return;
    this.pet.happy = Math.min(100, this.pet.happy + 15);
    this.currentState = 'happy';
    sound.playHappy();
    if (this.onStateChange) this.onStateChange();

    setTimeout(() => {
      this.currentState = 'idle';
      this.save();
      if (this.onStateChange) this.onStateChange();
    }, 1200);
  }

  // --- アイドルアニメーションシステム ---
  startIdleAnimations() {
    this.stopIdleAnimations();
    if (this.pet.isDead) return;

    const scheduleNext = () => {
      // 5~12秒のランダム間隔で次のアクション
      const delay = 5000 + Math.random() * 7000;
      this.idleTimer = setTimeout(() => {
        if (this.pet.isDead || this.currentState === 'eating' || this.currentState === 'evolving') {
          scheduleNext();
          return;
        }
        this.performRandomAction();
        scheduleNext();
      }, delay);
    };
    scheduleNext();
  }

  stopIdleAnimations() {
    if (this.idleTimer) {
      clearTimeout(this.idleTimer);
      this.idleTimer = null;
    }
    if (this.idleActionTimer) {
      clearTimeout(this.idleActionTimer);
      this.idleActionTimer = null;
    }
  }

  getRandomAction() {
    const p = this.pet;
    const actions = [];

    // エネルギー低い時は寝やすい
    if (p.energy < 40) {
      actions.push('sleeping', 'sleeping', 'sleeping', 'idle');
    } else {
      // 元気な時のアクション候補
      actions.push('walking', 'walking', 'jumping', 'idle');

      // ごきげん高い時は技を使いやすい
      if (p.happy > 60) {
        actions.push('skill', 'skill');
      }

      // すいこみはランダムで
      actions.push('inhaling_idle');

      // たまに寝る（元気でも）
      actions.push('sleeping');
    }

    return actions[Math.floor(Math.random() * actions.length)];
  }

  performRandomAction() {
    if (this.pet.isDead || this.currentState === 'eating' || this.currentState === 'evolving') return;

    const action = this.getRandomAction();
    this.idleAction = action;

    if (action === 'idle') {
      this.currentState = 'idle';
      this.idleAction = null;
      if (this.onStateChange) this.onStateChange();
      return;
    }

    this.currentState = action;
    if (this.onStateChange) this.onStateChange();

    // アクションの効果音
    if (action === 'skill') {
      sound.playCorrect();
    } else if (action === 'inhaling_idle') {
      sound.playInhale();
    } else if (action === 'jumping') {
      sound.playButton();
    }

    // アクション持続時間
    const durations = {
      sleeping: 4000,
      walking: 3000,
      skill: 2000,
      inhaling_idle: 1500,
      jumping: 1200
    };

    const duration = durations[action] || 2000;
    this.idleActionTimer = setTimeout(() => {
      this.currentState = 'idle';
      this.idleAction = null;
      if (this.onStateChange) this.onStateChange();
    }, duration);
  }

  // --- マキシムトマトで復活 ---
  reviveWithTomato() {
    if ((this.pet.inventory.maxim_tomato || 0) <= 0) {
      return { success: false, msg: "マキシムトマトがありません！クイズで復活の儀式を行ってください。" };
    }

    this.pet.inventory.maxim_tomato--;
    this.pet.isDead = false;
    this.pet.isSick = false;
    this.pet.sickStartTime = null;
    this.pet.deadTime = null;
    this.pet.energy = 100;
    this.pet.hunger = 100;
    this.pet.happy = 100;
    this.pet.poopCount = 0;
    
    // おむつカービィに戻る
    this.pet.currentFormId = 'baby_kirby';
    this.pet.stage = 1;
    this.pet.finalEvoTime = null;

    sound.playEvolution();
    this.save();
    if (this.onStateChange) this.onStateChange();

    return { success: true, msg: "✨ マキシムトマトの奇跡で、おむつカービィとして生まれ変わりました！" };
  }

  // --- 最終進化翌日の世代交代（転生） ---
  reincarnateToBaby() {
    this.pet.currentFormId = 'baby_kirby';
    this.pet.stage = 1;
    this.pet.finalEvoTime = null;
    this.pet.energy = 100;
    this.pet.hunger = 80;
    this.pet.happy = 100;
    this.pet.poopCount = 0;
    
    // パラメータを一部リセット（新しい進化ルートを目指せるように）
    this.pet.hiddenParams = {
      fire: 0,
      slash: 0,
      spark: 0,
      ice: 0,
      magic: 0,
      baseExp: 0,
      maximCount: (this.pet.hiddenParams.maximCount || 0)
    };

    sound.playEvolution();
    this.save();
    if (this.onRebirth) this.onRebirth();
  }

  // --- 進化判定 ---
  checkEvolution() {
    if (this.pet.isDead || this.pet.isSick) return { evolved: false };
    if (!this.storage.evolutionTree) return { evolved: false };

    const currentForm = this.formInfo;
    const currentStage = currentForm ? currentForm.stage : 1;
    const nextStage = currentStage + 1;

    if (nextStage > 4) return { evolved: false };

    const candidates = this.storage.evolutionTree.evolutions.filter(e => e.stage === nextStage);
    let bestCandidate = null;

    for (const cand of candidates) {
      const cond = cand.conditions;
      let matched = true;

      if (cond.minBaseExp !== undefined) {
        if ((this.pet.hiddenParams.baseExp || 0) < cond.minBaseExp) {
          matched = false;
        }
      }

      if (cond.params) {
        for (const [pKey, minVal] of Object.entries(cond.params)) {
          if ((this.pet.hiddenParams[pKey] || 0) < minVal) {
            matched = false;
            break;
          }
        }
      }

      if (matched) {
        bestCandidate = cand;
        break;
      }
    }

    if (bestCandidate && bestCandidate.id !== this.pet.currentFormId) {
      return { evolved: true, newForm: bestCandidate };
    }

    return { evolved: false };
  }

  triggerEvolution(newForm) {
    this.currentState = 'evolving';
    sound.playEvolution();
    this.pet.currentFormId = newForm.id;
    this.pet.stage = newForm.stage;

    // 最終進化の場合、到達時刻を記録（翌日転生用）
    if (newForm.stage === 4) {
      this.pet.finalEvoTime = Date.now();
    }

    if (!this.pet.unlockedForms.includes(newForm.id)) {
      this.pet.unlockedForms.push(newForm.id);
    }
    this.save();

    if (this.onEvolution) {
      this.onEvolution(newForm);
    }

    setTimeout(() => {
      this.currentState = 'idle';
      if (this.onStateChange) this.onStateChange();
    }, 4000);
  }

  changeForm(formId) {
    if (this.pet.unlockedForms.includes(formId)) {
      this.pet.currentFormId = formId;
      const f = this.storage.evolutionTree.evolutions.find(e => e.id === formId);
      if (f) this.pet.stage = f.stage;
      this.save();
      if (this.onStateChange) this.onStateChange();
      return true;
    }
    return false;
  }
}
