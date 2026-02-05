import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import PostCard from '../components/PostCard'
import Loading from '../components/Loading'
import { authService } from '../services/auth'
import { postsService } from '../services/posts'
import toast from 'react-hot-toast'

export default function Profile() {
    const { username } = useParams()
    const [profile, setProfile] = useState(null)
    const [posts, setPosts] = useState([])
    const [loading, setLoading] = useState(true)
    const [activeTab, setActiveTab] = useState('posts')

    useEffect(() => {
        loadProfile()
    }, [username])

    const loadProfile = async () => {
        try {
            const [profileData, postsData] = await Promise.all([
                authService.getUserProfile(username),
                postsService.getUserPosts(username),
            ])
            setProfile(profileData)
            setPosts(postsData.results || postsData)
        } catch (error) {
            toast.error('Failed to load profile')
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return <Loading size="lg" text="Loading profile..." />
    }

    if (!profile) {
        return (
            <div className="card text-center py-12">
                <h2 className="text-xl font-bold text-dark-300">User not found</h2>
                <Link to="/" className="btn-primary mt-4 inline-block">Go Home</Link>
            </div>
        )
    }

    return (
        <div className="max-w-3xl mx-auto">
            {/* Profile header */}
            <div className="card mb-6">
                <div className="flex items-center gap-4">
                    <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-3xl font-bold">
                        {profile.avatar ? (
                            <img src={profile.avatar} alt="" className="w-full h-full rounded-full object-cover" />
                        ) : (
                            profile.username.charAt(0).toUpperCase()
                        )}
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-white">u/{profile.username}</h1>
                        <p className="text-dark-400 text-sm">
                            {profile.karma} karma • Joined {new Date(profile.created_at).toLocaleDateString()}
                        </p>
                    </div>
                </div>

                {profile.bio && (
                    <p className="text-dark-300 mt-4">{profile.bio}</p>
                )}
            </div>

            {/* Tabs */}
            <div className="flex border-b border-dark-700 mb-6">
                <button
                    onClick={() => setActiveTab('posts')}
                    className={`px-4 py-3 border-b-2 transition-colors ${activeTab === 'posts'
                            ? 'border-primary-500 text-primary-400'
                            : 'border-transparent text-dark-400 hover:text-dark-200'
                        }`}
                >
                    Posts
                </button>
            </div>

            {/* Posts */}
            <div className="space-y-4">
                {posts.length > 0 ? (
                    posts.map((post) => (
                        <PostCard key={post.id} post={post} />
                    ))
                ) : (
                    <div className="card text-center py-12">
                        <p className="text-dark-400">No posts yet</p>
                    </div>
                )}
            </div>
        </div>
    )
}
