import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { Fixture } from './Fixture';
import './style.css';
createRoot(document.getElementById('root')!).render(<BrowserRouter><Fixture /></BrowserRouter>);
