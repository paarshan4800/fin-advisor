import Landing from "./pages/Landing/Landing";
import Footer from "./components/Footer";
import AppRoutes from "./AppRoutes";
import AppNavBar from "./components/AppNavBar";
import useUsers from "./hooks/useUsers";

function App() {
  const { usersData } = useUsers();

  return (
    <div className="App">
      <AppNavBar usersData={usersData} />
      <AppRoutes />
      <Footer />
    </div>
  );
}

export default App;
