import { Routes, Route } from 'react-router-dom';
import VideoList from './components/VideoList';
import VideoForm from './components/VideoForm';
import Fields from './components/Fields';

function App() {
  return (
    <Routes>
      <Route path="/" element={<VideoList />} />
      <Route path="/videos/new" element={<VideoForm />} />
      <Route path="/videos/:id/edit" element={<VideoForm />} />
      <Route path="/fields" element={<Fields />} />
    </Routes>
  );
}

export default App;
