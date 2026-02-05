import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import PostDetail from './pages/PostDetail'
import CreatePost from './pages/CreatePost'
import Community from './pages/Community'
import Profile from './pages/Profile'

function App() {
    return (
        <div className="min-h-screen bg-dark-950">
            <Navbar />
            <main className="container mx-auto px-4 py-6 max-w-5xl">
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/submit" element={<CreatePost />} />
                    <Route path="/post/:id" element={<PostDetail />} />
                    <Route path="/c/:slug" element={<Community />} />
                    <Route path="/u/:username" element={<Profile />} />
                </Routes>
            </main>
        </div>
    )
}

export default App
