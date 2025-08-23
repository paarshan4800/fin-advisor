import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#90caf9" },         // soft blue accent (MUI default dark)
    background: {
      default: "#0f1115",                 // subtle dark
      paper: "#151820",                   // slightly lighter for cards/appbar
    },
    text: { primary: "#e5e7eb", secondary: "#a6adbb" },
  },
  shape: { borderRadius: 10 },
  typography: {
    fontFamily:
      'Inter, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial',
    h3: { fontWeight: 700, letterSpacing: -0.2 },
    body1: { lineHeight: 1.65 },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: { margin: 0 }, // keep it plain
      },
    },
  },
});

export default theme;
