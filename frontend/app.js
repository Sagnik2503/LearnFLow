/* ═══════════════════════════════════════════════════════
   LearnFlow — Frontend Application
   ═══════════════════════════════════════════════════════ */

const API_BASE = window.location.origin;

// ── State ──────────────────────────────────────────
const state = {
  topic: '',
  email: '',
  name: '',
  trackId: null,
  syllabus: [],
  totalDays: 0,
  currentView: 'hero',
};


// ═══════════════════════════════════════════════════════
//  PARTICLES — Canvas animated background
// ═══════════════════════════════════════════════════════
function initParticles() {
  const canvas = document.getElementById('particles-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let particles = [];
  const PARTICLE_COUNT = 60;

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  function createParticle() {
    return {
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      radius: Math.random() * 1.5 + 0.5,
      opacity: Math.random() * 0.4 + 0.1,
    };
  }

  function init() {
    resize();
    particles = Array.from({ length: PARTICLE_COUNT }, createParticle);
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (const p of particles) {
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
      if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(139, 92, 246, ${p.opacity})`;
      ctx.fill();
    }

    // Draw connecting lines between nearby particles
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(139, 92, 246, ${0.06 * (1 - dist / 120)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(draw);
  }

  window.addEventListener('resize', resize);
  init();
  draw();
}


// ═══════════════════════════════════════════════════════
//  VIEW ROUTER
// ═══════════════════════════════════════════════════════
function showView(viewId) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));

  const target = document.getElementById(viewId);
  if (target) {
    // Small delay for CSS transition
    requestAnimationFrame(() => {
      target.classList.add('active');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  state.currentView = viewId.replace('-view', '');
}


// ═══════════════════════════════════════════════════════
//  TOAST NOTIFICATIONS
// ═══════════════════════════════════════════════════════
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  const icons = { error: '✕', success: '✓', info: 'ℹ' };
  toast.innerHTML = `<span>${icons[type] || 'ℹ'}</span> ${message}`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('exit');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}


// ═══════════════════════════════════════════════════════
//  LOADING ANIMATION
// ═══════════════════════════════════════════════════════
function startLoadingAnimation(topic) {
  document.getElementById('loading-topic-label').textContent =
    `Designing a syllabus for "${topic}"`;

  const steps = ['step-analyze', 'step-structure', 'step-generate', 'step-save'];

  // Reset all steps
  steps.forEach(id => {
    const el = document.getElementById(id);
    el.classList.remove('active', 'done');
  });
  document.getElementById(steps[0]).classList.add('active');

  let current = 0;
  const interval = setInterval(() => {
    if (current < steps.length) {
      document.getElementById(steps[current]).classList.remove('active');
      document.getElementById(steps[current]).classList.add('done');
      document.getElementById(steps[current]).querySelector('.step-icon').textContent = '✓';
    }
    current++;
    if (current < steps.length) {
      document.getElementById(steps[current]).classList.add('active');
    } else {
      clearInterval(interval);
    }
  }, 2500);

  return interval;
}


// ═══════════════════════════════════════════════════════
//  MARKDOWN RENDERER (lightweight)
// ═══════════════════════════════════════════════════════
function renderMarkdown(md) {
  if (!md) return '<p>No content available.</p>';

  let html = md
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

    .replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) =>
      `<pre><code class="language-${lang}">${code.trim()}</code></pre>`
    )

    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')

    .replace(/^---$/gm, '<hr />')
    .replace(/^\*\*\*$/gm, '<hr />')

    .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')

    .replace(/`([^`]+)`/g, '<code>$1</code>')

    .replace(/^&gt; \*\*(.+?):\*\* (.+)$/gm, '<blockquote class="example-block"><span class="block-label">$1:</span> $2</blockquote>')
    .replace(/^&gt; (.+)$/gm, '<blockquote><p>$1</p></blockquote>')

    .replace(/^[-*] (.+)$/gm, '<li>$1</li>')

    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')

    .replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener" class="bare-url">$1</a>')

    .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" style="max-width:100%;border-radius:12px;margin:1rem 0;" />')

    .replace(/^(?!<[a-z/])(.*\S.*)$/gm, '<p>$1</p>');

  html = html.replace(/(<li>.*?<\/li>\s*)+/g, match => `<ul>${match}</ul>`);

  html = html.replace(/<\/blockquote>\s*<blockquote>/g, '');

  html = html.replace(/<p><(h[123]|hr|ul|pre|blockquote)/g, '<$1');
  html = html.replace(/<\/(h[123]|ul|pre|blockquote)><\/p>/g, '</$1>');

  return html;
}


// ═══════════════════════════════════════════════════════
//  SHOW NEWSLETTER SKELETON
// ═══════════════════════════════════════════════════════
function showNewsletterSkeleton() {
  const body = document.getElementById('newsletter-body');
  body.innerHTML = `
    <div class="newsletter-skeleton">
      <div class="skeleton-line heading"></div>
      <div class="skeleton-line medium"></div>
      <div class="skeleton-line"></div>
      <div class="skeleton-line"></div>
      <div class="skeleton-line short"></div>
      <div style="height: 20px;"></div>
      <div class="skeleton-line heading" style="width:50%;"></div>
      <div class="skeleton-line"></div>
      <div class="skeleton-line medium"></div>
      <div class="skeleton-line"></div>
      <div class="skeleton-line short"></div>
      <div style="height: 20px;"></div>
      <div class="skeleton-line heading" style="width:60%;"></div>
      <div class="skeleton-line"></div>
      <div class="skeleton-line"></div>
      <div class="skeleton-line medium"></div>
      <div class="skeleton-line short"></div>
    </div>
  `;
}


// ═══════════════════════════════════════════════════════
//  RENDER SYLLABUS
// ═══════════════════════════════════════════════════════
function renderSyllabus(data) {
  state.syllabus = data.syllabus;
  state.trackId = data.track_id;
  state.totalDays = data.total_days;

  // Update header
  document.getElementById('syllabus-topic-badge').textContent = data.topic.toUpperCase();
  document.getElementById('syllabus-title').textContent = `Your ${data.total_days}-Day Learning Path`;
  document.getElementById('syllabus-days-count').textContent = data.total_days;
  document.getElementById('syllabus-user-email').textContent = state.email || 'your inbox';

  // Build timeline
  const timeline = document.getElementById('syllabus-timeline');
  timeline.innerHTML = '';

  data.syllabus.forEach((item, i) => {
    const card = document.createElement('div');
    card.className = 'timeline-card';
    card.style.animationDelay = `${i * 0.1}s`;

    const conceptsHtml = item.concepts
      .map(c => `<span class="concept-tag">${c}</span>`)
      .join('');

    const descriptionHtml = item.description
      ? `<p class="day-description">${item.description}</p>`
      : '';

    card.innerHTML = `
      <div class="day-card" data-day="${item.day}" data-track="${data.track_id}" id="day-card-${item.day}">
        <div class="day-card-header">
          <span class="day-number">Day ${item.day}</span>
          <span class="day-arrow">→</span>
        </div>
        <h3 class="day-title">${item.title}</h3>
        ${descriptionHtml}
        <div class="day-concepts">${conceptsHtml}</div>
      </div>
    `;

    // Click handler for each day card
    card.querySelector('.day-card').addEventListener('click', () => {
      openNewsletter(data.track_id, item.day, item.title);
    });

    timeline.appendChild(card);
  });

  showView('syllabus-view');
}


// ═══════════════════════════════════════════════════════
//  OPEN NEWSLETTER
// ═══════════════════════════════════════════════════════
async function openNewsletter(trackId, day, title) {
  showView('newsletter-view');
  showNewsletterSkeleton();

  try {
    const res = await fetch(`${API_BASE}/api/newsletter/${trackId}/${day}`);

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to load newsletter');
    }

    const data = await res.json();
    const body = document.getElementById('newsletter-body');
    body.innerHTML = renderMarkdown(data.content);

    showToast(`Day ${day} newsletter loaded`, 'success');

  } catch (err) {
    console.error('Newsletter load failed:', err);
    const body = document.getElementById('newsletter-body');
    body.innerHTML = `
      <h1>Day ${day}: ${title}</h1>
      <p style="color:var(--text-muted); margin-top:1rem;">
        Failed to generate the newsletter. The AI engine may still be processing this content.
      </p>
      <p style="color:var(--text-muted); font-size:0.9rem; margin-top:0.5rem;">
        Error: ${err.message}
      </p>
    `;
    showToast(err.message, 'error');
  }
}


// ═══════════════════════════════════════════════════════
//  FORM SUBMIT — Generate Syllabus
// ═══════════════════════════════════════════════════════
async function handleSubmit(e) {
  e.preventDefault();

  const topicInput = document.getElementById('topic-input');
  const emailInput = document.getElementById('email-input');
  const nameInput = document.getElementById('name-input');
  const btn = document.getElementById('generate-btn');
  const btnText = document.getElementById('btn-text');
  const btnShimmer = document.getElementById('btn-shimmer');

  const topic = topicInput.value.trim();
  const email = emailInput.value.trim();

  if (!topic) {
    showToast('Please enter a topic you want to learn.', 'error');
    topicInput.focus();
    return;
  }
  if (!email) {
    showToast('Please enter your email for daily newsletters.', 'error');
    emailInput.focus();
    return;
  }

  state.topic = topic;
  state.email = email;
  state.name = nameInput.value.trim();

  // Show loading view
  showView('loading-view');
  const loadingInterval = startLoadingAnimation(topic);

  // Disable button
  btn.disabled = true;
  btnText.textContent = 'Generating...';
  btnShimmer.style.display = 'block';

  try {
    const res = await fetch(`${API_BASE}/api/generate-syllabus`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic, email }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Syllabus generation failed');
    }

    const data = await res.json();

    clearInterval(loadingInterval);

    // Mark all steps done
    ['step-analyze', 'step-structure', 'step-generate', 'step-save'].forEach(id => {
      const el = document.getElementById(id);
      el.classList.remove('active');
      el.classList.add('done');
      el.querySelector('.step-icon').textContent = '✓';
    });

    // Brief pause for the "all done" feeling
    setTimeout(() => {
      renderSyllabus(data);
      showToast(`Syllabus generated: ${data.total_days} days of learning!`, 'success');
    }, 800);

  } catch (err) {
    console.error('Submit failed:', err);
    clearInterval(loadingInterval);
    showToast(err.message, 'error');
    showView('hero-view');
  } finally {
    btn.disabled = false;
    btnText.textContent = 'Generate My Learning Path';
    btnShimmer.style.display = 'none';
  }
}


// ═══════════════════════════════════════════════════════
//  EVENT LISTENERS
// ═══════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  // Init particles
  initParticles();

  // Form submit
  document.getElementById('topic-form').addEventListener('submit', handleSubmit);

  // Back buttons
  document.getElementById('back-to-hero').addEventListener('click', () => {
    showView('hero-view');
  });

  document.getElementById('back-to-syllabus').addEventListener('click', () => {
    showView('syllabus-view');
  });

  // Focus the topic input
  setTimeout(() => {
    document.getElementById('topic-input').focus();
  }, 600);
});
