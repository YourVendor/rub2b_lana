import React, { useState } from 'react';

const App = () => {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const response = await fetch('http://127.0.0.1:8000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ login, password }),
    });
    const data = await response.json();
    console.log(data); // Пока токен тут, потом в localStorage
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