/**
 * Storage & Data Loader Module (Enhanced for Lifecycle, Grades, and Parent Management)
 */

const STORAGE_KEY = 'kirby_pet_savedata_v2';
const CUSTOM_Q_KEY = 'kirby_custom_questions_v1';

export class StorageManager {
  constructor() {
    this.questions = [];
    this.evolutionTree = null;
    this.foods = [];
    this.customQuestions = this.loadCustomQuestions();
  }

  // 全静的データロード
  async loadAllData() {
    try {
      // 1. 進化ツリーロード
      const evoRes = await fetch('./data/evolution_tree.json');
      this.evolutionTree = await evoRes.json();

      // 2. ごはんデータロード
      const foodRes = await fetch('./data/foods.json');
      const foodJson = await foodRes.json();
      this.foods = foodJson.foods;

      // 3. 各教科・学年問題データロード
      const dataFiles = [
        'grade1.json',
        'grade2.json',
        'grade3.json',
        'grade4.json',
        'math_grade5.json',
        'japanese_grade5.json',
        'science_grade5.json',
        'social_grade5.json',
        'grade6.json',
        'english_grade5_6.json'
      ];

      this.questions = [];
      for (const file of dataFiles) {
        try {
          const res = await fetch(`./data/${file}`);
          if (res.ok) {
            const data = await res.json();
            const defaultSubj = data.subject || '算数';
            const defaultGrade = data.grade || 5;
            const defaultUnit = data.unit || '基本';

            if (Array.isArray(data.questions)) {
              for (const q of data.questions) {
                this.questions.push({
                  ...q,
                  subject: q.subject || defaultSubj,
                  unit: q.unit || defaultUnit,
                  grade: q.grade || defaultGrade,
                  category: 'general'
                });
              }
            }
          }
        } catch (e) {
          console.warn(`Could not load ${file}`, e);
        }
      }
      return true;
    } catch (err) {
      console.error("Failed to load game assets/data", err);
      return false;
    }
  }

  // デフォルトセーブデータ作成
  getDefaultSaveData() {
    const now = Date.now();
    return {
      selectedGrade: 5,
      lastAccessTime: now,
      stamina: {
        remaining: 5,
        lastResetDate: new Date(now).toISOString().slice(0, 10)
      },
      pet: {
        name: "カービィ",
        currentFormId: "baby_kirby",
        stage: 1,
        hunger: 100,    // 0-100 (まんぷく度)
        energy: 100,    // 0-100 (HP / 元気度)
        happy: 100,     // 0-100 (ごきげん度)
        poopCount: 0,   // うんちの数 (0-12)
        isSick: false,  // 病気フラグ
        sickStartTime: null, // 病気になった時刻
        isDead: false,  // 死亡フラグ
        deadTime: null, // 死亡時刻
        finalEvoTime: null, // 最終進化到達時刻
        hiddenParams: {
          fire: 0,
          slash: 0,
          spark: 0,
          ice: 0,
          magic: 0,
          baseExp: 0,
          maximCount: 0
        },
        inventory: {
          apple: 2,
          chili_curry: 0,
          sword_meat: 0,
          spark_soda: 0,
          ice_cream: 0,
          magic_candy: 0,
          star_candy: 0,
          maxim_tomato: 1
        },
        unlockedForms: ["baby_kirby"],
        totalQuestionsSolved: 0,
        correctCount: 0,
        studyStats: {
          算数: { solved: 0, correct: 0 },
          国語: { solved: 0, correct: 0 },
          理科: { solved: 0, correct: 0 },
          社会: { solved: 0, correct: 0 },
          英語: { solved: 0, correct: 0 }
        },
        wrongQuestionIds: [] // 苦手問題リベンジリスト
      }
    };
  }

  // セーブデータ取得
  loadGameData() {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return this.getDefaultSaveData();
    try {
      const data = JSON.parse(raw);
      const def = this.getDefaultSaveData();
      return {
        ...def,
        ...data,
        stamina: { ...def.stamina, ...(data.stamina || {}) },
        pet: {
          ...def.pet,
          ...data.pet,
          hiddenParams: { ...def.pet.hiddenParams, ...(data.pet?.hiddenParams || {}) },
          inventory: { ...def.pet.inventory, ...(data.pet?.inventory || {}) },
          studyStats: { ...def.pet.studyStats, ...(data.pet?.studyStats || {}) }
        }
      };
    } catch (e) {
      return this.getDefaultSaveData();
    }
  }

  // セーブ実行
  saveGameData(data) {
    data.lastAccessTime = Date.now();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }

  // --- 親用カスタム問題管理 ---
  loadCustomQuestions() {
    const raw = localStorage.getItem(CUSTOM_Q_KEY);
    if (!raw) return [];
    try {
      return JSON.parse(raw);
    } catch (e) {
      return [];
    }
  }

  saveCustomQuestions(questions) {
    this.customQuestions = questions;
    localStorage.setItem(CUSTOM_Q_KEY, JSON.stringify(questions));
  }

  addCustomQuestion(q) {
    q.id = 'custom-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
    this.customQuestions.unshift(q);
    this.saveCustomQuestions(this.customQuestions);
    return q;
  }

  updateCustomQuestion(id, updated) {
    const idx = this.customQuestions.findIndex(q => q.id === id);
    if (idx !== -1) {
      this.customQuestions[idx] = { ...this.customQuestions[idx], ...updated };
      this.saveCustomQuestions(this.customQuestions);
      return true;
    }
    return false;
  }

  deleteCustomQuestion(id) {
    this.customQuestions = this.customQuestions.filter(q => q.id !== id);
    this.saveCustomQuestions(this.customQuestions);
  }

  // 全問題プール（静的 + カスタム）
  getAllQuestions() {
    return [...this.questions, ...this.customQuestions];
  }
}
