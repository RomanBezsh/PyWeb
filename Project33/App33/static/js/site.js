class Base64 {
    static #textEncoder = new TextEncoder();
    static #textDecoder = new TextDecoder();

    // https://datatracker.ietf.org/doc/html/rfc4648#section-4
    static encode = (str) => btoa(String.fromCharCode(...Base64.#textEncoder.encode(str)));
    static decode = (str) => Base64.#textDecoder.decode(Uint8Array.from(atob(str), c => c.charCodeAt(0)));
    
    // https://datatracker.ietf.org/doc/html/rfc4648#section-5
    static encodeUrl = (str) => this.encode(str).replace(/\+/g, '-').replace(/\//g, '_'); //.replace(/=+$/, '');
    static decodeUrl = (str) => this.decode(str.replace(/\-/g, '+').replace(/\_/g, '/'));

    static jwtEncodeBody = (header, payload) => this.encodeUrl(JSON.stringify(header)) + '.' + this.encodeUrl(JSON.stringify(payload));
    static jwtDecodePayload = (jwt) => JSON.parse(this.decodeUrl(jwt.split('.')[1]));
}

document.addEventListener('DOMContentLoaded', () => {
    console.log("Script works");
    let btn = document.getElementById("btn-seed");
    if(btn) { btn.addEventListener('click', btnSeedClick); }
    
    btn = document.getElementById("auth-modal-btn");
    if(btn) { btn.addEventListener('click', btnAuthModalClick); }

    btn = document.getElementById("btn-auth-test");
    if(btn) { btn.addEventListener('click', btnAuthTestClick); }

    btn = document.getElementById("btn-auth-no-header");
    if(btn) { btn.addEventListener('click', btnAuthTestNoHeaderClick); }

    btn = document.getElementById("btn-auth-invalid-scheme");
    if(btn) { btn.addEventListener('click', btnAuthInvalidClick); }
});


function btnAuthTestClick() {
    if(!window.auth_token) {
        alert("Потрібно автентифікуватися");
        return;
    }
    const headerVal = 'Bearer ' + window.auth_token;
    console.log('auth test: sending header', headerVal);
    fetch("/test/", {
        headers: {
            "Authorization": headerVal
        }
    }).then(async r => {
        const t = await r.text();
        console.log('відповідь: ', t);
    }).catch(e => console.error('auth test error', e));
}

function btnAuthTestNoHeaderClick() {
    const test_response = fetch("/test/", {}).then(async r => {
        const t = await r.text();
        alert('відповідь : ' + t);
    });
}

function btnAuthInvalidClick() {
    fetch("/test/", {
        headers: {
            "Authorization": "Not Basic"
        }
    }).then(async r => {
        const t = await r.text();
        alert('відповідь: ' + t);
    }).catch(e => console.error(e));
}

function btnAuthModalClick(e) {
    if(e && typeof e.preventDefault === 'function') {
        e.preventDefault();
        e.stopPropagation();
    }
    const loginInput = document.getElementById("auth-modal-login");
    if(!loginInput) throw "auth-modal-login input not found";
    const passwordInput = document.getElementById("auth-modal-password");
    if(!passwordInput) throw "auth-modal-password input not found";
    let isOk = true;
    const login = loginInput.value;
    if(!login || login.includes(':')) {
        loginInput.classList.add("is-invalid");
        isOk = false;
    }
    else {
        loginInput.classList.remove("is-invalid");
    }
    const password = passwordInput.value;
    if(!password || password.length < 3) {
        passwordInput.classList.add("is-invalid");
        isOk = false;
    }
    else {
        passwordInput.classList.remove("is-invalid");
    }
    if(isOk) {
        let userPass = login + ':' + password;
        let credentials = Base64.encode(userPass);
        const headerVal = 'Basic ' + credentials;
        console.log('auth: sending header', headerVal);
        fetch("/auth/", {
            headers: {
                "Authorization": headerVal
            }
        }).then(async r => {
            console.log('auth: response status', r.status);
            if (r.ok) {
                r.text().then(t => {
                    window.auth_token = t;
                    // store base64 credentials for later test requests
                    window.auth_basic = credentials;
                    var myModalEl = document.getElementById('authModal');
                    var modal = bootstrap.Modal.getInstance(myModalEl)
                    modal.hide();
                });
            }
            else {
                let msg = `Помилка автентифікації (status ${r.status})`;
                try {
                    const j = await r.json();
                    msg = j.error || j.message || JSON.stringify(j);
                }
                catch(e) {
                    const t = await r.text().catch(() => null);
                    if(t) msg = t;
                }
                showAuthModalAlert(msg, 'danger');
            }
        }).catch(e => {
            showAuthModalAlert(e?.message || String(e), 'danger');
        });

    }
}

function showAuthModalAlert(text, type) {
    const loginInput = document.getElementById("auth-modal-login");
    const modal = loginInput ? loginInput.closest('.modal') : document.getElementById('auth-modal');
    if(!modal) {
        console.warn('Модальне вікно авторизації не знайдено, неможливо відобразити сповіщення');
        return;
    }

    const existing = modal.querySelector('#auth-modal-alerts');
    if(existing) existing.remove();

    const container = document.createElement('div');
    container.id = 'auth-modal-alerts';
    container.className = 'me-auto d-flex align-items-start';

    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show mb-0`;
    alert.setAttribute('role','alert');
    alert.innerHTML = `<div>${String(text)}</div><button type="button" class="btn-close ms-2" data-bs-dismiss="alert" aria-label="Close"></button>`;

    container.appendChild(alert);

    const placeholder = modal.querySelector('#auth-modal-alerts-placeholder');
    if(placeholder) {
        placeholder.innerHTML = '';
        placeholder.appendChild(container);
        return;
    }

    const footer = modal.querySelector('.modal-footer');
    if(footer) {
        footer.insertBefore(container, footer.firstChild);
    }
    else {
        const body = modal.querySelector('.modal-body') || modal;
        body.insertBefore(container, body.firstChild);
    }
}

function btnSeedClick() {
    if(confirm("Це вельми небезпечна дія. Підтверджуєте?")) {
        fetch("/seed/", {
            method: "PATCH"
        }).then(r => r.json())
        .then(j => {
            console.log(j);
        });
    }
}