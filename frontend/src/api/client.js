import axios from 'axios'

const TOKEN_KEY = 'pkb_access_token'
const USER_EMAIL_KEY = 'user_email'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT bearer token automatically to ALL outgoing requests
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
      localStorage.removeItem(USER_EMAIL_KEY)
    }
    return Promise.reject(error)
  },
)

export const auth = {
  login: async (email, password) => {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)

    const res = await client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })

    if (res.data.access_token) {
      localStorage.setItem(TOKEN_KEY, res.data.access_token)
      localStorage.setItem(USER_EMAIL_KEY, email)
    }
    return res.data
  },

  register: async (email, password) => {
    await client.post('/auth/signup', {
      username: email,
      password: password,
    })

    return auth.login(email, password)
  },

  logout: () => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_EMAIL_KEY)
  },

  isAuthenticated: () => !!localStorage.getItem(TOKEN_KEY),
  getUserEmail: () => localStorage.getItem(USER_EMAIL_KEY) || '',
}

export const documents = {
  list: async () => {
    const res = await client.get('/documents/list')
    const data = res.data
    if (Array.isArray(data)) return data
    if (Array.isArray(data?.documents)) return data.documents
    if (Array.isArray(data?.sources)) return data.sources
    if (Array.isArray(data?.files)) return data.files
    return []
  },

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

  remove: (documentId) => client.delete(`/documents/${documentId}`).then((r) => r.data),
}

export const search = {
  query: async (queryText, topK = 5) => {
    // Uses client (axios) so Authorization Bearer header is automatically attached
    const res = await client.get('/search', {
      params: {
        q: queryText,
        top_k: topK,
      },
    })
    return res.data
  },
}

export default client