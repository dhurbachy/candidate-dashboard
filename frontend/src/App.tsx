import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
const queryClient = new QueryClient();
import { BrowserRouter } from 'react-router';
import RouteMain from './routes/routeMain'
import { AuthProvider } from './context/authContext';
import { Toaster } from 'sonner';
import {useAxiosInterceptor} from "./utils/auth";

function AppContent() {
  
useAxiosInterceptor()
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
        <AuthProvider>

        
       <AppContent />
       </AuthProvider>


      </QueryClientProvider>
      <Toaster position="top-right" richColors />
    </>
  );
}

export default App;
