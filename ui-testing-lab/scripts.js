// Navigation
function navigate(section) {
    document.querySelectorAll('.test-section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.sidebar-link').forEach(l => l.classList.remove('active'));
    document.getElementById('section-' + section).classList.add('active');
    document.querySelector('[data-section="' + section + '"]').classList.add('active');
    document.getElementById('section-badge').textContent = section.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    document.getElementById('section-path').textContent = '/' + section;
    document.querySelector('.sidebar').classList.remove('open');

    // Init section-specific content
    if (section === 'infinite-scroll') initInfiniteScroll();
    if (section === 'dynamic-content') loadDynamicContent();
    if (section === 'shadow-dom') initShadowDOM();
    if (section === 'challenging-dom') loadChallengingDOM();
    if (section === 'keypresses') initKeypress();
    if (section === 'checkboxes') initCheckboxes();
}

// LOGIN
function handleLogin() {
    const user = document.getElementById('login-username').value;
    const pass = document.getElementById('login-password').value;
    const result = document.getElementById('login-result');
    const alert = document.getElementById('login-alert');

    if (!user || !pass) {
        alert.innerHTML = '<div class="alert-box alert-error">Please fill in all fields.</div>';
        result.textContent = 'Login failed: missing credentials';
        return;
    }

    if (user === 'tomsmith' && pass === 'SuperSecretPassword!') {
        alert.innerHTML = '<div class="alert-box alert-success">✓ You logged into a secure area!</div>';
        result.textContent = 'Login successful! Welcome, tomsmith.';
    } else {
        alert.innerHTML = '<div class="alert-box alert-error">✗ Your username is invalid!</div>';
        result.textContent = 'Login failed: invalid credentials';
    }
}

// CHECKBOXES
function initCheckboxes() {
    for (let i = 1; i <= 4; i++) {
        document.getElementById('cb-' + i).addEventListener('change', updateCheckboxStatus);
    }
    updateCheckboxStatus();
}

function updateCheckboxStatus() {
    let states = [];
    for (let i = 1; i <= 4; i++) {
        const cb = document.getElementById('cb-' + i);
        const status = document.getElementById('cb-' + i + '-status');
        if (cb.checked) {
            status.style.display = 'inline';
            states.push('checkbox ' + i + ': on');
        } else {
            status.style.display = 'none';
            states.push('checkbox ' + i + ': off');
        }
    }
    document.getElementById('checkbox-result').textContent = states.join(' | ');
}

function selectAllCheckboxes() {
    for (let i = 1; i <= 4; i++) document.getElementById('cb-' + i).checked = true;
    updateCheckboxStatus();
}

function deselectAllCheckboxes() {
    for (let i = 1; i <= 4; i++) document.getElementById('cb-' + i).checked = false;
    updateCheckboxStatus();
}

// DROPDOWN
function handleDropdownChange() {
    const select = document.getElementById('dropdown-select');
    const value = select.value;
    const text = select.options[select.selectedIndex].text;
    document.getElementById('dropdown-result').textContent = value ? `Selected: ${text} (value: ${value})` : 'No selection made...';
}

// INPUTS
function handleInputChange() {
    const val = document.getElementById('number-input').value;
    document.getElementById('input-result').textContent = val ? `Current value: ${val} (type: number)` : 'Awaiting input...';
}

function handleTextInputChange() {
    const val = document.getElementById('text-input').value;
    document.getElementById('text-input-result').textContent = val ? `Current value: "${val}" (length: ${val.length})` : 'Awaiting input...';
}

// FILE UPLOAD
const uploadZone = document.getElementById('upload-zone');
if (uploadZone) {
    uploadZone.addEventListener('dragover', (e) => { e.preventDefault(); uploadZone.classList.add('dragover'); });
    uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) handleFileUpload({ files: e.dataTransfer.files });
    });
}

function handleFileUpload(input) {
    const files = input.files || input;
    if (files.length > 0) {
        const file = files[0];
        document.getElementById('upload-result').textContent = `Uploaded: ${file.name} (${file.size} bytes, ${file.type || 'unknown'})`;
    }
}

// FILE DOWNLOAD
function triggerDownload(filename, content) {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    document.getElementById('download-result').textContent = `Downloaded: ${filename}`;
}

// FORGOT PASSWORD
function handleForgotPassword() {
    const email = document.getElementById('forgot-email').value;
    const alert = document.getElementById('forgot-alert');
    const result = document.getElementById('forgot-result');

    if (!email) {
        alert.innerHTML = '<div class="alert-box alert-error">Email is required.</div>';
        result.textContent = 'Submission failed: missing email';
        return;
    }

    if (!email.includes('@') || !email.includes('.')) {
        alert.innerHTML = '<div class="alert-box alert-warning">Please enter a valid email address.</div>';
        result.textContent = 'Invalid email format';
        return;
    }

    alert.innerHTML = '<div class="alert-box alert-success">✓ Internal email sent successfully.</div>';
    result.textContent = `Password reset email sent to: ${email}`;
}

// WYSIWYG
function execCmd(cmd) {
    document.execCommand(cmd, false, null);
    document.getElementById('wysiwyg-editor').focus();
}

function getWysiwygContent() {
    const content = document.getElementById('wysiwyg-editor').innerHTML;
    document.getElementById('wysiwyg-result').textContent = content;
}

// DYNAMIC CONTROLS
function toggleRemoveButton() {
    const checkbox = document.getElementById('enable-checkbox');
    const btn = document.getElementById('remove-btn');
    btn.disabled = !checkbox.checked;
    document.getElementById('dynamic-controls-result').textContent = checkbox.checked ? 'Button is now enabled.' : 'Button is now disabled.';
}

function handleRemoveElement() {
    const result = document.getElementById('dynamic-controls-result');
    result.textContent = 'Element removed!';
    result.style.color = 'var(--accent-green)';
    setTimeout(() => { result.textContent = 'Button toggled. Click again.'; result.style.color = ''; }, 1500);
}

let elementCounter = 0;
function addDynamicElement() {
    elementCounter++;
    const container = document.getElementById('dynamic-elements-container');
    const el = document.createElement('div');
    el.className = 'shifting-box';
    el.textContent = `Element ${elementCounter}`;
    el.style.opacity = '0';
    container.appendChild(el);
    setTimeout(() => el.style.opacity = '1', 50);
}

// DYNAMIC LOADING
function startLoading() {
    const container = document.getElementById('loading-container');
    const result = document.getElementById('loading-result');
    container.style.display = 'block';
    result.style.display = 'none';

    setTimeout(() => {
        container.style.display = 'none';
        result.style.display = 'block';
        result.textContent = '✓ Hello World! Content loaded successfully.';
    }, 3000);
}

// DYNAMIC CONTENT
const dynamicNames = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry'];
const dynamicAvatars = ['👤', '👩', '👨', '🧑', '👧', '🧔', '👩‍🦰', '👨‍🦱'];

function loadDynamicContent() {
    const container = document.getElementById('dynamic-content-container');
    container.innerHTML = '';
    for (let i = 0; i < 4; i++) {
        const name = dynamicNames[Math.floor(Math.random() * dynamicNames.length)];
        const avatar = dynamicAvatars[Math.floor(Math.random() * dynamicAvatars.length)];
        const item = document.createElement('div');
        item.className = 'dynamic-content-item';
        item.innerHTML = `
            <div style="width:48px;height:48px;border-radius:50%;background:var(--bg-tertiary);display:flex;align-items:center;justify-content:center;font-size:1.5rem;">${avatar}</div>
            <div>
                <div style="font-weight:600;">${name}</div>
                <div style="font-size:0.8rem;color:var(--text-secondary);">Content updated at ${new Date().toLocaleTimeString()}</div>
            </div>
        `;
        container.appendChild(item);
    }
}

// ADD/REMOVE ELEMENTS
let elementCount = 1;
function addElement() {
    const container = document.getElementById('element-list');
    const el = document.createElement('div');
    el.className = 'shifting-box';
    el.setAttribute('data-element-id', elementCount);
    const id = elementCount;
    el.innerHTML = `Element ${elementCount} <button class="btn btn-danger" style="padding:2px 8px;font-size:0.75rem;margin-left:8px;" onclick="removeSpecificElement(${id})">×</button>`;
    container.appendChild(el);
    elementCount++;
    updateElementCount();
}

function removeElement() {
    const container = document.getElementById('element-list');
    if (container.children.length > 0) {
        container.removeChild(container.lastChild);
        updateElementCount();
    }
}

function removeSpecificElement(id) {
    const el = document.querySelector(`[data-element-id="${id}"]`);
    if (el) {
        el.remove();
        updateElementCount();
    }
}

function updateElementCount() {
    const count = document.getElementById('element-list').children.length;
    document.getElementById('add-remove-result').textContent = `Elements: ${count}`;
}

// DISAPPEARING ELEMENTS
function disappear(btn) {
    btn.style.display = 'none';
    document.getElementById('disappearing-result').textContent = `${btn.textContent} has disappeared!`;
}

function resetDisappearing() {
    const container = document.getElementById('disappearing-container');
    container.innerHTML = '';
    ['Home', 'About', 'Contact Us', 'Portfolio', 'Blog'].forEach(name => {
        const btn = document.createElement('button');
        btn.className = 'btn';
        btn.textContent = name;
        btn.onclick = function() { disappear(this); };
        container.appendChild(btn);
    });
    document.getElementById('disappearing-result').textContent = 'Elements reset!';
}

// SHIFTING CONTENT
function shuffleContent() {
    const container = document.getElementById('shifting-container');
    const items = Array.from(container.children);
    for (let i = items.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        container.appendChild(items[j]);
    }
}

// INFINITE SCROLL
let infiniteLoaded = 0;
let infiniteLoading = false;

function initInfiniteScroll() {
    infiniteLoaded = 0;
    document.getElementById('infinite-scroll-container').innerHTML = '';
    loadMoreItems();
    document.getElementById('infinite-scroll-container').addEventListener('scroll', function() {
        if (this.scrollTop + this.clientHeight >= this.scrollHeight - 50 && !infiniteLoading) {
            loadMoreItems();
        }
    });
}

function loadMoreItems() {
    if (infiniteLoading) return;
    infiniteLoading = true;
    document.getElementById('infinite-scroll-loader').style.display = 'flex';

    setTimeout(() => {
        const container = document.getElementById('infinite-scroll-container');
        for (let i = 0; i < 5; i++) {
            infiniteLoaded++;
            const item = document.createElement('div');
            item.className = 'infinite-scroll-item';
            item.innerHTML = `<strong>Item #${infiniteLoaded}</strong><br><span style="font-size:0.8rem;color:var(--text-secondary);">Loaded at ${new Date().toLocaleTimeString()}</span>`;
            container.appendChild(item);
        }
        infiniteLoading = false;
        document.getElementById('infinite-scroll-loader').style.display = 'none';
        document.getElementById('infinite-result').textContent = `Loaded ${infiniteLoaded} items so far...`;
    }, 800);
}

// ALERTS
function showAlert(type) {
    const result = document.getElementById('alert-result');
    if (type === 'alert') {
        alert('This is a JavaScript alert!');
        result.textContent = 'Alert was shown and dismissed.';
    } else if (type === 'confirm') {
        const confirmed = confirm('Do you want to proceed?');
        result.textContent = `Confirm dialog: ${confirmed ? 'OK was clicked' : 'Cancel was clicked'}`;
    } else if (type === 'prompt') {
        const name = prompt('Please enter your name:', '');
        result.textContent = name ? `Prompt result: "${name}"` : 'Prompt was cancelled.';
    }
}

// KEY PRESSES
function initKeypress() {
    const display = document.getElementById('key-display');
    const result = document.getElementById('key-result');
    const keys = [];

    document.addEventListener('keydown', function(e) {
        if (!document.getElementById('section-keypresses').classList.contains('active')) return;
        e.preventDefault();
        display.textContent = e.key === ' ' ? 'Space' : e.key;
        keys.push(`"${e.key}" (code: ${e.code})`);
        result.textContent = `Keys pressed: ${keys.slice(-10).join(', ')}`;
    });
}

// HOVERS
document.querySelectorAll('.hover-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        const name = this.querySelector('.tooltip').textContent;
        document.getElementById('hovers-result').textContent = name;
    });
});

// DRAG AND DROP
let draggedElement = null;

function handleDragStart(e) {
    draggedElement = e.target;
    e.target.classList.add('dragging');
    e.dataTransfer.setData('text/plain', e.target.id);
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('drag-over');
}

function handleDrop(e, targetId) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    if (draggedElement) {
        e.currentTarget.appendChild(draggedElement);
        draggedElement.classList.remove('dragging');
        document.getElementById('drag-result').textContent = `${draggedElement.id} dropped into ${targetId}`;
        draggedElement = null;
    }
}

document.addEventListener('dragend', function() {
    document.querySelectorAll('.drag-item').forEach(el => el.classList.remove('dragging'));
});

// SLIDER
function handleSliderChange() {
    const val = document.getElementById('range-slider').value;
    document.getElementById('slider-display').textContent = val;
    document.getElementById('slider-result').textContent = `Current value: ${val}`;
}

// CONTEXT MENU
const contextTarget = document.getElementById('context-target');
let contextMenu = null;

contextTarget.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    closeContextMenu();

    contextMenu = document.createElement('div');
    contextMenu.className = 'context-menu';
    contextMenu.style.left = e.pageX + 'px';
    contextMenu.style.top = e.pageY + 'px';
    contextMenu.innerHTML = `
        <div class="context-menu-item" onclick="contextAction('Back')">↩ Back</div>
        <div class="context-menu-item" onclick="contextAction('Forward')">↪ Forward</div>
        <div class="context-menu-item" onclick="contextAction('Reload')">🔄 Reload</div>
        <div style="height:1px;background:var(--border);margin:4px 0;"></div>
        <div class="context-menu-item" onclick="contextAction('Save As')">💾 Save As...</div>
        <div class="context-menu-item" onclick="contextAction('Print')">🖨️ Print</div>
        <div style="height:1px;background:var(--border);margin:4px 0;"></div>
        <div class="context-menu-item" onclick="contextAction('View Source')">🔍 View Page Source</div>
        <div class="context-menu-item" onclick="contextAction('Inspect')">🔧 Inspect</div>
    `;
    document.body.appendChild(contextMenu);
});

function contextAction(action) {
    document.getElementById('context-result').textContent = `Context menu action: ${action}`;
    closeContextMenu();
}

function closeContextMenu() {
    if (contextMenu) {
        contextMenu.remove();
        contextMenu = null;
    }
}

document.addEventListener('click', closeContextMenu);

// MULTIPLE WINDOWS
function openNewWindow(url) {
    const win = window.open(url, '_blank', 'width=800,height=600');
    document.getElementById('windows-result').textContent = `Opened new window: ${url}`;
}

// SORT TABLE
let sortDirection = {};

function sortTable(colIndex) {
    const tbody = document.getElementById('sort-table-body');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const dir = sortDirection[colIndex] === 'asc' ? 'desc' : 'asc';
    sortDirection[colIndex] = dir;

    rows.sort((a, b) => {
        const aText = a.cells[colIndex].textContent.trim();
        const bText = b.cells[colIndex].textContent.trim();
        const aNum = parseFloat(aText);
        const bNum = parseFloat(bText);

        if (!isNaN(aNum) && !isNaN(bNum)) {
            return dir === 'asc' ? aNum - bNum : bNum - aNum;
        }
        return dir === 'asc' ? aText.localeCompare(bText) : bText.localeCompare(aText);
    });

    rows.forEach(row => tbody.appendChild(row));
    document.getElementById('table-result').textContent = `Sorted by column ${colIndex + 1} (${dir}ending)`;
}

// NOTIFICATIONS
function showNotification(type, message) {
    const toast = document.createElement('div');
    toast.className = 'notification-toast';
    if (type === 'success') toast.style.borderLeftColor = 'var(--accent-green)';
    else if (type === 'error') toast.style.borderLeftColor = 'var(--accent-red)';
    else if (type === 'warning') toast.style.borderLeftColor = 'var(--accent-orange)';
    else toast.style.borderLeftColor = 'var(--accent-blue)';

    toast.innerHTML = `<div style="font-size:0.9rem;">${message}</div>`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// STATUS CODES
function showStatus(code) {
    const messages = {
        200: 'OK - The request was successful.',
        201: 'Created - A new resource was created.',
        301: 'Moved Permanently - The resource has been permanently moved.',
        302: 'Found - The resource has been temporarily moved.',
        400: 'Bad Request - The server could not understand the request.',
        401: 'Unauthorized - Authentication is required.',
        403: 'Forbidden - Access is denied.',
        404: 'Not Found - The resource could not be found.',
        500: 'Internal Server Error - Something went wrong on the server.',
        503: 'Service Unavailable - The server is temporarily unavailable.'
    };
    document.getElementById('status-result').textContent = `HTTP ${code}: ${messages[code]}`;
}

// SHADOW DOM
function initShadowDOM() {
    const host = document.getElementById('shadow-host');
    if (!host.shadowRoot) {
        const shadow = host.attachShadow({ mode: 'open' });
        shadow.innerHTML = `
            <div style="padding:16px;background:var(--bg-primary);border-radius:4px;">
                <h3 style="margin:0 0 8px;font-size:1rem;color:var(--accent-purple);">Shadow DOM Content</h3>
                <p style="margin:0 0 12px;font-size:0.85rem;color:var(--text-secondary);">This content is inside a Shadow DOM.</p>
                <button id="shadow-btn" style="padding:6px 12px;background:var(--accent-purple);border:none;border-radius:4px;color:#fff;cursor:pointer;font-size:0.85rem;">Click Me</button>
                <input id="shadow-input" style="margin-top:8px;padding:6px 12px;background:var(--bg-secondary);border:1px solid var(--border);border-radius:4px;color:var(--text-primary);width:200px;font-size:0.85rem;" placeholder="Type in shadow input">
            </div>
        `;
        shadow.getElementById('shadow-btn').addEventListener('click', () => {
            document.getElementById('shadow-result').textContent = 'Shadow DOM button was clicked!';
        });
    }
}

function interactShadowDOM() {
    const host = document.getElementById('shadow-host');
    if (host.shadowRoot) {
        const input = host.shadowRoot.getElementById('shadow-input');
        if (input) {
            input.value = 'Interacted via Playwright!';
            document.getElementById('shadow-result').textContent = 'Shadow DOM input value set: ' + input.value;
        }
    }
}

// FLOATING MENU - already handled by CSS position:sticky

// ENTRY AD
function showEntryAd() {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.onclick = function(e) { if (e.target === overlay) closeEntryAd(overlay); };
    overlay.innerHTML = `
        <div class="modal-content modal-ad">
            <div style="font-size:2.5rem;margin-bottom:12px;">🎉</div>
            <h2 style="margin:0 0 8px;">Welcome to UI Testing Lab!</h2>
            <p style="color:var(--text-secondary);margin-bottom:20px;">This is an entry ad modal. Use Playwright to interact with and dismiss it.</p>
            <div style="background:var(--bg-primary);border:1px solid var(--border);border-radius:8px;padding:16px;margin-bottom:20px;text-align:left;">
                <div style="font-size:0.85rem;color:var(--text-secondary);">📊 Special Offer</div>
                <div style="font-size:1.25rem;font-weight:700;color:var(--accent-blue);">Get 50% Off Premium!</div>
                <div style="font-size:0.8rem;color:var(--text-muted);">Use code: PLAYWRIGHT2026</div>
            </div>
            <button class="btn btn-primary" onclick="closeEntryAd(this.closest('.modal-overlay'))">Close</button>
        </div>
    `;
    document.body.appendChild(overlay);
    document.getElementById('entry-ad-result').textContent = 'Entry ad modal displayed!';
}

function closeEntryAd(overlay) {
    overlay.remove();
    document.getElementById('entry-ad-result').textContent = 'Entry ad closed!';
}

// EXIT INTENT
let exitTimer = null;
let exitCooldown = false;

document.addEventListener('mouseleave', function(e) {
    if (e.clientY > 0 || exitCooldown) return;
    exitTimer = setTimeout(showExitIntent, 10000);
});

document.addEventListener('mouseenter', function() {
    if (exitTimer) {
        clearTimeout(exitTimer);
        exitTimer = null;
    }
});

function showExitIntent() {
    exitTimer = null;
    exitCooldown = true;
    setTimeout(() => { exitCooldown = false; }, 10000);
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.id = 'exit-modal';
    overlay.innerHTML = `
        <div class="modal-content">
            <div style="font-size:2.5rem;margin-bottom:12px;">👋</div>
            <h2 style="margin:0 0 8px;">Wait! Don't leave yet!</h2>
            <p style="color:var(--text-secondary);margin-bottom:20px;">Are you sure you want to exit? You might miss something amazing.</p>
            <div class="flex gap-2" style="justify-content:center;">
                <button class="btn btn-primary" onclick="document.getElementById('exit-modal').remove(); document.getElementById('exit-result').textContent = 'User decided to stay!';">Stay</button>
                <button class="btn btn-danger" onclick="document.getElementById('exit-modal').remove(); document.getElementById('exit-result').textContent = 'User chose to leave!';">Leave</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
    document.getElementById('exit-result').textContent = 'Exit intent modal triggered!';
}

// REDIRECT
let redirectTimer = null;

function handleRedirect(url) {
    const status = document.getElementById('redirect-status');
    const countdown = document.getElementById('redirect-countdown');
    const result = document.getElementById('redirect-result');
    status.style.display = 'block';
    let seconds = 5;
    countdown.textContent = seconds;

    redirectTimer = setInterval(() => {
        seconds--;
        countdown.textContent = seconds;
        if (seconds <= 0) {
            clearInterval(redirectTimer);
            status.style.display = 'none';
            window.location.href = url;
        }
    }, 1000);

    result.textContent = `Redirecting to: ${url}`;
}

function cancelRedirect() {
    if (redirectTimer) {
        clearInterval(redirectTimer);
        redirectTimer = null;
        document.getElementById('redirect-status').style.display = 'none';
        document.getElementById('redirect-result').textContent = 'Redirect cancelled!';
    }
}

// TYPOS
function checkTypos() {
    const text = document.getElementById('typos-content').textContent;
    const typoList = ['exmaple', 'purpse', 'erors', 'commn', 'recieve', 'definatly', 'seperate', 'occurance', 'enviroment', 'writen', 'contenet', 'presense', 'expressons'];
    const found = typoList.filter(typo => text.toLowerCase().includes(typo));
    document.getElementById('typos-result').textContent = `Found ${found.length} typos: ${found.join(', ')}`;
}

// CHALLENGING DOM
function loadChallengingDOM() {
    const tbody = document.getElementById('challenging-tbody');
    tbody.innerHTML = '';
    const firstNames = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack'];
    const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'];
    const actions = ['edit', 'delete'];

    for (let i = 0; i < 5; i++) {
        const row = document.createElement('tr');
        row.setAttribute('data-index', i);
        const fn = firstNames[Math.floor(Math.random() * firstNames.length)];
        const ln = lastNames[Math.floor(Math.random() * lastNames.length)];
        row.innerHTML = `
            <td>${fn}</td>
            <td>${ln}</td>
            <td>${fn.toLowerCase()}.${ln.toLowerCase()}@example.com</td>
            <td>$${(Math.random() * 100).toFixed(2)}</td>
            <td>http://example.com/${fn.toLowerCase()}</td>
            <td><a href="#" class="badge badge-blue" onclick="event.preventDefault();">${actions[Math.floor(Math.random() * actions.length)]}</a></td>
            <td>
                <button class="btn" style="padding:4px 8px;font-size:0.75rem;" onclick="alert('Edit: ${fn} ${ln}')">Edit</button>
                <button class="btn btn-danger" style="padding:4px 8px;font-size:0.75rem;" onclick="this.closest('tr').remove()">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    }
    document.getElementById('challenging-result').textContent = 'Table loaded with 5 random rows.';
}

// BROKEN IMAGES
function brokenImage(img, label) {
    img.style.display = 'none';
    img.parentElement.innerHTML = '<div style="font-size:2rem;">❌<br><span style="font-size:0.75rem;">' + label + '</span></div>';
}

// Initialize first section
document.addEventListener('DOMContentLoaded', function() {
    initCheckboxes();
});
