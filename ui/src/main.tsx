import React from 'react'
import ReactDOM from 'react-dom'
import './index.css'
import App from './App'
import { MantineProvider } from '@mantine/core'
import { ModalsProvider } from '@mantine/modals'
import { NotificationsProvider } from '@mantine/notifications'
import { BrowserRouter } from 'react-router-dom'

ReactDOM.render(
  <React.StrictMode>
    <MantineProvider>
      <ModalsProvider>
        <NotificationsProvider>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </NotificationsProvider>
      </ModalsProvider>
    </MantineProvider>
  </React.StrictMode>,
  document.getElementById('root')
)
