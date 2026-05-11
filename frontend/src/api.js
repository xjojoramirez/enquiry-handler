const BASE = '/api';

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export function classify(text) {
  return request('/classify', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

export function submitEnquiry(text) {
  return request('/enquiries', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}

export function listEnquiries() {
  return request('/enquiries');
}

export function getEnquiry(id) {
  return request(`/enquiries/${id}`);
}
