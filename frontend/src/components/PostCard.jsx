import { useState } from 'react'
import { Link } from 'react-router-dom'
import { formatDistanceToNow } from 'date-fns'
import VoteButtons from './VoteButtons'
import { postsService } from '../services/posts'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function PostCard({ post, onVoteUpdate }) {
    const { isAuthenticated } = useAuth()
    const [voteScore, setVoteScore] = useState(post.vote_score)
    const [userVote, setUserVote] = useState(post.user_vote)

    const handleVote = async (voteType) => {
        if (!isAuthenticated) {
            toast.error('Please log in to vote')
            return
        }

        try {
            const result = await postsService.votePost(post.id, voteType)
            setVoteScore(result.vote_score)
            setUserVote(userVote === voteType ? null : voteType)
            if (onVoteUpdate) {
                onVoteUpdate(post.id, result.vote_score)
            }
        } catch (error) {
            toast.error('Failed to vote')
        }
    }

    const timeAgo = formatDistanceToNow(new Date(post.created_at), { addSuffix: true })

    return (
        <article className="card flex gap-3 animate-fade-in">
            {/* Vote buttons */}
            <VoteButtons
                score={voteScore}
                userVote={userVote}
                onUpvote={() => handleVote('up')}
                onDownvote={() => handleVote('down')}
            />

            {/* Content */}
            <div className="flex-1 min-w-0">
                {/* Header */}
                <div className="flex items-center gap-2 text-xs text-dark-400 mb-1">
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
                <Link to={`/post/${post.id}`}>
                    <h2 className="text-lg font-medium text-dark-100 hover:text-primary-400 transition-colors mb-2">
                        {post.is_nsfw && <span className="badge-primary mr-2">NSFW</span>}
                        {post.is_spoiler && <span className="badge-accent mr-2">Spoiler</span>}
                        {post.title}
                    </h2>
                </Link>

                {/* Content preview */}
                {post.post_type === 'text' && post.content && (
                    <p className="text-dark-400 text-sm line-clamp-3 mb-3">
                        {post.content}
                    </p>
                )}

                {post.post_type === 'image' && post.image && (
                    <div className="relative max-h-96 overflow-hidden rounded-lg mb-3">
                        <img
                            src={post.image}
                            alt={post.title}
                            className="w-full object-cover"
                        />
                    </div>
                )}

                {post.post_type === 'link' && post.url && (
                    <a
                        href={post.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1 mb-3"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                        {new URL(post.url).hostname}
                    </a>
                )}

                {/* Footer */}
                <div className="flex items-center gap-4 text-xs text-dark-400">
                    <Link to={`/post/${post.id}`} className="flex items-center gap-1 hover:bg-dark-800 px-2 py-1 rounded transition-colors">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                        <span>{post.comment_count} Comments</span>
                    </Link>
                    <button className="flex items-center gap-1 hover:bg-dark-800 px-2 py-1 rounded transition-colors">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                        </svg>
                        <span>Share</span>
                    </button>
                </div>
            </div>
        </article>
    )
}
