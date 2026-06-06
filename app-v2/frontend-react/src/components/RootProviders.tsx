import { TanStackDevtools } from '@tanstack/react-devtools';
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools';
import { QueryClientProvider, QueryClient } from '@tanstack/react-query';
import { ReactQueryDevtoolsPanel } from '@tanstack/react-query-devtools';
import { TooltipProvider } from './ui/tooltip';

export const tanstackQueryClient = new QueryClient();

export function RootProviders({ children }: { children: React.ReactNode; }) {
  return (
    <>
      <QueryClientProvider client={tanstackQueryClient}>
        <TanStackDevtools
          config={{
            position: 'bottom-right',
          }}
          plugins={[
            {
              name: 'Tanstack Router',
              render: <TanStackRouterDevtoolsPanel />,
            },
            {
              name: 'TanStack Query',
              render: <ReactQueryDevtoolsPanel />,
            },
          ]}
        />
        <TooltipProvider>
          {children}
        </TooltipProvider>
      </QueryClientProvider>
    </>
  );
}