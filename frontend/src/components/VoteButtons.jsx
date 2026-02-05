export default function VoteButtons({ score, userVote, onUpvote, onDownvote, vertical = true }) {
    const containerClass = vertical
        ? 'flex flex-col items-center gap-1'
        : 'flex items-center gap-2'

    return (
        <div className={containerClass}>
            {/* Upvote */}
            <button
                onClick={onUpvote}
                className={`p-1 rounded transition-colors ${userVote === 'up'
                        ? 'text-primary-500 bg-primary-500/10'
                        : 'text-dark-400 hover:text-primary-400 hover:bg-dark-800'
                    }`}
                aria-label="Upvote"
            >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 4l-8 8h5v8h6v-8h5z" />
                </svg>
            </button>

            {/* Score */}
            <span className={`text-sm font-bold min-w-[2rem] text-center ${userVote === 'up' ? 'text-primary-500' :
                    userVote === 'down' ? 'text-blue-500' :
                        'text-dark-300'
                }`}>
                {score}
            </span>

            {/* Downvote */}
            <button
                onClick={onDownvote}
                className={`p-1 rounded transition-colors ${userVote === 'down'
                        ? 'text-blue-500 bg-blue-500/10'
                        : 'text-dark-400 hover:text-blue-400 hover:bg-dark-800'
                    }`}
                aria-label="Downvote"
            >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 20l8-8h-5V4H9v8H4z" />
                </svg>
            </button>
        </div>
    )
}
