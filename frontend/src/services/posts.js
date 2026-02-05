import api from './api'

export const postsService = {
    async getPosts(params = {}) {
        const response = await api.get('/posts/', { params })
        return response.data
    },

    async getPost(id) {
        const response = await api.get(`/posts/${id}/`)
        return response.data
    },

    async createPost(data) {
        const response = await api.post('/posts/', data)
        return response.data
    },

    async updatePost(id, data) {
        const response = await api.patch(`/posts/${id}/`, data)
        return response.data
    },

    async deletePost(id) {
        await api.delete(`/posts/${id}/`)
    },

    async votePost(id, voteType) {
        const response = await api.post(`/posts/${id}/vote/`, { vote_type: voteType })
        return response.data
    },

    async getUserPosts(username) {
        const response = await api.get(`/posts/user/${username}/`)
        return response.data
    },
}

export const commentsService = {
    async getComments(postId, sort = 'best') {
        const response = await api.get(`/comments/post/${postId}/`, { params: { sort } })
        return response.data
    },

    async createComment(data) {
        const response = await api.post('/comments/', data)
        return response.data
    },

    async updateComment(id, content) {
        const response = await api.patch(`/comments/${id}/`, { content })
        return response.data
    },

    async deleteComment(id) {
        await api.delete(`/comments/${id}/`)
    },

    async voteComment(id, voteType) {
        const response = await api.post(`/comments/${id}/vote/`, { vote_type: voteType })
        return response.data
    },
}

export const communitiesService = {
    async getCommunities() {
        const response = await api.get('/communities/')
        return response.data
    },

    async getCommunity(slug) {
        const response = await api.get(`/communities/${slug}/`)
        return response.data
    },

    async createCommunity(data) {
        const response = await api.post('/communities/', data)
        return response.data
    },

    async joinCommunity(slug) {
        const response = await api.post(`/communities/${slug}/join/`)
        return response.data
    },

    async leaveCommunity(slug) {
        const response = await api.post(`/communities/${slug}/leave/`)
        return response.data
    },
}
