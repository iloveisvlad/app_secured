const tokenKey = "taskops_token";

function token() {
  return localStorage.getItem(tokenKey);
}

function setToken(value) {
  localStorage.setItem(tokenKey, value);
}

function clearToken() {
  localStorage.removeItem(tokenKey);
}

function requireAuth() {
  if (!token() && location.pathname !== "/" && location.pathname !== "/login") {
    location.href = "/login";
  }
}

async function api(path, options = {}) {
  const headers = options.headers || {};
  if (token()) {
    headers.Authorization = `Bearer ${token()}`;
  }
  const response = await fetch(path, { ...options, headers });
  if (response.status === 401) {
    clearToken();
    location.href = "/login";
    return null;
  }
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || response.statusText);
  }
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }
  return response.text();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function item(title, body, footer = "") {
  return `<div class="item"><h3>${escapeHtml(title)}</h3><p>${escapeHtml(body || "")}</p>${footer}</div>`;
}

async function loadCurrentUser() {
  const slot = document.getElementById("current-user");
  if (!slot) return;
  const user = await api("/auth/me");
  slot.textContent = `${user.full_name} · ${user.role}`;
}

async function loadProjects(selectIds = []) {
  const projects = await api("/projects");
  const list = document.getElementById("projects-list");
  if (list) {
    list.innerHTML = projects.map(project => item(
      project.name,
      project.description,
      `<span class="badge">tasks: ${project.tasks_count}</span> <a href="/projects/${project.id}/view">open</a>`
    )).join("");
  }
  for (const selectId of selectIds) {
    const select = document.getElementById(selectId);
    if (!select) continue;
    const first = select.dataset.keepEmpty === "true" ? `<option value="">all projects</option>` : "";
    select.innerHTML = first + projects.map(project => `<option value="${project.id}">${escapeHtml(project.name)}</option>`).join("");
  }
  return projects;
}

async function loadTasks(projectId = null, targetId = "tasks-list") {
  const path = projectId ? `/tasks?project_id=${projectId}` : "/tasks";
  const tasks = await api(path);
  const list = document.getElementById(targetId);
  if (!list) return tasks;
  list.innerHTML = tasks.map(task => item(
    task.title,
    task.description,
    `<span class="badge">${task.status}</span> <span class="badge">${task.priority}</span> <a href="/tasks/${task.id}/view">open</a>`
  )).join("") || `<p class="muted">задач пока нет</p>`;
  return tasks;
}

async function initLogin() {
  const form = document.getElementById("login-form");
  if (!form) return;
  form.addEventListener("submit", async event => {
    event.preventDefault();
    const data = new FormData(form);
    const body = new URLSearchParams();
    body.set("username", data.get("username"));
    body.set("password", data.get("password"));
    try {
      const result = await fetch("/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      if (!result.ok) throw new Error("login failed");
      const payload = await result.json();
      setToken(payload.access_token);
      location.href = "/dashboard";
    } catch (error) {
      document.getElementById("login-message").textContent = error.message;
    }
  });
}

async function initDashboard() {
  await loadCurrentUser();
  await loadProjects(["task-project-select"]);
  await loadTasks();

  const projectForm = document.getElementById("project-form");
  projectForm.addEventListener("submit", async event => {
    event.preventDefault();
    const data = new FormData(projectForm);
    await api("/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: data.get("name"), description: data.get("description") }),
    });
    projectForm.reset();
    await loadProjects(["task-project-select"]);
  });

  const taskForm = document.getElementById("task-form");
  taskForm.addEventListener("submit", async event => {
    event.preventDefault();
    const data = new FormData(taskForm);
    await api("/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project_id: Number(data.get("project_id")),
        title: data.get("title"),
        description: data.get("description"),
        priority: data.get("priority"),
        status: data.get("status"),
      }),
    });
    taskForm.reset();
    await loadTasks();
  });
}

async function initProject() {
  const root = document.querySelector("[data-page='project']");
  const projectId = root.dataset.projectId;
  const project = await api(`/projects/${projectId}`);
  document.getElementById("project-title").textContent = project.name;
  document.getElementById("project-description").textContent = project.description || "";
  await loadTasks(projectId, "project-tasks-list");
}

async function loadTask(taskId) {
  const task = await api(`/tasks/${taskId}`);
  document.getElementById("task-title").textContent = task.title;
  document.getElementById("task-description").textContent = task.description || "";
  document.querySelector("#task-update-form [name='status']").value = task.status;
  document.querySelector("#task-update-form [name='priority']").value = task.priority;
  document.getElementById("task-meta").innerHTML = `project: ${task.project_id}<br>created: ${task.created_at}<br>updated: ${task.updated_at}`;
}

async function loadComments(taskId) {
  const comments = await api(`/tasks/${taskId}/comments`);
  const list = document.getElementById("comments-list");
  list.innerHTML = comments.map(comment => item(comment.author_username || `user ${comment.author_id}`, comment.body, `<span class="badge">${comment.created_at}</span>`)).join("") || `<p class="muted">комментариев пока нет</p>`;
}

async function loadAttachments(taskId) {
  const attachments = await api(`/tasks/${taskId}/attachments`);
  const list = document.getElementById("attachments-list");
  list.innerHTML = attachments.map(file => item(
    file.filename,
    `${file.size_bytes} bytes · ${file.content_type || "unknown"}`,
    `<a href="/tasks/${taskId}/attachments/${file.id}/download" data-download="/tasks/${taskId}/attachments/${file.id}/download">download</a>`
  )).join("") || `<p class="muted">вложений пока нет</p>`;
}

function setFormBusy(form, isBusy) {
  const controls = form.querySelectorAll("button, input, select, textarea");
  controls.forEach(control => {
    control.disabled = isBusy;
  });
}

function setMessage(id, text) {
  const slot = document.getElementById(id);
  if (slot) {
    slot.textContent = text;
  }
}

async function initTask() {
  const root = document.querySelector("[data-page='task']");
  const taskId = root.dataset.taskId;
  await loadTask(taskId);
  await loadComments(taskId);
  await loadAttachments(taskId);

  document.getElementById("task-update-form").addEventListener("submit", async event => {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    setFormBusy(form, true);
    try {
      await api(`/tasks/${taskId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: data.get("status"), priority: data.get("priority") }),
      });
      await loadTask(taskId);
    } finally {
      setFormBusy(form, false);
    }
  });

  document.getElementById("comment-form").addEventListener("submit", async event => {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const body = String(data.get("body") || "").trim();

    if (!body) {
      setMessage("comment-message", "комментарий не должен быть пустым");
      return;
    }

    setFormBusy(form, true);
    setMessage("comment-message", "сохранение комментария...");
    try {
      await api(`/tasks/${taskId}/comments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ body }),
      });
      form.reset();
      await loadComments(taskId);
      setMessage("comment-message", "комментарий добавлен");
    } catch (error) {
      setMessage("comment-message", error.message);
    } finally {
      setFormBusy(form, false);
    }
  });

  document.getElementById("attachment-form").addEventListener("submit", async event => {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const selectedFile = data.get("file");

    if (!selectedFile || selectedFile.size === 0) {
      setMessage("attachment-message", "выберите файл для загрузки");
      return;
    }

    setFormBusy(form, true);
    setMessage("attachment-message", "загрузка файла...");
    try {
      await api(`/tasks/${taskId}/attachments`, { method: "POST", body: data });
      form.reset();
      await loadAttachments(taskId);
      setMessage("attachment-message", "файл загружен");
    } catch (error) {
      setMessage("attachment-message", error.message);
    } finally {
      setFormBusy(form, false);
    }
  });
}

async function initReports() {
  const select = document.getElementById("report-project-select");
  select.dataset.keepEmpty = "true";
  await loadProjects(["report-project-select"]);

  document.getElementById("report-form").addEventListener("submit", async event => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const projectId = data.get("project_id") ? Number(data.get("project_id")) : null;
    const job = await api("/reports/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: projectId, format: data.get("format") }),
    });
    pollReport(job.id);
  });
}

async function pollReport(jobId) {
  const slot = document.getElementById("report-status");
  for (let i = 0; i < 30; i++) {
    const job = await api(`/reports/${jobId}`);
    if (job.status === "done") {
      slot.innerHTML = `status: done<br><a href="${job.download_url}" data-download="${job.download_url}">download report</a>`;
      return;
    }
    if (job.status === "failed") {
      slot.textContent = `status: failed · ${job.error_message}`;
      return;
    }
    slot.textContent = `status: ${job.status}`;
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
}


async function downloadWithToken(url) {
  const response = await fetch(url, { headers: { Authorization: `Bearer ${token()}` } });
  if (!response.ok) throw new Error("download failed");
  const blob = await response.blob();
  const disposition = response.headers.get("content-disposition") || "";
  const match = disposition.match(/filename="?([^";]+)"?/i);
  const filename = match ? match[1] : "download.bin";
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(objectUrl);
}

function initDownloads() {
  document.addEventListener("click", async event => {
    const target = event.target.closest("[data-download]");
    if (!target) return;
    event.preventDefault();
    try {
      await downloadWithToken(target.dataset.download);
    } catch (error) {
      alert(error.message);
    }
  });
}

function initLogout() {
  const button = document.getElementById("logout-button");
  if (!button) return;
  button.addEventListener("click", () => {
    clearToken();
    location.href = "/login";
  });
}

async function boot() {
  requireAuth();
  initLogout();
  initDownloads();
  const page = document.querySelector("[data-page]")?.dataset.page;
  try {
    if (page === "login") await initLogin();
    if (page === "dashboard") await initDashboard();
    if (page === "project") await initProject();
    if (page === "task") await initTask();
    if (page === "reports") await initReports();
  } catch (error) {
    console.error(error);
    alert(error.message);
  }
}

boot();
