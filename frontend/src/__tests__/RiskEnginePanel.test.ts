export {};

jest.mock('notistack', () => ({
  SnackbarProvider: ({ children }: any) => children,
  useSnackbar: () => ({ enqueueSnackbar: jest.fn() })
}));
describe('RiskEnginePanel smoke test', () => {
  test('module loads', () => {
    const mod = require('../components/RiskEnginePanel');
    expect(mod).toBeTruthy();
    expect(mod.default).toBeDefined();
  });
});
