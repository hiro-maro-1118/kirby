/**
 * Quiz & Inhale Battle System (5-Question Session with Post-Session Rewards & Stamina)
 */

import { sound } from './audio.js';

export class QuizEngine {
  constructor(storage, pet) {
    this.storage = storage;
    this.pet = pet;
    
    // 5問セッション状態
    this.sessionQuestions = [];
    this.sessionIndex = 0;
    this.sessionResults = [];
    this.sessionRewards = [];
    this.currentQuestion = null;
    this.currentEnemySprite = null;
    this.isRevengeMode = false;
    this.isReviveMode = false;
    this.onBattleResult = null;
  }

  // --- スタミナチェック＆日付リセット ---
  checkAndResetStamina() {
    const saveData = this.pet.saveData;
    if (!saveData.stamina) {
      saveData.stamina = { remaining: 5, lastResetDate: new Date().toISOString().slice(0, 10) };
    }

    const today = new Date().toISOString().slice(0, 10);
    if (saveData.stamina.lastResetDate !== today) {
      saveData.stamina.remaining = 5;
      saveData.stamina.lastResetDate = today;
      this.pet.save();
    }

    return saveData.stamina;
  }

  getStaminaRemaining() {
    const stamina = this.checkAndResetStamina();
    return stamina.remaining;
  }

  consumeStamina() {
    const stamina = this.checkAndResetStamina();
    if (stamina.remaining <= 0) return false;
    stamina.remaining--;
    this.pet.save();
    return true;
  }

  // 5問セッションの開始
  startSession(options = {}) {
    this.isRevengeMode = !!options.isRevenge;
    this.isReviveMode = !!options.isRevive;
    this.sessionResults = [];
    this.sessionRewards = [];
    this.sessionIndex = 0;

    // スタミナチェック（復活モードはスタミナ消費なし）
    if (!this.isReviveMode) {
      const stamina = this.checkAndResetStamina();
      if (stamina.remaining <= 0) {
        return { noStamina: true };
      }
      // スタミナ消費
      this.consumeStamina();
    }

    let pool = this.getQuestionPool(options);
    if (!pool || pool.length === 0) {
      // 問題がなかった場合はスタミナを返す
      if (!this.isReviveMode) {
        this.pet.saveData.stamina.remaining++;
        this.pet.save();
      }
      return null;
    }

    // シャッフル
    const shuffled = [...pool].sort(() => Math.random() - 0.5);
    
    // 復活モードは1問、通常は最大5問
    const count = this.isReviveMode ? 1 : Math.min(5, shuffled.length);
    this.sessionQuestions = shuffled.slice(0, count);

    this.currentQuestion = this.sessionQuestions[0];
    this.currentEnemySprite = `./assets/sprites/enemy_${this.currentQuestion.monster || 'waddle_dee'}.webp`;

    return {
      total: this.sessionQuestions.length,
      currentIndex: 0,
      question: this.currentQuestion
    };
  }

  getQuestionPool(options = {}) {
    const { grade = null, subject = null, category = null, isRevenge = false, isRevive = false } = options;
    let pool = this.storage.getAllQuestions();

    if (isRevive) return pool;

    if (isRevenge) {
      const wrongIds = this.pet.pet.wrongQuestionIds || [];
      pool = pool.filter(q => wrongIds.includes(q.id));
      return pool;
    }

    if (grade && grade !== 'all') {
      const gNum = parseInt(grade, 10);
      pool = pool.filter(q => q.grade === gNum);
    }

    if (subject && subject !== 'all') {
      pool = pool.filter(q => q.subject === subject);
    }

    if (category && category !== 'all') {
      pool = pool.filter(q => q.category === category);
    }

    return pool;
  }

  // ドロップアイテム抽選（セッション後の報酬用）
  rollDropReward() {
    const rand = Math.random() * 100;
    if (rand < 10) {
      return 'maxim_tomato'; // 10% マキシムトマト
    } else if (rand < 30) {
      return 'star_candy';   // 20% 無敵キャンディ
    } else {
      const regularPool = ['apple', 'chili_curry', 'sword_meat', 'spark_soda', 'ice_cream', 'magic_candy'];
      return regularPool[Math.floor(Math.random() * regularPool.length)];
    }
  }

  // ボーナス用レアアイテム抽選
  rollBonusReward() {
    const bonusPool = ['maxim_tomato', 'star_candy'];
    return bonusPool[Math.floor(Math.random() * bonusPool.length)];
  }

  // セッション終了後の報酬を一括計算
  calculateSessionRewards() {
    const correctCount = this.sessionResults.filter(r => r.isCorrect).length;
    const total = this.sessionQuestions.length;
    const rewards = [];

    if (this.isReviveMode) {
      // 復活モード: 正解でマキシムトマト
      if (correctCount > 0) {
        rewards.push('maxim_tomato');
      }
    } else {
      // 通常モード: 正解数に応じて報酬
      // 0問正解: なし
      // 1-2問正解: 通常アイテム1個
      // 3-4問正解: 通常アイテム2個
      // 5問正解(パーフェクト): 通常アイテム2個 + ボーナスレアアイテム1個
      let itemCount = 0;
      if (correctCount >= 1 && correctCount <= 2) {
        itemCount = 1;
      } else if (correctCount >= 3 && correctCount <= 4) {
        itemCount = 2;
      } else if (correctCount >= 5) {
        itemCount = 2;
      }

      for (let i = 0; i < itemCount; i++) {
        rewards.push(this.rollDropReward());
      }

      // パーフェクトボーナス
      if (correctCount === total && total >= 5) {
        rewards.push(this.rollBonusReward());
      }
    }

    // インベントリに追加
    for (const foodId of rewards) {
      this.pet.pet.inventory[foodId] = (this.pet.pet.inventory[foodId] || 0) + 1;
    }

    // rewardsをfoodオブジェクトに変換
    const rewardFoods = rewards.map(foodId => {
      return this.storage.foods.find(f => f.id === foodId) || { id: foodId, name: 'ごちそう', icon: '🍎' };
    });

    this.sessionRewards = rewardFoods;
    this.pet.save();

    return {
      rewards: rewardFoods,
      correctCount,
      total,
      isPerfect: correctCount === total && total >= 5
    };
  }

  // 解答判定（アイテムドロップなし、正解/不正解のみ記録）
  submitAnswer(userAnswer) {
    if (!this.currentQuestion) return null;

    const q = this.currentQuestion;
    let isCorrect = false;

    if (q.type === 'choice' || q.type === 'passage') {
      isCorrect = (parseInt(userAnswer, 10) === parseInt(q.answer, 10));
    } else if (q.type === 'fill') {
      const cleaned = String(userAnswer).trim().toLowerCase();
      const answerClean = String(q.answer).trim().toLowerCase();
      const acceptable = (q.acceptable || []).map(a => String(a).trim().toLowerCase());
      isCorrect = (cleaned === answerClean || acceptable.includes(cleaned));
    } else if (q.type === 'numeric') {
      const numVal = parseFloat(String(userAnswer).replace(/[^0-9.-]/g, ''));
      isCorrect = (numVal === parseFloat(q.answer));
    }

    // 学習統計の加算
    if (!this.pet.pet.studyStats) this.pet.pet.studyStats = {};
    const stats = this.pet.pet.studyStats[q.subject] || { solved: 0, correct: 0 };
    stats.solved++;
    this.pet.pet.studyStats[q.subject] = stats;
    this.pet.pet.totalQuestionsSolved = (this.pet.pet.totalQuestionsSolved || 0) + 1;

    if (isCorrect) {
      stats.correct++;
      this.pet.pet.correctCount = (this.pet.pet.correctCount || 0) + 1;
      sound.playCorrect();

      // リベンジ成功時に苦手リストから削除
      const wrongList = this.pet.pet.wrongQuestionIds || [];
      const idx = wrongList.indexOf(q.id);
      if (idx !== -1) {
        wrongList.splice(idx, 1);
        this.pet.pet.wrongQuestionIds = wrongList;
      }

      if (this.isReviveMode) {
        this.pet.reviveWithTomato();
      }
    } else {
      sound.playWrong();
      if (!this.pet.pet.wrongQuestionIds) this.pet.pet.wrongQuestionIds = [];
      if (!this.pet.pet.wrongQuestionIds.includes(q.id)) {
        this.pet.pet.wrongQuestionIds.push(q.id);
      }
    }

    this.pet.save();

    const isLastQuestion = (this.sessionIndex + 1 >= this.sessionQuestions.length);

    const result = {
      isCorrect,
      question: q,
      userAnswer,
      correctAnswer: this.formatAnswerDisplay(q),
      explanation: q.explanation || "しっかり見直してみよう！",
      isLastQuestion,
      sessionIndex: this.sessionIndex,
      totalSession: this.sessionQuestions.length
    };

    this.sessionResults.push(result);

    if (this.onBattleResult) {
      this.onBattleResult(result);
    }

    return result;
  }

  // 次の問題へ進む
  nextQuestion() {
    this.sessionIndex++;
    if (this.sessionIndex < this.sessionQuestions.length) {
      this.currentQuestion = this.sessionQuestions[this.sessionIndex];
      this.currentEnemySprite = `./assets/sprites/enemy_${this.currentQuestion.monster || 'waddle_dee'}.webp`;
      return {
        isFinished: false,
        question: this.currentQuestion,
        currentIndex: this.sessionIndex,
        total: this.sessionQuestions.length
      };
    } else {
      // 5問終了・報酬一括計算
      const rewardResult = this.calculateSessionRewards();
      const correctTotal = this.sessionResults.filter(r => r.isCorrect).length;
      return {
        isFinished: true,
        total: this.sessionQuestions.length,
        correctCount: correctTotal,
        rewards: rewardResult.rewards,
        isPerfect: rewardResult.isPerfect,
        results: this.sessionResults
      };
    }
  }

  formatAnswerDisplay(q) {
    if (q.type === 'choice' || q.type === 'passage') {
      return (q.options && q.options[q.answer]) ? q.options[q.answer] : q.answer;
    }
    if (q.type === 'numeric') {
      return `${q.answer} ${q.unit || ''}`;
    }
    return q.answer;
  }
}
