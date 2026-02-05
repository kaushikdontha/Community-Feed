import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import PostCard from '../components/PostCard'
import Loading from '../components/Loading'
import { postsService, communitiesService } from '../services/posts'
import toast from 'react-hot-toast'

export default function Home() {
    const [posts, setPosts] = useState([])
    const [communities, setCommunities] = useState([])
    const [loading, setLoading] = useState(true)
    const [sortBy, setSortBy] = useState('new')

    useEffect(() => {
        loadData()
    }, [sortBy])

    const loadData = async () => {
        try {
            const [postsData, communitiesData] = await Promise.all([
                postsService.getPosts({ sort: sortBy }),
                communitiesService.getCommunities(),
            ])
            setPosts(postsData.results || postsData)
            setCommunities(communitiesData.results || communitiesData)
        } catch (error) {
            toast.error('Failed to load feed')
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return <Loading size="lg" text="Loading feed..." />
    }

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main feed */}
            <div className="lg:col-span-2 space-y-4">
                {/* Sort tabs */}
                <div className="card flex gap-2 p-2">
                    {['hot', 'new', 'top'].map((sort) => (
                        <button
                            key={sort}
                            onClick={() => setSortBy(sort)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${sortBy === sort
                                    ? 'bg-primary-600 text-white'
                                    : 'text-dark-400 hover:bg-dark-800 hover:text-dark-200'
                                }`}
                        >
                            {sort.charAt(0).toUpperCase() + sort.slice(1)}
                        </button>
                    ))}
                </div>

                {/* Posts */}
                {posts.length > 0 ? (
                    <div className="space-y-4">
                        {posts.map((post) => (
                            <PostCard key={post.id} post={post} />
                        ))}
                    </div>
                ) : (
                    <div className="card text-center py-12">
                        <svg className="w-16 h-16 text-dark-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                        </svg>
                        <h3 className="text-lg font-medium text-dark-300 mb-2">No posts yet</h3>
                        <p className="text-dark-500 mb-4">Be the first to post something!</p>
                        <Link to="/submit" className="btn-primary">Create Post</Link>
                    </div>
                )}
            </div>

            {/* Sidebar */}
            <aside className="hidden lg:block space-y-4">
                {/* Welcome card */}
                <div className="card bg-gradient-to-br from-primary-600/20 to-accent-600/20 border-primary-600/30">
                    <h2 className="text-lg font-bold text-white mb-2">Welcome to Community Feed!</h2>
                    <p className="text-dark-300 text-sm mb-4">
                        Join communities, share your thoughts, and engage in discussions.
                    </p>
                    <Link to="/submit" className="btn-primary w-full text-center block">
                        Create Post
                    </Link>
                </div>

                {/* Communities */}
                <div className="card">
                    <h3 className="font-bold text-dark-100 mb-3">Communities</h3>
                    {communities.length > 0 ? (
                        <div className="space-y-2">
                            {communities.slice(0, 5).map((community) => (
                                <Link
                                    key={community.id}
                                    to={`/c/${community.slug}`}
                                    className="flex items-center gap-3 p-2 rounded-lg hover:bg-dark-800 transition-colors"
                                >
                                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-sm font-bold">
                                        {community.name.charAt(0).toUpperCase()}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="font-medium text-dark-200 text-sm truncate">c/{community.name}</p>
                                        <p className="text-dark-500 text-xs">{community.member_count} members</p>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    ) : (
                        <p className="text-dark-500 text-sm">No communities yet</p>
                    )}
                </div>
            </aside>
        </div>
    )
}
