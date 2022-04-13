import NavBar from './components/navbar'
import {
  Routes,
  Route,
} from "react-router-dom";
import Dashboard from "./pages/dashboard"
import Settings from "./pages/settings"
import { QueryClient, QueryClientProvider } from 'react-query'

const queryClient = new QueryClient()

function App() {

  return (
    <>
      <NavBar links={[{ "link": "", "label": "Dashboard" }, { "link": "settings", "label": "Settings" }]} />
        <QueryClientProvider client={queryClient}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </QueryClientProvider>
    </>
  )
}

export default App
