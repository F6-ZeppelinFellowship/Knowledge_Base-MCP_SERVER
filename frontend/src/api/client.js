import axios from 'axios'

const TOKEN_KEY = 'pkb_access_token'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT bearer token to outgoing requests
client.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Clear token on 401 Unauthorized errors
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
    }
    return Promise.reject(error)
  },
)

export const auth = {
  async login(email, password) {
    const params = new URLSearchParams()
    params.append('username', email)
    params.append('password', password)

    const { data } = await client.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    
    localStorage.setItem(TOKEN_KEY, data.access_token)
    localStorage.setItem('user_email', email)
    return data
  },

  async signup(email, password) {
    await client.post('/auth/signup', {
      username: email,
      password: password,
    })
    return this.login(email, password)
  },

  logout() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem('user_email')
  },

  getUserEmail() {
    return localStorage.getItem('user_email') || ''
  },

  isAuthenticated() {
    return Boolean(localStorage.getItem(TOKEN_KEY))
  },
}

export const documents = {
  list: () => client.get('/documents/list').then((r) => r.data),
  upload: (file, onProgress) => {
    const form = new FormData()
    form.append('file', file)
    return client
      .post('/documents/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (evt) => {
          if (onProgress && evt.total) {
            onProgress(Math.round((evt.loaded / evt.total) * 100))
          }
        },
      })
      .then((r) => r.data)
  },
  // Fixed endpoint path to match @router.delete("/{document_id}") in documents.py
  remove: (documentId) => client.delete(`/documents/${documentId}`).then((r) => r.data),
}

export const search = {
  query: (query, topK = 5) =>
    client.get('/search', { params: { q: query, top_k: topK } }).then((r) => r.data),
}

export default client


