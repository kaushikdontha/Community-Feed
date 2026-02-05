import { useState } from 'react'
import { formatDistanceToNow } from 'date-fns'
import { Link } from 'react-router-dom'
import VoteButtons from './VoteButtons'
import { commentsService } from '../services/posts'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function CommentThread({ comment, postId, onReplyAdded }) {
    const { user, isAuthenticated } = useAuth()
    const [showReplyForm, setShowReplyForm] = useState(false)
    const [replyContent, setReplyContent] = useState('')
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [voteScore, setVoteScore] = useState(comment.vote_score)
    const [userVote, setUserVote] = useState(comment.user_vote)
    const [replies, setReplies] = useState(comment.replies || [])

    const handleVote = async (voteType) => {
        if (!isAuthenticated) {
            toast.error('Please log in to vote')
            return
        }

        try {
            const result = await commentsService.voteComment(comment.id, voteType)
            setVoteScore(result.vote_score)
            setUserVote(userVote === voteType ? null : voteType)
        } catch (error) {
            toast.error('Failed to vote')
        }
    }

    const handleReply = async (e) => {
        e.preventDefault()
        if (!replyContent.trim()) return

        setIsSubmitting(true)
        try {
            const newComment = await commentsService.createComment({
                content: replyContent,
                post: postId,
                parent: comment.id,
            })
            setReplies([...replies, { ...newComment, replies: [] }])
            setReplyContent('')
            setShowReplyForm(false)
            toast.success('Reply posted!')
            if (onReplyAdded) onReplyAdded()
        } catch (error) {
            toast.error('Failed to post reply')
        } finally {
            setIsSubmitting(false)
        }
    }

    const timeAgo = formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })

    if (comment.is_deleted) {
        return (
            <div className="pl-4 border-l-2 border-dark-700">
                <p className="text-dark-500 italic text-sm">[deleted]</p>
                {replies.length > 0 && (
                    <div className="mt-3 space-y-3">
                        {replies.map((reply) => (
                            <CommentThread
                                key={reply.id}
                                comment={reply}
                                postId={postId}
                                onReplyAdded={onReplyAdded}
                            />
                        ))}
                    </div>
                )}
            </div>
        )
    }

    return (
        <div className="animate-fade-in">
            <div className="flex gap-3">
                {/* Vote buttons (horizontal for comments) */}
                <div className="hidden sm:block">
                    <VoteButtons
                        score={voteScore}
                        userVote={userVote}
                        onUpvote={() => handleVote('up')}
                        onDownvote={() => handleVote('down')}
                    />
                </div>

                <div className="flex-1">
                    {/* Header */}
                    <div className="flex items-center gap-2 text-xs text-dark-400 mb-1">
                        <Link to={`/u/${comment.author}`} className="font-medium text-dark-200 hover:text-primary-400">
                            {comment.author}
                        </Link>
                        <span>•</span>
                        <span>{timeAgo}</span>
                    </div>

                    {/* Content */}
                    <p className="text-dark-200 text-sm whitespace-pre-wrap mb-2">
                        {comment.content}
                    </p>

                    {/* Actions */}
                    <div className="flex items-center gap-3 text-xs">
                        {/* Mobile vote buttons */}
                        <div className="sm:hidden flex items-center gap-1">
                            <VoteButtons
                                score={voteScore}
                                userVote={userVote}
                                onUpvote={() => handleVote('up')}
                                onDownvote={() => handleVote('down')}
                                vertical={false}
                            />
                        </div>

                        {isAuthenticated && (
                            <button
                                onClick={() => setShowReplyForm(!showReplyForm)}
                                className="text-dark-400 hover:text-primary-400 transition-colors"
                            >
                                Reply
                            </button>
                        )}
                    </div>

                    {/* Reply form */}
                    {showReplyForm && (
                        <form onSubmit={handleReply} className="mt-3">
                            <textarea
                                value={replyContent}
                                onChange={(e) => setReplyContent(e.target.value)}
                                placeholder="Write a reply..."
                                className="input text-sm min-h-[80px] resize-y"
                                required
                            />
                            <div className="flex gap-2 mt-2">
                                <button type="submit" disabled={isSubmitting} className="btn-primary text-sm py-1">
                                    {isSubmitting ? 'Posting...' : 'Reply'}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowReplyForm(false)}
                                    className="btn-ghost text-sm py-1"
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    )}
                </div>
            </div>

            {/* Nested replies */}
            {replies.length > 0 && (
                <div className="ml-4 mt-3 pl-4 border-l-2 border-dark-700 space-y-3">
                    {replies.map((reply) => (
                        <CommentThread
                            key={reply.id}
                            comment={reply}
                            postId={postId}
                            onReplyAdded={onReplyAdded}
                        />
                    ))}
                </div>
            )}
        </div>
    )
}
