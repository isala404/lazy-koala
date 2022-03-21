import { Container, MantineProvider } from '@mantine/core';
import { ModalsProvider } from '@mantine/modals';
import NavBar from './componentes/navbar'
import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";
import Dashboard from "./pages/dashboard"
import Settings from "./pages/settings"
import { QueryClient, QueryClientProvider } from 'react-query'
import { NotificationsProvider } from '@mantine/notifications';

const queryClient = new QueryClient()

function App() {
  
  return (
    <>
    <MantineProvider>
      <ModalsProvider>
        <NotificationsProvider>
          <BrowserRouter>
            <NavBar links={[{ "link": "", "label": "Dashboard" }, { "link": "settings", "label": "Settings" }]} />
            <Container>
              <QueryClientProvider client={queryClient}>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </QueryClientProvider>
            </Container>
          </BrowserRouter>
        </NotificationsProvider>
      </ModalsProvider>
    </MantineProvider>
    </>
  )
}

export default App
