import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import StoryDetailPage from './pages/StoryDetailPage'
import EditPage from './pages/EditPage'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/story/:id" element={<StoryDetailPage />} />
        <Route path="/edit" element={<EditPage />} />
      </Routes>
    </Router>
  )
}

export default App

