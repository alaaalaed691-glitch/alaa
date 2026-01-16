export function qs(sel, root = document) {
  return root.querySelector(sel);
}

export function qsa(sel, root = document) {
  return Array.from(root.querySelectorAll(sel));
}

export function setText(el, text) {
  if (!el) return;
  el.textContent = text;
}

export function setHtml(el, html) {
  if (!el) return;
  el.innerHTML = html;
}

export function show(el) {
  if (!el) return;
  el.classList.remove('hidden');
}

export function hide(el) {
  if (!el) return;
  el.classList.add('hidden');
}

export function alertBox(type, msg) {
  const div = document.createElement('div');
  div.className = `alert ${type}`;
  div.textContent = msg;
  return div;
}

export function badgeForResult(result) {
  if (result === 'success') return '<span class="tag">نجاح</span>';
  if (result === 'partial') return '<span class="tag">جزئي</span>';
  return '<span class="tag">فشل</span>';
}

export function escapeHtml(str) {
  return String(str)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}
