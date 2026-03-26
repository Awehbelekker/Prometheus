import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import MainContent from '../components/MainContent';
import './App.css';

const App: React.FC = () => {
  const [selectedItem, setSelectedItem] = useState('dashboard');
  return (
    <div className="app-root" style={{ display: 'flex' }}>
      <Sidebar selectedItem={selectedItem} setSelectedItem={setSelectedItem} />
      <div style={{ flex: 1 }}>
        <MainContent selectedItem={selectedItem} />
      </div>
    </div>
  );
};

export default App;
