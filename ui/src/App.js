import Landing from './pages/Landing/Landing';
import Footer from './components/Footer';
import AppRoutes from './AppRoutes';
import AppNavBar from './components/AppNavBar';

function App() {
  return (
    <div className="App">
      <AppNavBar />
      <AppRoutes />
      <Footer />
    </div>
  );
}

export default App;
