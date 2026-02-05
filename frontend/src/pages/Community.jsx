import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import PostCard from '../components/PostCard'
import Loading from '../components/Loading'
import { communitiesService, postsService } from '../services/posts'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function Community() {
    const { slug } = useParams()
    const { isAuthenticated } = useAuth()
    const [community, setCommunity] = useState(null)
    const [posts, setPosts] = useState([])
    const [loading, setLoading] = useState(true)
    const [joining, setJoining] = useState(false)

    useEffect(() => {
        loadCommunity()
    }, [slug])

    const loadCommunity = async () => {
        try {
            const [communityData, postsData] = await Promise.all([
                communitiesService.getCommunity(slug),
                postsService.getPosts({ community: slug }),
            ])
            setCommunity(communityData)
            setPosts(postsData.results || postsData)
        } catch (error) {
            toast.error('Failed to load community')
        } finally {
            setLoading(false)
        }
    }

    const handleJoin = async () => {
        if (!isAuthenticated) {
            toast.error('Please log in to join communities')
            return
        }

        setJoining(true)
        try {
            if (community.is_member) {
                await communitiesService.leaveCommunity(slug)
                setCommunity({ ...community, is_member: false, member_count: community.member_count - 1 })
                toast.success('Left community')
            } else {
                await communitiesService.joinCommunity(slug)
                setCommunity({ ...community, is_member: true, member_count: community.member_count + 1 })
                toast.success('Joined community!')
            }
        } catch (error) {
            toast.error('Action failed')
        } finally {
            setJoining(false)
        }
    }

    if (loading) {
        return <Loading size="lg" text="Loading community..." />
    }

    if (!community) {
        return (
            <div className="card text-center py-12">
                <h2 className="text-xl font-bold text-dark-300">Community not found</h2>
                <Link to="/" className="btn-primary mt-4 inline-block">Go Home</Link>
            </div>
        )
    }

    return (
        <div>
            {/* Banner */}
            <div className="relative h-32 bg-gradient-to-r from-primary-600 to-accent-600 rounded-xl mb-4">
                {community.banner && (
                    <img
                        src={community.banner}
                        alt=""
                        className="w-full h-full object-cover rounded-xl"
                    />
                )}
            </div>

            {/* Header */}
            <div className="card mb-6 -mt-16 relative">
                <div className="flex items-end gap-4">
                    <div className="w-20 h-20 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white text-3xl font-bold border-4 border-dark-900">
                        {community.icon ? (
                            <img src={community.icon} alt="" className="w-full h-full rounded-xl object-cover" />
                        ) : (
                            community.name.charAt(0).toUpperCase()
                        )}
                    </div>
                    <div className="flex-1 pb-1">
                        <h1 className="text-2xl font-bold text-white">c/{community.name}</h1>
                        <p className="text-dark-400 text-sm">{community.member_count} members</p>
                    </div>
                    <button
                        onClick={handleJoin}
                        disabled={joining}
                        className={community.is_member ? 'btn-secondary' : 'btn-primary'}
                    >
                        {joining ? '...' : community.is_member ? 'Joined' : 'Join'}
                    </button>
                </div>

                {community.description && (
                    <p className="text-dark-300 mt-4">{community.description}</p>
                )}
            </div>

            {/* Posts */}
            <div className="space-y-4">
                {posts.length > 0 ? (
                    posts.map((post) => (
                        <PostCard key={post.id} post={post} />
                    ))
                ) : (
                    <div className="card text-center py-12">
                        <p className="text-dark-400 mb-4">No posts in this community yet</p>
                        <Link to="/submit" className="btn-primary">Create the first post</Link>
                    </div>
                )}
            </div>
        </div>
    )
}
