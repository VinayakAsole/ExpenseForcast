const API_BASE_URL = '/api';

const API = {
    async get(url) {
        return this.request(url, 'GET');
    },

    async post(url, data) {
        return this.request(url, 'POST', data);
    },

    async put(url, data) {
        return this.request(url, 'PUT', data);
    },

    async delete(url) {
        return this.request(url, 'DELETE');
    },

    async request(url, method, data = null) {
        const token = localStorage.getItem('token');
        const headers = {
            'Content-Type': 'application/json'
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            method,
            headers
        };
        if (data) {
            config.body = JSON.stringify(data);
        }

        const response = await fetch(`${API_BASE_URL}${url}`, config);
        
        let result;
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            result = await response.json();
        } else {
            const text = await response.text();
            result = { error: text || `Error ${response.status}: ${response.statusText}` };
        }

        if (!response.ok) {
            if (response.status === 401 && !url.includes('/auth/login')) {
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                window.location.href = '/login';
            }
            throw { response: { data: result }, status: response.status };
        }

        // Automatic Background Sync to Firebase
        if (method !== 'GET' && !url.includes('/auth') && !url.includes('/sync/firebase-push')) {
            // Trigger sync asynchronously to not block the current operation's response
            setTimeout(() => {
                const syncHeaders = { ...headers };
                fetch(`${API_BASE_URL}/sync/firebase-push`, {
                    method: 'POST',
                    headers: syncHeaders
                }).catch(err => console.error("Realtime Firebase Sync failed:", err));
            }, 100);
        }

        return { data: result };
    }
};
