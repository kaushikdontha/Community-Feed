import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { formatDistanceToNow } from 'date-fns'
import VoteButtons from '../components/VoteButtons'
import CommentThread from '../components/CommentThread'
import Loading from '../components/Loading'
import { postsService, commentsService } from '../services/posts'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function PostDetail() {
    const { id } = useParams()
    const { isAuthenticated } = useAuth()
    const [post, setPost] = useState(null)
    const [comments, setComments] = useState([])
    const [loading, setLoading] = useState(true)
    const [newComment, setNewComment] = useState('')
    const [submitting, setSubmitting] = useState(false)
    const [sortBy, setSortBy] = useState('best')

    useEffect(() => {
        loadPost()
    }, [id])

    useEffect(() => {
        if (post) {
            loadComments()
        }
    }, [post, sortBy])

    const loadPost = async () => {
        try {
            const postData = await postsService.getPost(id)
            setPost(postData)
        } catch (error) {
            toast.error('Failed to load post')
        } finally {
            setLoading(false)
        }
    }

    const loadComments = async () => {
        try {
            const commentsData = await commentsService.getComments(id, sortBy)
            setComments(commentsData.results || commentsData)
        } catch (error) {
            console.error('Failed to load comments:', error)
        }
    }

    const handleVote = async (voteType) => {
        if (!isAuthenticated) {
            toast.error('Please log in to vote')
            return
        }

        try {
            const result = await postsService.votePost(id, voteType)
            setPost({ ...post, vote_score: result.vote_score })
        } catch (error) {
            toast.error('Failed to vote')
        }
    }

    const handleComment = async (e) => {
        e.preventDefault()
        if (!newComment.trim()) return

        setSubmitting(true)
        try {
            await commentsService.createComment({
                content: newComment,
                post: parseInt(id),
            })
            setNewComment('')
            loadComments()
            setPost({ ...post, comment_count: post.comment_count + 1 })
            toast.success('Comment posted!')
        } catch (error) {
            toast.error('Failed to post comment')
        } finally {
            setSubmitting(false)
        }
    }

    if (loading) {
        return <Loading size="lg" text="Loading post..." />
    }

    if (!post) {
        return (
            <div className="card text-center py-12">
                <h2 className="text-xl font-bold text-dark-300">Post not found</h2>
                <Link to="/" className="btn-primary mt-4 inline-block">Go Home</Link>
            </div>
        )
    }

    const timeAgo = formatDistanceToNow(new Date(post.created_at), { addSuffix: true })

    return (
        <div className="max-w-3xl mx-auto">
            {/* Post */}
            <article className="card mb-6">
                <div className="flex gap-4">
                    {/* Vote buttons */}
                    <VoteButtons
                        score={post.vote_score}
                        userVote={post.user_vote}
                        onUpvote={() => handleVote('up')}
                        onDownvote={() => handleVote('down')}
                    />

                    {/* Content */}
                    <div className="flex-1">
                        {/* Header */}
                        <div className="flex items-center gap-2 text-sm text-dark-400 mb-2">
                            <Link to={`/c/${post.community_slug}`} className="font-medium text-dark-200 hover:text-primary-400">
                                c/{post.community_name}
                            </Link>
                            <span>•</span>
                            <span>Posted by</span>
                            <Link to={`/u/${post.author}`} className="hover:text-primary-400">
                                u/{post.author}
                            </Link>
                            <span>•</span>
                            <span>{timeAgo}</span>
                        </div>

                        {/* Title */}
                        <h1 className="text-2xl font-bold text-white mb-4">
                            {post.is_nsfw && <span className="badge-primary mr-2 text-sm">NSFW</span>}
                            {post.is_spoiler && <span className="badge-accent mr-2 text-sm">Spoiler</span>}
                            {post.title}
                        </h1>

                        {/* Content */}
                        {post.post_type === 'text' && post.content && (
                            <div className="prose prose-invert max-w-none mb-4">
                                <p className="text-dark-200 whitespace-pre-wrap">{post.content}</p>
                            </div>
                        )}

                        {post.post_type === 'image' && post.image && (
                            <div className="mb-4">
                                <img
                                    src={post.image}
                                    alt={post.title}
                                    className="max-w-full rounded-lg"
                                />
                            </div>
                        )}

                        {post.post_type === 'link' && post.url && (
                            <a
                                href={post.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-2 text-primary-400 hover:text-primary-300 mb-4"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                                {post.url}
                            </a>
                        )}

                        {/* Stats */}
                        <div className="flex items-center gap-4 text-sm text-dark-400 pt-4 border-t border-dark-700">
                            <span>{post.comment_count} comments</span>
                        </div>
                    </div>
                </div>
            </article>

            {/* Comment form */}
            {isAuthenticated ? (
                <form onSubmit={handleComment} className="card mb-6">
                    <textarea
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                        placeholder="What are your thoughts?"
                        className="input min-h-[100px] resize-y mb-3"
                        required
                    />
                    <div className="flex justify-end">
                        <button type="submit" disabled={submitting} className="btn-primary">
                            {submitting ? 'Posting...' : 'Comment'}
                        </button>
                    </div>
                </form>
            ) : (
                <div className="card mb-6 text-center py-4">
                    <p className="text-dark-400">
                        <Link to="/login" className="text-primary-400 hover:text-primary-300">Log in</Link>
                        {' '}to leave a comment
                    </p>
                </div>
            )}

            {/* Comments */}
            <div className="card">
                {/* Sort options */}
                <div className="flex items-center gap-2 mb-4 pb-4 border-b border-dark-700">
                    <span className="text-sm text-dark-400">Sort by:</span>
                    {['best', 'new', 'old'].map((sort) => (
                        <button
                            key={sort}
                            onClick={() => setSortBy(sort)}
                            className={`px-3 py-1 rounded text-sm transition-colors ${sortBy === sort
                                    ? 'bg-primary-600 text-white'
                                    : 'text-dark-400 hover:bg-dark-800'
                                }`}
                        >
                            {sort.charAt(0).toUpperCase() + sort.slice(1)}
                        </button>
                    ))}
                </div>

                {/* Comment list */}
                {comments.length > 0 ? (
                    <div className="space-y-4">
                        {comments.map((comment) => (
                            <CommentThread
                                key={comment.id}
                                comment={comment}
                                postId={parseInt(id)}
                                onReplyAdded={() => setPost({ ...post, comment_count: post.comment_count + 1 })}
                            />
                        ))}
                    </div>
                ) : (
                    <p className="text-center text-dark-500 py-8">No comments yet. Be the first!</p>
                )}
            </div>
        </div>
    )
}
