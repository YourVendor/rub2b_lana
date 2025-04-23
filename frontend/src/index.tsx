import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import Dashboard from './components/Dashboard';
import Admin from './pages/Admin';
import Moderator from './pages/Moderator';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import ModeratorItemToGoods from "./pages/Moderator_item_to_goods";

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/moderator" element={<Moderator />} />
        <Route path="/moderator-item-to-goods" element={<ModeratorItemToGoods />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);