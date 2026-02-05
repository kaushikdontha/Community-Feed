# Community Feed -  Community Platform

A full-stack web application for community discussions with nested comments, voting, and karma system. Built with React.js frontend and Django REST Framework backend with PostgreSQL database.

## Features

- 🗣️ **Communities** - Create and join topic-based communities (subreddits)
- 📝 **Posts & Voting** - Share content with upvote/downvote system
- 💬 **Threaded Comments** - Nested comment trees with voting support
- ⭐ **Karma System** - Track user reputation with dynamic 24h leaderboard
- 👤 **User Profiles** - Avatars, bios, and activity history
- � **JWT Authentication** - Secure token-based authentication

## Tech Stack

**Frontend:**
- React.js 18
- React Router DOM
- Vite
- Axios
- CSS3

**Backend:**
- Python 3.10+
- Django 5.0
- Django REST Framework
- Simple JWT
- PostgreSQL (prod)

## Screenshots

### Home Feed
Browse posts from all communities with voting and comments.

![Home Feed](frontend/public/screenshots/home-feed.png)

### Post Detail
View full post with threaded comment tree.

![Post Detail](frontend/public/screenshots/post-detail.png)

### Create Post
Easy post creation with community selection.

![Create Post](frontend/public/screenshots/create-post.png)

### User Profile
View user karma, posts, and activity.

![User Profile](frontend/public/screenshots/user-profile.png)

### Leaderboard
24-hour karma leaderboard calculated from transaction history.

![Leaderboard](frontend/public/screenshots/leaderboard.png)

## Project Structure

```
Community-Feed/
├── backend/
│   ├── apps/
│   │   ├── users/           # Auth, karma, leaderboard
│   │   ├── posts/           # Posts + voting
│   │   ├── comments/        # Threaded comments
│   │   └── communities/     # Subreddit-like groups
│   ├── community_feed/      # Django settings
│   ├── seed_data.py         # Test data generator
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/           # Route pages
│   │   ├── services/        # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── EXPLAINER.md             # Technical deep-dive
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- npm or yarn

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/kaushikdontha/community-feed.git
cd community-feed
```

2. **Setup Backend**

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

3. **Setup Frontend**

```bash
cd frontend
npm install
```

### Running the Application

**Start the Backend** (from `backend/` folder)

```bash
python manage.py runserver
```

Server runs on http://localhost:8000

**Start the Frontend** (from `frontend/` folder)

```bash
npm run dev
```

App runs on http://localhost:5173

### Seed Test Data (Optional)

```bash
cd backend
python seed_data.py
```

This creates 6 test users (password: `testpass123`), a General community, and sample posts with comments.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/register/` | User registration |
| POST | `/api/users/token/` | JWT login |
| POST | `/api/users/token/refresh/` | Refresh JWT token |
| GET | `/api/users/me/` | Current user profile |
| GET | `/api/communities/` | List all communities |
| POST | `/api/communities/` | Create community |
| GET | `/api/posts/` | List all posts |
| POST | `/api/posts/` | Create new post |
| GET | `/api/posts/:id/` | Get post detail |
| POST | `/api/posts/:id/vote/` | Vote on post |
| GET | `/api/posts/:id/comments/` | Get post comments |
| POST | `/api/comments/` | Create comment |
| POST | `/api/comments/:id/vote/` | Vote on comment |
| GET | `/api/leaderboard/24h/` | 24h karma leaderboard |
| GET | `/api/leaderboard/all-time/` | All-time leaderboard |

## Test Accounts

After running `seed_data.py`:

| Username | Password | Role |
|----------|----------|------|
| alice | testpass123 | Community creator |
| bob | testpass123 | Active poster |
| charlie | testpass123 | Regular user |
| diana | testpass123 | Regular user |
| eve | testpass123 | Regular user |
| frank | testpass123 | Regular user |

## Environment Variables

For production, create a `.env` file in the `backend/` folder:


## Live Demo

- **Frontend:** [Coming Soon - Vercel deployment]
- **Backend API:** [Coming Soon - Railway deployment]

