"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

type props = {
  children: React.ReactNode;
};

const queryClient = new QueryClient();

const Provider = ({ children }: props) => {
  return (

      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

export default Provider;
