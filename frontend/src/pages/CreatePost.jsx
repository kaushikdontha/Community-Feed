import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { postsService, communitiesService } from '../services/posts'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function CreatePost() {
    const { isAuthenticated } = useAuth()
    const navigate = useNavigate()
    const [communities, setCommunities] = useState([])
    const [postType, setPostType] = useState('text')
    const [title, setTitle] = useState('')
    const [content, setContent] = useState('')
    const [url, setUrl] = useState('')
    const [community, setCommunity] = useState('')
    const [isNsfw, setIsNsfw] = useState(false)
    const [isSpoiler, setIsSpoiler] = useState(false)
    const [isSubmitting, setIsSubmitting] = useState(false)

    useEffect(() => {
        if (!isAuthenticated) {
            toast.error('Please log in to create a post')
            navigate('/login')
            return
        }
        loadCommunities()
    }, [isAuthenticated])

    const loadCommunities = async () => {
        try {
            const data = await communitiesService.getCommunities()
            setCommunities(data.results || data)
        } catch (error) {
            console.error('Failed to load communities:', error)
        }
    }

    const handleSubmit = async (e) => {
        e.preventDefault()

        if (!community) {
            toast.error('Please select a community')
            return
        }

        setIsSubmitting(true)

        try {
            const postData = {
                title,
                post_type: postType,
                community: parseInt(community),
                is_nsfw: isNsfw,
                is_spoiler: isSpoiler,
            }

            if (postType === 'text') {
                postData.content = content
            } else if (postType === 'link') {
                postData.url = url
            }

            const newPost = await postsService.createPost(postData)
            toast.success('Post created!')
            navigate(`/post/${newPost.id}`)
        } catch (error) {
            const message = error.response?.data?.detail || 'Failed to create post'
            toast.error(message)
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <div className="max-w-2xl mx-auto">
            <h1 className="text-2xl font-bold text-white mb-6">Create a Post</h1>

            <div className="card">
                {/* Community selector */}
                <div className="mb-6">
                    <label className="block text-sm font-medium text-dark-300 mb-2">
                        Choose a community
                    </label>
                    <select
                        value={community}
                        onChange={(e) => setCommunity(e.target.value)}
                        className="input"
                        required
                    >
                        <option value="">Select a community</option>
                        {communities.map((c) => (
                            <option key={c.id} value={c.id}>
                                c/{c.name}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Post type tabs */}
                <div className="flex border-b border-dark-700 mb-6">
                    {[
                        { type: 'text', label: 'Text', icon: 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z' },
                        { type: 'link', label: 'Link', icon: 'M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1' },
                    ].map(({ type, label, icon }) => (
                        <button
                            key={type}
                            type="button"
                            onClick={() => setPostType(type)}
                            className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${postType === type
                                    ? 'border-primary-500 text-primary-400'
                                    : 'border-transparent text-dark-400 hover:text-dark-200'
                                }`}
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={icon} />
                            </svg>
                            {label}
                        </button>
                    ))}
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <input
                            type="text"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            placeholder="Title"
                            className="input text-lg"
                            maxLength={300}
                            required
                        />
                        <p className="text-xs text-dark-500 mt-1 text-right">{title.length}/300</p>
                    </div>

                    {postType === 'text' && (
                        <div className="mb-4">
                            <textarea
                                value={content}
                                onChange={(e) => setContent(e.target.value)}
                                placeholder="Text (optional)"
                                className="input min-h-[200px] resize-y"
                            />
                        </div>
                    )}

                    {postType === 'link' && (
                        <div className="mb-4">
                            <input
                                type="url"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                placeholder="URL"
                                className="input"
                                required
                            />
                        </div>
                    )}

                    {/* Flags */}
                    <div className="flex gap-4 mb-6">
                        <label className="flex items-center gap-2 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={isNsfw}
                                onChange={(e) => setIsNsfw(e.target.checked)}
                                className="w-4 h-4 rounded border-dark-600 bg-dark-800 text-primary-500 focus:ring-primary-500"
                            />
                            <span className="text-sm text-dark-300">NSFW</span>
                        </label>
                        <label className="flex items-center gap-2 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={isSpoiler}
                                onChange={(e) => setIsSpoiler(e.target.checked)}
                                className="w-4 h-4 rounded border-dark-600 bg-dark-800 text-accent-500 focus:ring-accent-500"
                            />
                            <span className="text-sm text-dark-300">Spoiler</span>
                        </label>
                    </div>

                    <div className="flex justify-end gap-3">
                        <button
                            type="button"
                            onClick={() => navigate(-1)}
                            className="btn-ghost"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="btn-primary"
                        >
                            {isSubmitting ? 'Posting...' : 'Post'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
