import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Footer from './components/Footer'
import Sidebar from './components/Sidebar'
import ScrollToTopButton from './components/ScrollToTop'
import HomePage from './pages/HomePage'
import ProductPage from './pages/ProductPage'
import CategoryPage from './pages/CategoryPage'
import SegmentPage from './pages/SegmentPage'
import AdminPage from './pages/AdminPage'
import './App.css'

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-wrapper">
        <Header />
        <div className="app-body">
          <Sidebar />
          <main className="app-main">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/produto/:id" element={<ProductPage />} />
              <Route path="/segmento/:slug" element={<SegmentPage />} />
              <Route path="/categoria/:slug" element={<CategoryPage />} />
              <Route path="/admin" element={<AdminPage />} />
            </Routes>
          </main>
        </div>
        <Footer />
        <ScrollToTopButton />
      </div>
    </BrowserRouter>
  )
}
