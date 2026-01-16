async function requestJson(path, { method = 'GET', body } = {}) {
  const res = await fetch(path, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { raw: text };
  }

  if (!res.ok) {
    const msg = data && data.error ? data.error : `HTTP ${res.status}`;
    const err = new Error(msg);
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data;
}

export const api = {
  register: (payload) => requestJson('/register', { method: 'POST', body: payload }),
  login: (payload) => requestJson('/login', { method: 'POST', body: payload }),
  getChallenges: () => requestJson('/challenges'),
  getChallenge: (id) => requestJson(`/challenges/${id}`),
  addChallenge: (payload) => requestJson('/add_challenge', { method: 'POST', body: payload }),
  updateChallenge: (id, payload) => requestJson(`/challenges/${id}`, { method: 'PUT', body: payload }),
  deleteChallenge: (id, payload) => requestJson(`/challenges/${id}`, { method: 'DELETE', body: payload }),
  submit: (payload) => requestJson('/submit', { method: 'POST', body: payload }),
  getSubmissions: (username) => requestJson(`/submissions/${encodeURIComponent(username)}`),

  teacherListSubmissions: (payload) => requestJson('/teacher/submissions', { method: 'POST', body: payload }),
  teacherUpdateSubmission: (submissionId, payload) =>
    requestJson(`/teacher/submissions/${encodeURIComponent(submissionId)}`, { method: 'PUT', body: payload }),

  addTestCase: (challengeId, payload) =>
    requestJson(`/challenges/${challengeId}/add_test_case`, { method: 'POST', body: payload }),
  deleteTestCase: (testCaseId, payload) =>
    requestJson(`/test_cases/${testCaseId}`, { method: 'DELETE', body: payload }),

  addSolutionTemplate: (challengeId, payload) =>
    requestJson(`/challenges/${challengeId}/add_solution_template`, { method: 'POST', body: payload }),
  deleteSolutionTemplate: (templateId, payload) =>
    requestJson(`/solution_templates/${templateId}`, { method: 'DELETE', body: payload }),

  exportChallenge: (challengeId) => requestJson(`/challenges/${challengeId}/export`),
  copyChallenge: (challengeId, payload) => requestJson(`/challenges/${challengeId}/copy`, { method: 'POST', body: payload }),
  importChallenge: (payload) => requestJson('/import_challenge', { method: 'POST', body: payload }),
};
