const start = document.querySelector('#start');
const status = document.querySelector('#status');
const result = document.querySelector('#result');
const languageSelect = document.querySelector('#language');
const themeToggle = document.querySelector('#theme-toggle');

const translations = {
  unknown: {
    lang: 'en', trust: 'Voice · Retrieval · Evidence', headlineOne: 'Ask By Voice.', headlineTwo: 'Answer With Evidence.',
    subhead: 'A multilingual voice RAG assistant using Sarvam speech-to-text and MSMARCO-XI retrieval for grounded, cited answers.',
    ask: 'Ask by voice', ready: 'Ready for a voice question', listening: 'Listening… click again to send', send: 'Send question',
    transcribing: 'Transcribing…', answerReady: 'Answer ready', response: 'Response', permission: 'Microphone permission is required for voice questions.',
    failed: 'Voice request failed', transcript: 'Transcript', grounded: 'grounded', notGrounded: 'not grounded',
    metrics: ['Speech recognition', 'Hybrid retrieval', 'Safe answers', 'Cited sources']
  },
  'en-IN': {},
  'hi-IN': {
    lang: 'hi', trust: 'आवाज़ · खोज · प्रमाण', headlineOne: 'आवाज़ से पूछें।', headlineTwo: 'प्रमाण के साथ उत्तर।',
    subhead: 'Sarvam स्पीच-टू-टेक्स्ट और MSMARCO-XI खोज पर आधारित बहुभाषी वॉइस RAG सहायक, जो प्रमाणित उत्तर देता है।',
    ask: 'आवाज़ से पूछें', ready: 'सवाल पूछने के लिए तैयार', listening: 'सुन रहा हूँ… भेजने के लिए फिर क्लिक करें', send: 'सवाल भेजें',
    transcribing: 'आवाज़ को टेक्स्ट में बदल रहा है…', answerReady: 'उत्तर तैयार है', response: 'प्रतिक्रिया', permission: 'वॉइस सवालों के लिए माइक्रोफ़ोन की अनुमति आवश्यक है।',
    failed: 'वॉइस अनुरोध विफल रहा', transcript: 'प्रतिलिपि', grounded: 'प्रमाणित', notGrounded: 'अप्रमाणित',
    metrics: ['स्पीच पहचान', 'हाइब्रिड खोज', 'सुरक्षित उत्तर', 'उद्धृत स्रोत']
  },
  'bn-IN': {
    lang: 'bn', trust: 'কণ্ঠ · অনুসন্ধান · প্রমাণ', headlineOne: 'ভয়েসে প্রশ্ন করুন।', headlineTwo: 'প্রমাণসহ উত্তর পান।',
    subhead: 'Sarvam স্পিচ-টু-টেক্সট ও MSMARCO-XI অনুসন্ধান ব্যবহার করে প্রমাণভিত্তিক উত্তর দেওয়া বহুভাষিক ভয়েস RAG সহকারী।',
    ask: 'ভয়েসে জিজ্ঞাসা করুন', ready: 'ভয়েস প্রশ্নের জন্য প্রস্তুত', listening: 'শুনছি… পাঠাতে আবার ক্লিক করুন', send: 'প্রশ্ন পাঠান',
    transcribing: 'ভয়েসকে লেখায় বদলানো হচ্ছে…', answerReady: 'উত্তর প্রস্তুত', response: 'প্রতিক্রিয়া', permission: 'ভয়েস প্রশ্নের জন্য মাইক্রোফোনের অনুমতি প্রয়োজন।',
    failed: 'ভয়েস অনুরোধ ব্যর্থ হয়েছে', transcript: 'প্রতিলিপি', grounded: 'প্রমাণিত', notGrounded: 'অপ্রমাণিত',
    metrics: ['বক্তৃতা শনাক্তকরণ', 'হাইব্রিড অনুসন্ধান', 'নিরাপদ উত্তর', 'উদ্ধৃত উৎস']
  },
  'ta-IN': {
    lang: 'ta', trust: 'குரல் · தேடல் · ஆதாரம்', headlineOne: 'குரலில் கேளுங்கள்.', headlineTwo: 'ஆதாரத்துடன் பதில்.',
    subhead: 'Sarvam பேச்சு-உரை மற்றும் MSMARCO-XI தேடலைப் பயன்படுத்தி ஆதாரபூர்வ பதில்களை வழங்கும் பன்மொழி குரல் RAG உதவியாளர்.',
    ask: 'குரலில் கேளுங்கள்', ready: 'குரல் கேள்விக்குத் தயார்', listening: 'கேட்கிறேன்… அனுப்ப மீண்டும் அழுத்தவும்', send: 'கேள்வியை அனுப்பவும்',
    transcribing: 'குரல் உரையாக மாற்றப்படுகிறது…', answerReady: 'பதில் தயார்', response: 'பதில்', permission: 'குரல் கேள்விகளுக்கு மைக்ரோஃபோன் அனுமதி தேவை.',
    failed: 'குரல் கோரிக்கை தோல்வியடைந்தது', transcript: 'உரை', grounded: 'ஆதாரமுள்ளது', notGrounded: 'ஆதாரமில்லை',
    metrics: ['பேச்சு அறிதல்', 'கலப்பு தேடல்', 'பாதுகாப்பான பதில்கள்', 'மேற்கோள் ஆதாரங்கள்']
  },
  'te-IN': {
    lang: 'te', trust: 'వాయిస్ · శోధన · ఆధారం', headlineOne: 'వాయిస్‌తో అడగండి.', headlineTwo: 'ఆధారాలతో సమాధానం.',
    subhead: 'Sarvam స్పీచ్-టు-టెక్స్ట్ మరియు MSMARCO-XI శోధనతో ఆధారపూర్వక సమాధానాలు ఇచ్చే బహుభాషా వాయిస్ RAG సహాయకుడు.',
    ask: 'వాయిస్‌తో అడగండి', ready: 'వాయిస్ ప్రశ్నకు సిద్ధం', listening: 'వింటున్నాను… పంపడానికి మళ్లీ నొక్కండి', send: 'ప్రశ్న పంపండి',
    transcribing: 'వాయిస్‌ను టెక్స్ట్‌గా మారుస్తోంది…', answerReady: 'సమాధానం సిద్ధం', response: 'ప్రతిస్పందన', permission: 'వాయిస్ ప్రశ్నలకు మైక్రోఫోన్ అనుమతి అవసరం.',
    failed: 'వాయిస్ అభ్యర్థన విఫలమైంది', transcript: 'ట్రాన్స్‌క్రిప్ట్', grounded: 'ఆధారిత', notGrounded: 'ఆధారం లేదు',
    metrics: ['మాట గుర్తింపు', 'హైబ్రిడ్ శోధన', 'సురక్షిత సమాధానాలు', 'ఉల్లేఖిత మూలాలు']
  }
};
translations['en-IN'] = translations.unknown;

let phase = 'ready';
let busy = false;
let recorder;
let chunks = [];
let audioContext;
let audioSource;
let analyser;
let meterFrame;
let smoothedVoiceLevel = 0;

const copy = () => translations[languageSelect.value] || translations.unknown;
const show = message => { status.textContent = message; };
const buttonIcon = name => `<i class="fa-solid fa-${name}" aria-hidden="true"></i>`;

function updateButton() {
  const text = copy();
  if (phase === 'listening') start.innerHTML = `${buttonIcon('stop')} ${text.send}`;
  else start.innerHTML = `${buttonIcon('microphone')} ${text.ask}`;
}

function paintVoiceLevel(level) {
  start.style.setProperty('--voice-scale', (1.015 + level * 0.065).toFixed(3));
  start.style.setProperty('--voice-ring-scale', (1.08 + level * 0.18).toFixed(3));
  start.style.setProperty('--voice-blur', `${Math.round(24 + level * 48)}px`);
  start.style.setProperty('--voice-spread', `${Math.round(2 + level * 8)}px`);
  start.style.setProperty('--voice-alpha', (0.28 + level * 0.52).toFixed(2));
  start.style.setProperty('--voice-haze-alpha', (0.17 + level * 0.33).toFixed(2));
  start.style.setProperty('--voice-icon-scale', (1 + level * 0.3).toFixed(3));
}

function startVoiceVisualization(stream) {
  start.classList.add('is-listening');
  paintVoiceLevel(0);
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextClass) return;
  audioContext = new AudioContextClass();
  analyser = audioContext.createAnalyser();
  analyser.fftSize = 256;
  analyser.smoothingTimeConstant = 0.72;
  audioSource = audioContext.createMediaStreamSource(stream);
  audioSource.connect(analyser);
  const samples = new Uint8Array(analyser.fftSize);
  const updateMeter = () => {
    analyser.getByteTimeDomainData(samples);
    let energy = 0;
    for (const sample of samples) {
      const amplitude = (sample - 128) / 128;
      energy += amplitude * amplitude;
    }
    const rms = Math.sqrt(energy / samples.length);
    const level = Math.min(1, Math.max(0, (rms - 0.018) * 9));
    smoothedVoiceLevel = smoothedVoiceLevel * 0.68 + level * 0.32;
    paintVoiceLevel(smoothedVoiceLevel);
    meterFrame = requestAnimationFrame(updateMeter);
  };
  updateMeter();
}

function stopVoiceVisualization() {
  if (meterFrame) cancelAnimationFrame(meterFrame);
  meterFrame = undefined;
  audioSource?.disconnect();
  audioSource = undefined;
  analyser = undefined;
  if (audioContext && audioContext.state !== 'closed') audioContext.close().catch(() => {});
  audioContext = undefined;
  smoothedVoiceLevel = 0;
  start.classList.remove('is-listening');
  paintVoiceLevel(0);
}

function applyLanguage() {
  const text = copy();
  document.documentElement.lang = text.lang;
  document.querySelector('#trust-copy').textContent = text.trust;
  document.querySelector('#headline-one').textContent = text.headlineOne;
  document.querySelector('#headline-two').textContent = text.headlineTwo;
  document.querySelector('#subhead-copy').textContent = text.subhead;
  ['metric-stt', 'metric-search', 'metric-safe', 'metric-cited'].forEach((id, index) => {
    document.querySelector(`#${id}`).textContent = text.metrics[index];
  });
  updateButton();
  if (!busy && result.hidden) show(text.ready);
  localStorage.setItem('voiceRagLanguage', languageSelect.value);
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  const light = theme === 'light';
  themeToggle.innerHTML = buttonIcon(light ? 'moon' : 'sun');
  themeToggle.setAttribute('aria-label', light ? 'Use dark mode' : 'Use light mode');
  themeToggle.title = light ? 'Use dark mode' : 'Use light mode';
  localStorage.setItem('voiceRagTheme', theme);
}

function render(data) {
  const text = copy();
  result.hidden = false;
  document.querySelector('#transcript').textContent = data.transcript ? `${text.transcript}: ${data.transcript}` : '';
  document.querySelector('#answer').textContent = data.answer;
  const source = data.citations?.[0]?.source;
  const evidenceLabel = data.reason === 'assistant_help' ? 'guidance' : (data.grounded ? text.grounded : text.notGrounded);
  document.querySelector('#details').textContent = `${data.status} · ${evidenceLabel} · ${Math.round(data.latency_ms?.total || 0)}ms${source ? ` · Source: ${source}` : ''}`;
  show(data.status === 'answered' ? text.answerReady : `${text.response}: ${data.reason || data.status}`);
}

async function send(audio) {
  const text = copy();
  phase = 'processing';
  updateButton();
  show(text.transcribing);
  const form = new FormData();
  form.append('audio', audio, 'voice.webm');
  form.append('language_code', languageSelect.value);
  const response = await fetch('/api/v1/voice-query', { method: 'POST', body: form });
  if (!response.ok) {
    let detail = text.failed;
    try { detail = (await response.json()).detail || detail; } catch (_) { /* non-JSON error */ }
    throw new Error(detail);
  }
  render(await response.json());
}

async function listen() {
  if (busy) return;
  busy = true;
  result.hidden = true;
  let stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    chunks = [];
    recorder = new MediaRecorder(stream);
    recorder.ondataavailable = event => { if (event.data.size) chunks.push(event.data); };
    recorder.onstop = async () => {
      stopVoiceVisualization();
      try {
        await send(new Blob(chunks, { type: recorder.mimeType || 'audio/webm' }));
      } catch (error) {
        show(error.message);
      } finally {
        stream.getTracks().forEach(track => track.stop());
        busy = false;
        phase = 'ready';
        updateButton();
      }
    };
    recorder.start();
    startVoiceVisualization(stream);
    phase = 'listening';
    show(copy().listening);
    updateButton();
  } catch (_) {
    stopVoiceVisualization();
    stream?.getTracks().forEach(track => track.stop());
    busy = false;
    phase = 'ready';
    show(copy().permission);
    updateButton();
  }
}

const savedLanguage = localStorage.getItem('voiceRagLanguage');
if (savedLanguage && translations[savedLanguage]) languageSelect.value = savedLanguage;
const savedTheme = localStorage.getItem('voiceRagTheme');
applyTheme(savedTheme || (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'));
applyLanguage();

languageSelect.addEventListener('change', applyLanguage);
themeToggle.addEventListener('click', () => applyTheme(document.documentElement.dataset.theme === 'light' ? 'dark' : 'light'));
start.addEventListener('click', () => recorder?.state === 'recording' ? recorder.stop() : listen());

const splitFlapRoot = document.querySelector('#builder-credit');
function createSplitFlap(root, text) {
  const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const target = [...text.toUpperCase()];
  root.classList.add('split-flap-text');
  const tiles = target.map((character, index) => {
    const tile = document.createElement('span');
    tile.className = 'split-flap-text__tile';
    tile.setAttribute('aria-hidden', 'true');
    tile.innerHTML = '<span class="split-flap-text__half split-flap-text__half--top"><span class="split-flap-text__char"></span></span><span class="split-flap-text__half split-flap-text__half--bottom"><span class="split-flap-text__char"></span></span><span class="split-flap-text__flap split-flap-text__flap--front"><span class="split-flap-text__char"></span></span><span class="split-flap-text__flap split-flap-text__flap--back"><span class="split-flap-text__char"></span></span>';
    root.appendChild(tile);
    return { tile, character, index };
  });
  const paint = (entry, character, flipping = false) => {
    entry.tile.classList.toggle('is-flipping', flipping);
    entry.tile.querySelectorAll('.split-flap-text__char').forEach(node => { node.textContent = character === ' ' ? '\u00a0' : character; });
  };
  tiles.forEach(entry => paint(entry, reduced ? entry.character : ' '));
  if (reduced) return;
  tiles.forEach(entry => {
    let step = 0;
    setTimeout(() => {
      const timer = setInterval(() => {
        step += 1;
        paint(entry, step >= 7 ? entry.character : charset[Math.floor(Math.random() * charset.length)], step < 7);
        if (step >= 7) clearInterval(timer);
      }, 58);
    }, 180 + entry.index * 42);
  });
}
if (splitFlapRoot) createSplitFlap(splitFlapRoot, 'BUILT BY PINKU SHARMA');
