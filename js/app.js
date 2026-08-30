const textarea = document.getElementById('jd-input');
const counter = document.getElementById('char-counter');
const predictBtn = document.getElementById('predict-btn');
const clearBtn = document.getElementById('clear-btn');
const emptyState = document.getElementById('empty-state');
const resultsContent = document.getElementById('results-content');
const loader = document.getElementById('loader');

const MAX_CHARS = 5000;

function updateCounter() {
	const len = textarea.value.length;
	counter.textContent = `${len} / ${MAX_CHARS}`;
	if (len > MAX_CHARS) {
		counter.classList.add('text-error');
		counter.classList.remove('text-on-surface-variant');
		predictBtn.disabled = true;
	} else {
		counter.classList.remove('text-error');
		counter.classList.add('text-on-surface-variant');
		predictBtn.disabled = false;
	}
}

function showResults() {
	loader.classList.add('hidden');
	emptyState.classList.add('hidden');
	resultsContent.classList.remove('hidden');
	resultsContent.classList.add('animate-fade-in-up');
}

function showLoader() {
	emptyState.classList.add('hidden');
	resultsContent.classList.add('hidden');
	loader.classList.remove('hidden');
}

function showEmpty() {
	emptyState.classList.remove('hidden');
	resultsContent.classList.add('hidden');
	loader.classList.add('hidden');
}

predictBtn.addEventListener('click', () => {
	if (textarea.value.trim().length === 0) {
		textarea.focus();
		return;
	}
	showLoader();
	predictBtn.disabled = true;
	setTimeout(() => {
		showResults();
		predictBtn.disabled = false;
	}, 1200);
});

clearBtn.addEventListener('click', () => {
	textarea.value = '';
	updateCounter();
	showEmpty();
	textarea.focus();
});

textarea.addEventListener('input', updateCounter);
updateCounter();
