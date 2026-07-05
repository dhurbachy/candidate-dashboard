import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
const queryClient = new QueryClient();
import { BrowserRouter } from 'react-router';
import RouteMain from './routes/routeMain'

function AppContent() {
  

  return (
    <BrowserRouter>
      <RouteMain />
    </BrowserRouter>
  );
}
function App() {
  return (
    <>
      <QueryClientProvider client={queryClient}>
       <AppContent>

       </AppContent>

      </QueryClientProvider>
    </>
  );
}

export default App;
