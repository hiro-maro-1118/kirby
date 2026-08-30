/**
 * Admin Dashboard Controller
 */

import { StorageManager } from './storage.js';

class AdminDashboard {
  constructor() {
    this.storage = new StorageManager();
    this.currentCategory = 'general'; // general, weak, advanced, stats
    this.editingId = null;
    this.allQuestions = [];
  }

  async init() {
    await this.storage.loadAllData();
    this.refreshQuestionList();
    this.bindEvents();
    this.updateCategoryCounts();
    this.updateTypeFormFields();
  }

  refreshQuestionList() {
    this.allQuestions = this.storage.getAllQuestions();
    this.renderQuestionList();
    this.updateCategoryCounts();
    if (this.currentCategory === 'stats') {
      this.renderStats();
    }
  }

  updateCategoryCounts() {
    const all = this.storage.getAllQuestions();
    const generalCount = all.filter(q => (q.category || 'general') === 'general').length;
    const weakCount = all.filter(q => q.category === 'weak').length;
    const advancedCount = all.filter(q => q.category === 'advanced').length;

    document.getElementById('countGeneral').textContent = generalCount;
    document.getElementById('countWeak').textContent = weakCount;
    document.getElementById('countAdvanced').textContent = advancedCount;
  }

  bindEvents() {
    // 区分タブ切り替え
    document.querySelectorAll('.cat-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        const cat = e.currentTarget.getAttribute('data-category');
        this.switchCategory(cat);
      });
    });

    // 問題形式切り替え
    document.getElementById('qType').addEventListener('change', () => {
      this.updateTypeFormFields();
    });

    // フォーム送信
    document.getElementById('questionForm').addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleFormSubmit();
    });

    // 編集キャンセル
    document.getElementById('btnCancelEdit').addEventListener('click', () => {
      this.resetForm();
    });

    // フィルタ・検索
    document.getElementById('filterGrade').addEventListener('change', () => this.renderQuestionList());
    document.getElementById('filterSubject').addEventListener('change', () => this.renderQuestionList());
    document.getElementById('filterSearch').addEventListener('input', () => this.renderQuestionList());

    // JSONエクスポート
    document.getElementById('btnExportJson').addEventListener('click', () => {
      this.exportJson();
    });

    // JSONインポート
    document.getElementById('fileImportJson').addEventListener('change', (e) => {
      this.importJson(e);
    });
  }

  switchCategory(cat) {
    this.currentCategory = cat;
    document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.cat-tab[data-category="${cat}"]`)?.classList.add('active');

    const sectionQ = document.getElementById('sectionQuestionManagement');
    const sectionStats = document.getElementById('sectionStats');

    if (cat === 'stats') {
      sectionQ.classList.add('hidden');
      sectionStats.classList.remove('hidden');
      this.renderStats();
    } else {
      sectionQ.classList.remove('hidden');
      sectionStats.classList.add('hidden');
      if (document.getElementById('qCategory')) {
        document.getElementById('qCategory').value = cat;
      }

      const labels = {
        general: '📝 とりあえず作る',
        weak: '⚠️ にがてな問題',
        advanced: '🚀 1学年上の問題'
      };
      document.getElementById('currentCategoryBadge').textContent = labels[cat] || '';
      this.renderQuestionList();
    }
  }

  updateTypeFormFields() {
    const type = document.getElementById('qType').value;
    const groupPassage = document.getElementById('groupPassage');
    const groupOptions = document.getElementById('groupOptions');
    const groupChoiceAns = document.getElementById('groupChoiceAnswer');
    const groupTextAns = document.getElementById('groupTextAnswer');

    if (type === 'passage') {
      groupPassage.classList.remove('hidden');
      groupOptions.classList.remove('hidden');
      groupChoiceAns.classList.remove('hidden');
      groupTextAns.classList.add('hidden');
    } else if (type === 'choice') {
      groupPassage.classList.add('hidden');
      groupOptions.classList.remove('hidden');
      groupChoiceAns.classList.remove('hidden');
      groupTextAns.classList.add('hidden');
    } else {
      groupPassage.classList.add('hidden');
      groupOptions.classList.add('hidden');
      groupChoiceAns.classList.add('hidden');
      groupTextAns.classList.remove('hidden');
    }
  }

  handleFormSubmit() {
    const grade = parseInt(document.getElementById('qGrade').value, 10);
    const subject = document.getElementById('qSubject').value;
    const unit = document.getElementById('qUnit').value.trim() || '保護者カスタム';
    const category = document.getElementById('qCategory') ? document.getElementById('qCategory').value : this.currentCategory;
    const type = document.getElementById('qType').value;
    const passage = document.getElementById('qPassage').value.trim();
    const question = document.getElementById('qQuestion').value.trim();
    const reward = document.getElementById('qReward').value;
    const explanation = document.getElementById('qExplanation').value.trim();

    let options = [];
    let answer = null;

    if (type === 'choice' || type === 'passage') {
      options = [
        document.getElementById('opt0').value.trim(),
        document.getElementById('opt1').value.trim(),
        document.getElementById('opt2').value.trim(),
        document.getElementById('opt3').value.trim()
      ];
      if (options.some(o => !o)) {
        alert("選択肢を4つすべて入力してください。");
        return;
      }
      answer = parseInt(document.getElementById('qChoiceAnswer').value, 10);
    } else {
      answer = document.getElementById('qTextAnswer').value.trim();
      if (!answer) {
        alert("正解を入力してください。");
        return;
      }
    }

    const qData = {
      grade,
      subject,
      unit,
      type,
      category,
      passage: type === 'passage' ? passage : undefined,
      question,
      options,
      answer,
      foodReward: reward,
      explanation: explanation || "しっかり復習しよう！",
      monster: "king_dedede"
    };

    if (this.editingId) {
      this.storage.updateCustomQuestion(this.editingId, qData);
      alert("問題を更新しました！");
    } else {
      this.storage.addCustomQuestion(qData);
      alert("新しい問題を登録しました！");
    }

    this.resetForm();
    this.refreshQuestionList();
  }

  editQuestion(id) {
    const q = this.storage.customQuestions.find(item => item.id === id);
    if (!q) return;

    this.editingId = id;
    document.getElementById('formTitle').textContent = '✏️ 問題を編集';
    document.getElementById('btnSubmitForm').textContent = '💾 変更を保存する';
    document.getElementById('btnCancelEdit').classList.remove('hidden');

    document.getElementById('qGrade').value = q.grade;
    document.getElementById('qSubject').value = q.subject;
    document.getElementById('qUnit').value = q.unit || '';
    if (document.getElementById('qCategory')) {
      document.getElementById('qCategory').value = q.category || 'general';
    }
    document.getElementById('qType').value = q.type;
    document.getElementById('qQuestion').value = q.question;
    document.getElementById('qPassage').value = q.passage || '';
    document.getElementById('qReward').value = q.foodReward || 'apple';
    document.getElementById('qExplanation').value = q.explanation || '';

    this.updateTypeFormFields();

    if (q.type === 'choice' || q.type === 'passage') {
      if (q.options) {
        document.getElementById('opt0').value = q.options[0] || '';
        document.getElementById('opt1').value = q.options[1] || '';
        document.getElementById('opt2').value = q.options[2] || '';
        document.getElementById('opt3').value = q.options[3] || '';
      }
      document.getElementById('qChoiceAnswer').value = q.answer;
    } else {
      document.getElementById('qTextAnswer').value = q.answer;
    }

    document.getElementById('questionForm').scrollIntoView({ behavior: 'smooth' });
  }

  deleteQuestion(id) {
    if (confirm("この問題を削除してもよろしいですか？")) {
      this.storage.deleteCustomQuestion(id);
      if (this.editingId === id) this.resetForm();
      this.refreshQuestionList();
    }
  }

  resetForm() {
    this.editingId = null;
    document.getElementById('formTitle').textContent = '➕ 新しい問題を登録';
    document.getElementById('btnSubmitForm').textContent = '💾 この問題を保存する';
    document.getElementById('btnCancelEdit').classList.add('hidden');
    document.getElementById('questionForm').reset();
    this.updateTypeFormFields();
  }

  renderQuestionList() {
    const container = document.getElementById('questionListContainer');
    container.innerHTML = '';

    const filterGrade = document.getElementById('filterGrade').value;
    const filterSubject = document.getElementById('filterSubject').value;
    const search = document.getElementById('filterSearch').value.trim().toLowerCase();

    // 現在のタブ区分で絞り込み（カスタム問題 + デフォルト問題すべて）
    const all = this.storage.getAllQuestions();
    let list = all.filter(q => (q.category || 'general') === this.currentCategory);

    // 学年フィルタ
    if (filterGrade !== 'all') {
      list = list.filter(q => q.grade === parseInt(filterGrade, 10));
    }

    // 教科フィルタ
    if (filterSubject !== 'all') {
      list = list.filter(q => q.subject === filterSubject);
    }

    // 検索フィルタ
    if (search) {
      list = list.filter(q => 
        (q.question && q.question.toLowerCase().includes(search)) ||
        (q.unit && q.unit.toLowerCase().includes(search))
      );
    }

    if (list.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; padding: 36px 12px; color: #94a3b8;">
          <p style="font-size:14px; font-weight:600;">該当する問題がありません</p>
          <p style="font-size:12px; margin-top:4px;">左のフォームから新しい問題を登録してみましょう！</p>
        </div>
      `;
      return;
    }

    const typeLabels = { choice: '4択', fill: '穴埋め', numeric: '数字入力', passage: '長文読解' };

    list.forEach(q => {
      const isCustom = !!q.id?.startsWith('custom-');
      const card = document.createElement('div');
      card.className = 'q-item-card';

      let ansDisplay = q.answer;
      if ((q.type === 'choice' || q.type === 'passage') && q.options) {
        ansDisplay = `${q.answer + 1}. ${q.options[q.answer] || ''}`;
      }

      card.innerHTML = `
        <div class="q-item-header">
          <div class="q-tags">
            <span class="tag">小${q.grade}</span>
            <span class="tag subject">${q.subject}</span>
            <span class="tag type">${typeLabels[q.type] || q.type}</span>
            ${q.unit ? `<span class="tag">${q.unit}</span>` : ''}
            ${isCustom ? '<span class="tag" style="background:#dcfce7;color:#15803d;">自作</span>' : ''}
          </div>
          ${isCustom ? `
            <div class="q-actions">
              <button class="btn-icon edit" data-id="${q.id}">✏️ 編集</button>
              <button class="btn-icon delete" data-id="${q.id}">🗑️ 削除</button>
            </div>
          ` : '<span style="font-size:11px; color:#94a3b8;">標準問題</span>'}
        </div>
        ${q.passage ? `<div style="font-size:11px; background:#f1f5f9; padding:6px; border-radius:4px; margin-bottom:4px; color:#475569;">${q.passage}</div>` : ''}
        <div class="q-item-body">
          <strong>問:</strong> ${q.question}
        </div>
        <div class="q-item-meta">
          <span><strong>正解:</strong> ${ansDisplay}</span>
          <span><strong>解説:</strong> ${q.explanation || 'なし'}</span>
        </div>
      `;

      if (isCustom) {
        card.querySelector('.btn-icon.edit').onclick = () => this.editQuestion(q.id);
        card.querySelector('.btn-icon.delete').onclick = () => this.deleteQuestion(q.id);
      }

      container.appendChild(card);
    });
  }

  renderStats() {
    const saveData = this.storage.loadGameData();
    const p = saveData.pet || {};

    const all = this.storage.getAllQuestions();
    const weakCategoryCount = all.filter(q => q.category === 'weak').length;
    const wrongCount = (p.wrongQuestionIds || []).length;

    document.getElementById('statTotalSolved').innerHTML = `${totalSolved} <small>問</small>`;
    document.getElementById('statTotalCorrect').innerHTML = `${totalCorrect} <small>問</small>`;
    document.getElementById('statOverallAccuracy').textContent = `${accuracy}%`;
    document.getElementById('statWeakCount').innerHTML = `${weakCategoryCount} <small>問 (うちリベンジ: ${wrongCount}問)</small>`;

    const table = document.getElementById('subjectStatsTable');
    table.innerHTML = '';

    const stats = p.studyStats || {};
    const subjects = ['算数', '国語', '理科', '社会', '英語'];

    subjects.forEach(subj => {
      const sData = stats[subj] || { solved: 0, correct: 0 };
      const sAcc = sData.solved > 0 ? Math.round((sData.correct / sData.solved) * 100) : 0;

      const row = document.createElement('div');
      row.className = 'sub-stat-row';
      row.innerHTML = `
        <span class="sub-name">${subj}</span>
        <div class="sub-bar-wrap">
          <div class="sub-bar-fill" style="width: ${sAcc}%;"></div>
        </div>
        <span style="font-weight:700; width:45px; text-align:right;">${sAcc}%</span>
        <span class="sub-count">${sData.correct} / ${sData.solved} 問</span>
      `;
      table.appendChild(row);
    });
  }

  exportJson() {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.storage.customQuestions, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `kirby_custom_questions_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  }

  importJson(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const json = JSON.parse(event.target.result);
        if (Array.isArray(json)) {
          const merged = [...json, ...this.storage.customQuestions];
          // 重複ID除去
          const unique = Array.from(new Map(merged.map(item => [item.id, item])).values());
          this.storage.saveCustomQuestions(unique);
          alert(`${json.length}件の問題をインポートしました！`);
          this.refreshQuestionList();
        } else {
          alert("JSONフォーマットが配列ではありません。");
        }
      } catch (err) {
        alert("JSONファイルの読み込みに失敗しました。");
      }
    };
    reader.readAsText(file);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const admin = new AdminDashboard();
  admin.init();
});
