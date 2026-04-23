import { BrowserRouter } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import routes from './routes';

function App() {
  return (
    <BrowserRouter>
      <MainLayout />
    </BrowserRouter>
  );
}

export default App;
