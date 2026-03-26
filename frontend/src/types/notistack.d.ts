declare module 'notistack' {
  import * as React from 'react';
  export interface OptionsObject {
    variant?: 'default' | 'error' | 'success' | 'warning' | 'info';
    autoHideDuration?: number;
    preventDuplicate?: boolean;
  }
  export type SnackbarKey = string | number;
  export interface SnackbarProviderProps { children?: React.ReactNode; maxSnack?: number; }
  export const SnackbarProvider: React.ComponentType<SnackbarProviderProps>;
  export function useSnackbar(): { enqueueSnackbar: (message: string, options?: OptionsObject) => SnackbarKey };
}
