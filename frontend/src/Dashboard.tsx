import React, { useEffect, useState } from 'react';

const Dashboard = () => {
  const [message, setMessage] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetch('http://127.0.0.1:8000/dashboard', {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((data) => setMessage(data.message))
        .catch((err) => setMessage('Ошибка: ' + err));
    } else {
      setMessage('Нет токена, войди заново');
    }
  }, []);

  return <h1>{message}</h1>;
};

export default Dashboard;