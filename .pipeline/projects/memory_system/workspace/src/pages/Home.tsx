import { Link } from 'react-router-dom';
import './Home.css';

const Home = () => {
  return (
    <div className="home-page">
      <h1>Welcome to Memory System</h1>
      <p className="tagline">Train your memory with proven techniques inspired by "Moonwalking with Einstein"</p>
      
      <div className="features">
        <div className="feature-card">
          <h2>🎯 Card Matching</h2>
          <p>Practice your memory with card matching exercises. Start with a few pairs and gradually increase the difficulty.</p>
          <Link to="/card-exercise" className="btn btn-primary">Start Exercise</Link>
        </div>
        
        <div className="feature-card">
          <h2>🔢 Number Sequences</h2>
          <p>Train your working memory with number sequence exercises. Remember increasingly long sequences of numbers.</p>
          <Link to="/number-exercise" className="btn btn-primary">Start Exercise</Link>
        </div>
        
        <div className="feature-card">
          <h2>🏰 Memory Palaces</h2>
          <p>Build your own memory palaces using the memory palace technique. Place items in virtual locations to remember them.</p>
          <Link to="/memory-palace" className="btn btn-primary">Create Palace</Link>
        </div>
      </div>
      
      <div className="musical-wheel-section">
        <h2>🎨 Musical Wheel Visualizer</h2>
        <p>Experience our unique musical wheel visualization that helps you remember cards and numbers through interactive rotation and selection.</p>
        <Link to="/card-exercise" className="btn btn-secondary">Try the Wheel</Link>
      </div>
    </div>
  );
};

export default Home;
