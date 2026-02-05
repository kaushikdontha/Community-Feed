import api from './api'

export const authService = {
    async login(username, password) {
        const response = await api.post('/token/', { username, password })
        return response.data
    },

    async register(username, email, password) {
        const response = await api.post('/users/register/', {
            username,
            email,
            password,
            password_confirm: password,
        })
        return response.data
    },

    async getCurrentUser() {
        const response = await api.get('/users/me/')
        return response.data
    },

    async updateProfile(data) {
        const response = await api.patch('/users/profile/', data)
        return response.data
    },

    async getUserProfile(username) {
        const response = await api.get(`/users/${username}/`)
        return response.data
    },
}
