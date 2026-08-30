/**
 * Main Application Controller (5-Question Test Sessions & Clean Hidden Params)
 */

import { StorageManager } from './storage.js';
import { KirbyPet } from './pet.js';
import { QuizEngine } from './quiz.js';
import { sound } from './audio.js';

class KirbyApp {
  constructor() {
    this.storage = new StorageManager();
    this.pet = null;
    this.quiz = null;
    this.currentView = 'home';
    // メニューサイクル（親用管理は admin.html に分離したため4画面に整理）
    this.menuCycle = ['home', 'studyMenu', 'food', 'zukan'];
    this.menuIndex = 0;
  }

  async init() {
    const success = await this.storage.loadAllData();
    if (!success) {
      alert("データの読み込みに失敗しました。");
    }

    this.pet = new KirbyPet(this.storage);
    this.quiz = new QuizEngine(this.storage, this.pet);

    this.pet.onStateChange = () => this.updateUI();
    this.pet.onEvolution = (form) => this.showEvolutionModal(form);
    this.pet.onRebirth = () => {
      alert("🌟 最終進化から1日が経過し、新たな世代の「おむつカービィ」に生まれ変わりました！");
      this.updateUI();
    };
    this.pet.onDeath = () => {
      this.showReviveModal();
    };

    this.bindEvents();

    const savedGrade = this.pet.saveData.selectedGrade || 5;
    document.getElementById('selectGrade').value = savedGrade;
    this.updateSubjectButtonsByGrade(savedGrade);

    this.switchView('home');
    this.updateUI();

    if (this.pet.pet.isDead) {
      this.showReviveModal();
    }
  }

  // 画面切り替え
  switchView(viewName) {
    this.currentView = viewName;
    const views = {
      home: document.getElementById('viewHome'),
      studyMenu: document.getElementById('viewStudyMenu'),
      battle: document.getElementById('viewBattle'),
      food: document.getElementById('viewFood'),
      zukan: document.getElementById('viewZukan')
    };

    for (const [key, el] of Object.entries(views)) {
      if (el) {
        if (key === viewName) {
          el.classList.remove('hidden');
        } else {
          el.classList.add('hidden');
        }
      }
    }

    if (viewName === 'food') this.renderFoodList();
    if (viewName === 'zukan') this.renderZukan();
    if (viewName === 'studyMenu') this.renderStudyMenu();
    if (viewName === 'home') {
      this.renderPoops();
      this.pet.startIdleAnimations();
    } else {
      this.pet.stopIdleAnimations();
    }

    this.updateUI();
  }

  // UI更新
  updateUI() {
    if (!this.pet) return;

    const p = this.pet.pet;
    document.getElementById('statHunger').textContent = `🍖 ${Math.round(p.hunger)}%`;
    document.getElementById('statEnergy').textContent = `💖 ${Math.round(p.energy)}%`;
    document.getElementById('statPoop').textContent = `💩 ${p.poopCount || 0}`;

    // スタミナ表示
    const staminaRemaining = this.quiz ? this.quiz.getStaminaRemaining() : 5;
    document.getElementById('statStamina').textContent = `⚡ ${staminaRemaining}/5`;
    
    const form = this.pet.formInfo;
    let formName = form ? form.name : "カービィ";
    if (p.isDead) formName = "おばけカービィ (死亡)";
    else if (p.isSick) formName = "びょうきカービィ";
    document.getElementById('statFormName').textContent = formName;

    const petImg = document.getElementById('petImg');
    petImg.src = this.pet.currentSpritePath;

    const bubble = document.getElementById('petSpeechBubble');
    if (p.isDead) {
      bubble.textContent = 'うらめしや〜…トマトを…👻';
    } else if (p.isSick) {
      bubble.textContent = 'うぅ…きもちわるいぽよ…🤒';
    } else if (p.poopCount >= 4) {
      bubble.textContent = 'うんちがいっぱいでくさいぽよ〜！🧹';
    } else if (this.pet.currentState === 'eating') {
      bubble.textContent = 'もぐもぐ…おいしいぽよ！😋';
    } else if (this.pet.currentState === 'happy') {
      bubble.textContent = 'わーい！うれしいぽよ！💖';
    } else if (p.hunger < 30) {
      bubble.textContent = 'おなかすいたぽよ〜ごはんちょうだい🍙';
    } else if (p.energy < 40) {
      bubble.textContent = 'つかれたぽよ…ねむい…💤';
    } else {
      bubble.textContent = `ぽよ！${form ? form.title : '元気いっぱい！'}`;
    }

    document.getElementById('badgeStage').textContent = p.isDead ? '💀 死亡状態' : (p.isSick ? '🤒 病気中' : `第${p.stage}形態: ${form ? form.name : ''}`);

    if (this.currentView === 'home') {
      this.renderPoops();
      this.updatePetAnimation();
    }
  }

  // カービィのアニメーション状態をDOMに反映
  updatePetAnimation() {
    const container = document.getElementById('petMainSprite');
    const sleepZzz = document.getElementById('petSleepZzz');
    const starEffect = document.getElementById('petStarEffect');
    const bubble = document.getElementById('petSpeechBubble');

    if (!container) return;

    // 全アニメーションクラスをリセット
    const animClasses = ['pet-sleeping', 'pet-walking', 'pet-skill', 'pet-inhaling-idle', 'pet-jumping'];
    animClasses.forEach(cls => container.classList.remove(cls));
    sleepZzz.classList.add('hidden');
    starEffect.classList.add('hidden');

    const state = this.pet.currentState;

    switch (state) {
      case 'sleeping':
        container.classList.add('pet-sleeping');
        sleepZzz.classList.remove('hidden');
        bubble.textContent = 'すやすや…ぐぅ…💤';
        break;
      case 'walking':
        container.classList.add('pet-walking');
        bubble.textContent = 'てくてく〜♪🚶';
        break;
      case 'skill':
        container.classList.add('pet-skill');
        starEffect.classList.remove('hidden');
        bubble.textContent = 'スターショット！⭐✨';
        break;
      case 'inhaling_idle':
        container.classList.add('pet-inhaling-idle');
        bubble.textContent = 'すいこみ〜！🌀';
        break;
      case 'jumping':
        container.classList.add('pet-jumping');
        bubble.textContent = 'ぴょーん！🎵';
        break;
    }
  }

  renderPoops() {
    const layer = document.getElementById('poopLayer');
    layer.innerHTML = '';
    const count = this.pet.pet.poopCount || 0;

    const positions = [
      { top: 20, left: 15 },
      { top: 30, left: 75 },
      { top: 65, left: 20 },
      { top: 70, left: 70 },
      { top: 15, left: 45 },
      { top: 75, left: 45 },
      { top: 45, left: 10 },
      { top: 45, left: 80 },
      { top: 25, left: 30 },
      { top: 25, left: 60 },
      { top: 60, left: 35 },
      { top: 60, left: 58 },
    ];

    for (let i = 0; i < Math.min(count, 12); i++) {
      const pos = positions[i];
      const img = document.createElement('img');
      img.src = './assets/sprites/poop.webp';
      img.className = 'poop-item';
      img.style.top = `${pos.top}%`;
      img.style.left = `${pos.left}%`;
      img.title = 'クリックしておそうじ！';
      img.onclick = (e) => {
        e.stopPropagation();
        this.pet.clean();
      };
      layer.appendChild(img);
    }
  }

  bindEvents() {
    // Aボタン
    document.getElementById('btnA').addEventListener('click', () => {
      sound.playButton();
      this.handleButtonA();
    });

    // Bボタン
    document.getElementById('btnB').addEventListener('click', () => {
      sound.playCancel();
      this.handleButtonB();
    });

    // Cボタン
    document.getElementById('btnC').addEventListener('click', () => {
      sound.playButton();
      this.handleButtonC();
    });

    window.addEventListener('keydown', (e) => {
      if (e.key === 'z' || e.key === 'Z') document.getElementById('btnA').click();
      if (e.key === 'x' || e.key === 'X') document.getElementById('btnB').click();
      if (e.key === 'c' || e.key === 'C') document.getElementById('btnC').click();
    });

    document.getElementById('btnHomeClean').addEventListener('click', () => this.pet.clean());
    document.getElementById('btnHomeFeed').addEventListener('click', () => this.switchView('food'));
    document.getElementById('btnHomeStudy').addEventListener('click', () => this.switchView('studyMenu'));

    document.getElementById('petMainSprite').addEventListener('click', () => {
      if (this.pet.pet.isDead) {
        this.showReviveModal();
      } else {
        this.pet.playWithPet();
      }
    });

    document.getElementById('selectGrade').addEventListener('change', (e) => {
      const g = e.target.value;
      this.pet.saveData.selectedGrade = g;
      this.pet.save();
      this.updateSubjectButtonsByGrade(g);
    });

    document.querySelectorAll('#studySubjectGrid .choice-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const subj = e.currentTarget.getAttribute('data-subject');
        if (subj) {
          const grade = document.getElementById('selectGrade').value;
          this.start5QuestionSession({ subject: subj, grade: grade });
        }
      });
    });

    document.getElementById('btnWeakCategory')?.addEventListener('click', () => {
      const grade = document.getElementById('selectGrade').value;
      this.start5QuestionSession({ category: 'weak', grade: grade });
    });

    document.getElementById('btnRevengeMode').addEventListener('click', () => {
      this.start5QuestionSession({ isRevenge: true });
    });

    // 各問の結果ダイアログ「つぎへ」
    document.getElementById('btnResultNext').addEventListener('click', () => {
      this.proceedToNextQuestion();
    });

    // 総合リザルト画面「お部屋にもどる」
    document.getElementById('btnSessionFinish').addEventListener('click', () => {
      document.getElementById('sessionResultDialog').classList.add('hidden');
      this.switchView('home');
    });

    // 進化オーバーレイ
    document.getElementById('evoOverlay').addEventListener('click', () => {
      document.getElementById('evoOverlay').classList.add('hidden');
    });

    // 復活モーダル
    document.getElementById('btnReviveUseTomato').addEventListener('click', () => {
      const res = this.pet.reviveWithTomato();
      alert(res.msg);
      if (res.success) {
        document.getElementById('reviveModal').classList.add('hidden');
        this.updateUI();
      }
    });

    document.getElementById('btnReviveQuiz').addEventListener('click', () => {
      document.getElementById('reviveModal').classList.add('hidden');
      this.start5QuestionSession({ isRevive: true });
    });
  }

  updateSubjectButtonsByGrade(grade) {
    const btnEng = document.getElementById('btnSubjEng');
    const gNum = parseInt(grade, 10);
    if (grade === 'all' || gNum >= 5) {
      btnEng.style.display = 'block';
    } else {
      btnEng.style.display = 'none';
    }
  }

  handleButtonA() {
    if (this.pet.pet.isDead) {
      this.showReviveModal();
      return;
    }

    // 総合リザルト画面が出ている場合
    const sessionDialog = document.getElementById('sessionResultDialog');
    if (!sessionDialog.classList.contains('hidden')) {
      document.getElementById('btnSessionFinish').click();
      return;
    }

    // 各問結果ダイアログが出ている場合
    const resDialog = document.getElementById('resultDialog');
    if (!resDialog.classList.contains('hidden')) {
      this.proceedToNextQuestion();
      return;
    }

    if (this.currentView === 'home') {
      if (this.pet.pet.poopCount > 0) {
        this.pet.clean();
      } else {
        this.switchView('studyMenu');
      }
    } else if (this.currentView === 'food') {
      const firstFood = this.storage.foods.find(f => (this.pet.pet.inventory[f.id] || 0) > 0);
      if (firstFood) {
        this.pet.feed(firstFood.id);
        this.renderFoodList();
      }
    }
  }

  handleButtonB() {
    if (this.currentView === 'battle') {
      this.switchView('studyMenu');
    } else {
      this.switchView('home');
      this.menuIndex = 0;
    }
  }

  handleButtonC() {
    this.menuIndex = (this.menuIndex + 1) % this.menuCycle.length;
    this.switchView(this.menuCycle[this.menuIndex]);
  }

  renderStudyMenu() {
    const wrongCount = (this.pet.pet.wrongQuestionIds || []).length;
    document.getElementById('revengeCount').textContent = wrongCount;
  }

  // --- 5問連続テストセッションの開始 ---
  start5QuestionSession(options = {}) {
    const session = this.quiz.startSession(options);

    // スタミナ不足
    if (session && session.noStamina) {
      alert("⚡ 今日のテストはもう全部解いちゃったぽよ！\nまた明日あそびにきてね！");
      this.updateUI();
      return;
    }

    if (!session) {
      alert(options.isRevenge ? "にがてな問題はありません！" : "該当する問題がありません。");
      return;
    }

    this.switchView('battle');
    document.getElementById('sessionResultDialog').classList.add('hidden');
    this.renderCurrentBattleQuestion(session.question, session.currentIndex, session.total);
    this.updateUI(); // スタミナ表示更新
  }

  // 現在の問題の描画
  renderCurrentBattleQuestion(q, currentIndex, total) {
    document.getElementById('battleProgressBadge').textContent = `第 ${currentIndex + 1} / ${total} 問`;
    document.getElementById('battleSubjectUnit').textContent = `[小${q.grade || 5}] ${q.subject}`;
    const typeNames = { choice: '4択', fill: '穴埋め', numeric: '数字入力', passage: '長文読解' };
    document.getElementById('battleQType').textContent = typeNames[q.type] || 'クイズ';

    document.getElementById('battlePetImg').src = this.pet.currentSpritePath;
    document.getElementById('battleEnemyImg').src = `./assets/sprites/enemy_${q.monster || 'waddle_dee'}.webp`;
    document.getElementById('battleEnemyImg').style.transform = 'none';
    document.getElementById('battleEnemyImg').style.opacity = '1';
    document.getElementById('battleInhaleWind').style.display = 'none';
    document.getElementById('resultDialog').classList.add('hidden');

    const passageEl = document.getElementById('battlePassage');
    if (q.passage) {
      passageEl.textContent = q.passage;
      passageEl.classList.remove('hidden');
    } else {
      passageEl.classList.add('hidden');
    }

    document.getElementById('battleQuestionText').textContent = q.question;

    const area = document.getElementById('answersArea');
    area.innerHTML = '';

    if (q.type === 'choice' || q.type === 'passage') {
      const grid = document.createElement('div');
      grid.className = 'choice-grid';
      (q.options || []).forEach((opt, idx) => {
        const btn = document.createElement('button');
        btn.className = 'choice-btn';
        btn.textContent = `${idx + 1}. ${opt}`;
        btn.onclick = () => this.handleQuizAnswer(idx);
        grid.appendChild(btn);
      });
      area.appendChild(grid);
    } else if (q.type === 'fill') {
      const form = document.createElement('div');
      form.className = 'input-form-area';
      form.innerHTML = `
        <input type="text" class="quiz-input" id="quizInputFill" placeholder="答えを入力..." autofocus>
        <button class="quiz-submit-btn" id="btnSubmitFill">決定</button>
      `;
      area.appendChild(form);
      const input = form.querySelector('#quizInputFill');
      const subBtn = form.querySelector('#btnSubmitFill');
      subBtn.onclick = () => this.handleQuizAnswer(input.value);
      input.onkeydown = (e) => { if (e.key === 'Enter') subBtn.click(); };
      setTimeout(() => input.focus(), 100);
    } else if (q.type === 'numeric') {
      const wrap = document.createElement('div');
      wrap.innerHTML = `
        <div class="input-form-area">
          <input type="number" class="quiz-input" id="quizInputNum" placeholder="数字を入力...">
          <button class="quiz-submit-btn" id="btnSubmitNum">決定</button>
        </div>
        <div class="numpad-grid">
          ${[1,2,3,4,5,6,7,8,9,0,'.','BS'].map(n => `<button class="numpad-btn" data-val="${n}">${n}</button>`).join('')}
        </div>
      `;
      area.appendChild(wrap);
      const input = wrap.querySelector('#quizInputNum');
      const subBtn = wrap.querySelector('#btnSubmitNum');
      subBtn.onclick = () => this.handleQuizAnswer(input.value);
      input.onkeydown = (e) => { if (e.key === 'Enter') subBtn.click(); };

      wrap.querySelectorAll('.numpad-btn').forEach(btn => {
        btn.onclick = () => {
          const val = btn.getAttribute('data-val');
          if (val === 'BS') {
            input.value = input.value.slice(0, -1);
          } else {
            input.value += val;
          }
        };
      });
    }
  }

  handleQuizAnswer(answer) {
    const res = this.quiz.submitAnswer(answer);
    if (!res) return;

    if (res.isCorrect) {
      sound.playInhale();
      document.getElementById('battlePetImg').src = './assets/sprites/pet_inhale.webp';
      document.getElementById('battleInhaleWind').style.display = 'block';

      const enemy = document.getElementById('battleEnemyImg');
      enemy.style.transition = 'all 0.6s ease-in';
      enemy.style.transform = 'translateX(-70px) scale(0.2)';
      enemy.style.opacity = '0';

      setTimeout(() => {
        this.showQuizResultDialog(res);
      }, 700);
    } else {
      this.showQuizResultDialog(res);
    }
  }

  showQuizResultDialog(res) {
    const dialog = document.getElementById('resultDialog');
    const title = document.getElementById('resultTitle');
    const reward = document.getElementById('resultReward');
    const exp = document.getElementById('resultExplanation');
    const btnNext = document.getElementById('btnResultNext');

    dialog.classList.remove('hidden');

    if (res.isCorrect) {
      title.textContent = '🌟 大正解！すいこみ成功！';
      title.className = 'result-title correct';
      reward.textContent = '✨ やったね！すごいぽよ！';
      reward.style.display = 'block';
    } else {
      title.textContent = '💨 ざんねん！にげられた…';
      title.className = 'result-title wrong';
      reward.textContent = `正解は: 「${res.correctAnswer}」`;
      reward.style.display = 'block';
    }

    exp.innerHTML = `<strong>【解説】</strong><br>${res.explanation}`;
    btnNext.textContent = res.isLastQuestion ? '総合リザルトを見る！ [A]' : 'つぎの問題へ！ [A]';
  }

  proceedToNextQuestion() {
    document.getElementById('resultDialog').classList.add('hidden');
    const next = this.quiz.nextQuestion();

    if (next.isFinished) {
      // 5問終了・総合リザルト画面表示
      this.showSessionResult(next);
    } else {
      // 次の問題へ
      this.renderCurrentBattleQuestion(next.question, next.currentIndex, next.total);
    }
  }

  // 総合リザルト画面
  showSessionResult(sessionSummary) {
    const dialog = document.getElementById('sessionResultDialog');
    const scoreText = document.getElementById('sessionScoreText');
    const title = document.getElementById('sessionResultTitle');
    const list = document.getElementById('sessionRewardsList');

    dialog.classList.remove('hidden');

    const total = sessionSummary.total;
    const correct = sessionSummary.correctCount;
    scoreText.textContent = `${total}問中 ${correct}問 正解！`;

    if (correct === total) {
      title.textContent = '👑 パーフェクト！全問大正解！';
      sound.playEvolution();
    } else if (correct >= Math.ceil(total / 2)) {
      title.textContent = '🎉 よくがんばったぽよ！';
      sound.playCorrect();
    } else {
      title.textContent = '💪 つぎはもっとがんばろう！';
      sound.playHappy();
    }

    list.innerHTML = '';

    // パーフェクトボーナス表示
    if (sessionSummary.isPerfect) {
      const bonusBadge = document.createElement('div');
      bonusBadge.className = 'perfect-bonus-badge';
      bonusBadge.textContent = '🌟 パーフェクトボーナス！レアアイテムゲット！';
      list.parentElement.insertBefore(bonusBadge, list);
    }

    if (sessionSummary.rewards.length === 0) {
      list.innerHTML = '<span style="font-size:11px; color:#777;">今回はごちそうを獲得できませんでした</span>';
    } else {
      sessionSummary.rewards.forEach(r => {
        const chip = document.createElement('div');
        chip.className = 'reward-item-chip';
        chip.innerHTML = `${r.icon} ${r.name}`;
        list.appendChild(chip);
      });
    }
  }

  // ごちそう一覧（裏パラメータ数値非表示）
  renderFoodList() {
    const list = document.getElementById('foodList');
    list.innerHTML = '';

    this.storage.foods.forEach(food => {
      const count = this.pet.pet.inventory[food.id] || 0;
      const card = document.createElement('div');
      card.className = 'food-card';
      card.innerHTML = `
        <div class="food-card-header">
          <span>${food.icon} ${food.name}</span>
          <span class="food-count">x${count}</span>
        </div>
        <div style="font-size:10px; color:#555; margin-top:2px; line-height:1.2;">
          ${food.description}
        </div>
      `;
      card.onclick = () => {
        if (count > 0) {
          const res = this.pet.feed(food.id);
          if (res.success) {
            this.renderFoodList();
          } else {
            alert(res.msg);
          }
        } else {
          sound.playCancel();
          alert(`「${food.name}」を持っていません。5問テストを解いて手に入れよう！`);
        }
      };
      list.appendChild(card);
    });
  }

  // 図鑑画面（裏パラメータ数値非表示）
  renderZukan() {
    const grid = document.getElementById('zukanGrid');
    grid.innerHTML = '';
    const evolutions = this.storage.evolutionTree.evolutions;

    const titleEl = document.getElementById('zukanSelectedTitle');
    const descEl = document.getElementById('zukanSelectedDesc');

    evolutions.forEach(evo => {
      const isUnlocked = this.pet.pet.unlockedForms.includes(evo.id);
      const item = document.createElement('div');
      item.className = `zukan-item ${isUnlocked ? '' : 'locked'}`;
      item.innerHTML = `
        <img src="./assets/sprites/pet_${evo.spriteKey}.webp" alt="${evo.name}">
        <span>${isUnlocked ? evo.name : '???'}</span>
      `;
      if (isUnlocked) {
        item.onclick = () => {
          titleEl.textContent = `【${evo.name}】 ${evo.title}`;
          descEl.textContent = evo.description;
          this.pet.changeForm(evo.id);
          sound.playButton();
        };
      }
      grid.appendChild(item);
    });
  }

  showEvolutionModal(form) {
    const modal = document.getElementById('evoOverlay');
    const sprite = document.getElementById('evoSprite');
    const name = document.getElementById('evoName');

    sprite.src = `./assets/sprites/pet_${form.spriteKey}.webp`;
    name.textContent = `${form.name}（${form.title}）`;
    modal.classList.remove('hidden');

    setTimeout(() => {
      modal.classList.add('hidden');
    }, 4500);
  }

  showReviveModal() {
    document.getElementById('reviveModal').classList.remove('hidden');
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const app = new KirbyApp();
  app.init();
});
