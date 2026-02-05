import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
    const { user, isAuthenticated, logout } = useAuth()

    return (
        <nav className="sticky top-0 z-50 bg-dark-900/95 backdrop-blur-sm border-b border-dark-800">
            <div className="container mx-auto px-4 max-w-5xl">
                <div className="flex items-center justify-between h-14">
                    {/* Logo */}
                    <Link to="/" className="flex items-center gap-2 text-xl font-bold text-white hover:text-primary-400 transition-colors">
                        <svg className="w-8 h-8 text-primary-500" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                        </svg>
                        <span className="hidden sm:inline">Community Feed</span>
                    </Link>

                    {/* Search */}
                    <div className="flex-1 max-w-md mx-4 hidden md:block">
                        <div className="relative">
                            <input
                                type="text"
                                placeholder="Search..."
                                className="input pl-10 py-1.5 text-sm"
                            />
                            <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                        </div>
                    </div>

                    {/* Right side */}
                    <div className="flex items-center gap-2">
                        {isAuthenticated ? (
                            <>
                                <Link to="/submit" className="btn-primary text-sm py-1.5">
                                    + Create Post
                                </Link>
                                <div className="relative group">
                                    <button className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-dark-800 transition-colors">
                                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white font-medium">
                                            {user?.username?.charAt(0).toUpperCase()}
                                        </div>
                                        <span className="hidden sm:inline text-sm text-dark-200">{user?.username}</span>
                                    </button>
                                    {/* Dropdown */}
                                    <div className="absolute right-0 top-full mt-1 w-48 bg-dark-800 border border-dark-700 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                                        <Link to={`/u/${user?.username}`} className="block px-4 py-2 text-sm text-dark-200 hover:bg-dark-700 rounded-t-lg">
                                            Profile
                                        </Link>
                                        <div className="border-t border-dark-700" />
                                        <button onClick={logout} className="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-dark-700 rounded-b-lg">
                                            Sign Out
                                        </button>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <>
                                <Link to="/login" className="btn-ghost text-sm py-1.5">
                                    Log In
                                </Link>
                                <Link to="/register" className="btn-primary text-sm py-1.5">
                                    Sign Up
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    )
}
