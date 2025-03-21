import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const App = () => {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://37.140.192.91:8000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login, password }),
      });
      const data = await response.json();
      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
        navigate('/dashboard');
      } else {
        alert('Ошибка входа: ' + JSON.stringify(data));
      }
    } catch (error) {
      alert('Ошибка сети: ' + error);
    }
  };

  return (
    <div style={{ textAlign: 'center', padding: '50px' }}>
      <h1>RUB2B — опт, который работает</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Логин"
          value={login}
          onChange={(e) => setLogin(e.target.value)}
          style={{ display: 'block', margin: '10px auto' }}
        />
        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ display: 'block', margin: '10px auto' }}
        />
        <button type="submit">Войти</button>
      </form>
    </div>
  );
};

export default App;