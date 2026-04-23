import { createBrowserRouter, Navigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import Home from '../pages/Home';
import CardExercise from '../pages/CardExercise';
import NumberExercise from '../pages/NumberExercise';
import MemoryPalace from '../pages/MemoryPalace';

export const routes = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/card-exercise" replace />,
      },
      {
        path: 'home',
        element: <Home />,
      },
      {
        path: 'card-exercise',
        element: <CardExercise />,
      },
      {
        path: 'number-exercise',
        element: <NumberExercise />,
      },
      {
        path: 'memory-palace',
        element: <MemoryPalace />,
      },
    ],
  },
]);

export default routes;
